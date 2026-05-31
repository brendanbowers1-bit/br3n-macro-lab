"""Load settlement lab data — bridges parent fx_regime_lab raw cache when local raw is empty."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.curated_bridge import (
    build_access_from_macro,
    build_documented_stress_events,
    build_finality_from_reference,
    build_liquidity_from_bis,
    build_liquidity_from_ecb,
    build_payment_flows_from_cpmi,
    build_payment_flows_from_rpw,
    estimate_cost_of_capital,
    merge_payment_flows,
)
from src.data.file_discovery import has_real_data
from src.data.mock_data import create_mock_dataset
from src.quality.lineage import attach_lineage, base_lineage, calculate_file_hash
from src.quality.data_quality import annotate_quality
from src.utils.paths import LAB_ROOT, RAW_DIR

PARENT_RAW = LAB_ROOT.parent / "data" / "raw"


def _load_csv_if_exists(path: Path, source_id: str, observed: bool = True) -> pd.DataFrame | None:
    if not path.exists():
        return None
    df = pd.read_csv(path)
    try:
        rel = str(path.relative_to(LAB_ROOT.parent))
    except ValueError:
        rel = path.name
    lg = base_lineage(
        source_id,
        raw_file_name=rel,
        raw_file_hash=calculate_file_hash(path),
        mock_data_flag=False,
        observed=observed,
    )
    return annotate_quality(attach_lineage(df, lg))


def _bridge(local: Path, parent: Path) -> Path:
    return local if local.exists() else parent


def parent_lab_has_data() -> bool:
    return any(
        p.exists()
        for p in (
            PARENT_RAW / "imf" / "fx_rates_from_lab.csv",
            PARENT_RAW / "fred" / "dxy_daily.csv",
            PARENT_RAW / "world_bank_rpw" / "rpw_historical_panel.csv",
            PARENT_RAW / "bis" / "fx_turnover_2022.csv",
            PARENT_RAW / "imf" / "macro_indicators_wb_api.csv",
        )
    )


def _load_or_empty(path: Path, source_id: str, observed: bool = True) -> pd.DataFrame:
    df = _load_csv_if_exists(path, source_id, observed=observed)
    return df if df is not None else pd.DataFrame()


def load_bis_cpmi_files() -> pd.DataFrame:
    for name in ("cpmi_payment_systems_curated.csv", "cpmi_payment_systems.csv"):
        p = RAW_DIR / "bis_cpmi" / name
        if p.exists():
            return _load_or_empty(p, "bis_cpmi")
    return pd.DataFrame()


def load_settlement_liquidity_curated() -> pd.DataFrame:
    p = RAW_DIR / "bis_cpmi" / "settlement_liquidity_curated.csv"
    return _load_or_empty(p, "bis_triennial_fx")


def load_world_bank_findex_files() -> pd.DataFrame:
    for name in ("findex_indicators_curated.csv", "findex_indicators.csv"):
        p = RAW_DIR / "world_bank" / name
        if p.exists():
            return _load_or_empty(p, "world_bank_findex")
    return pd.DataFrame()


def load_world_bank_rpw_files() -> pd.DataFrame:
    p = _bridge(RAW_DIR / "world_bank" / "rpw_corridors.csv", PARENT_RAW / "world_bank_rpw" / "rpw_historical_panel.csv")
    return _load_or_empty(p, "world_bank_rpw")


def load_imf_files() -> pd.DataFrame:
    p = _bridge(RAW_DIR / "imf" / "fx_rates.csv", PARENT_RAW / "imf" / "fx_rates_from_lab.csv")
    df = _load_csv_if_exists(p, "imf")
    if df is None or df.empty:
        return pd.DataFrame()
    if "volatility_30d" not in df.columns and "usd_fx_rate" in df.columns:
        df = df.sort_values("date")
        df["volatility_30d"] = (
            df.groupby("currency")["usd_fx_rate"].pct_change().rolling(30).std() * (252 ** 0.5)
        )
    return df


def load_imf_macro_files() -> pd.DataFrame:
    p = _bridge(RAW_DIR / "imf" / "macro_indicators.csv", PARENT_RAW / "imf" / "macro_indicators_wb_api.csv")
    return _load_or_empty(p, "imf")


def load_bis_triennial_files() -> pd.DataFrame:
    p = _bridge(RAW_DIR / "bis_cpmi" / "fx_turnover.csv", PARENT_RAW / "bis" / "fx_turnover_2022.csv")
    return _load_or_empty(p, "bis_triennial_fx")


def load_fred_files() -> pd.DataFrame:
    for name in ("sofr_curated.csv", "sofr.csv"):
        p = RAW_DIR / "fred" / name
        if p.exists():
            return _load_or_empty(p, "fred")
    p = _bridge(RAW_DIR / "fred" / "sofr.csv", PARENT_RAW / "fred" / "dxy_daily.csv")
    return _load_or_empty(p, "fred")


def load_ecb_target_files() -> pd.DataFrame:
    p = RAW_DIR / "ecb" / "target_statistics_curated.csv"
    return _load_or_empty(p, "ecb_payments")


def load_finality_reference_files() -> pd.DataFrame:
    p = RAW_DIR / "manual" / "finality_legal_reference.csv"
    if p.exists():
        return _load_or_empty(p, "manual_assumptions", observed=False)
    return build_finality_from_reference()


def load_stress_events_curated() -> pd.DataFrame:
    p = RAW_DIR / "bis_cpmi" / "documented_stress_events.csv"
    if p.exists():
        return _load_or_empty(p, "bis_cpmi")
    return build_documented_stress_events()


def load_manual_assumptions() -> pd.DataFrame:
    df = _load_csv_if_exists(RAW_DIR / "manual" / "settlement_assumptions.csv", "manual_assumptions", observed=False)
    if df is None or df.empty:
        return pd.DataFrame()
    df["manual_assumption_flag"] = True
    return df


def _build_fx_exposure_from_imf(imf: pd.DataFrame) -> pd.DataFrame:
    if imf.empty:
        return pd.DataFrame()
    rows = []
    lg = base_lineage("imf", mock_data_flag=False)
    for currency, grp in imf.groupby("currency"):
        g = grp.sort_values("date").tail(60)
        if g.empty:
            continue
        vol30 = float(g["volatility_30d"].dropna().iloc[-1]) if g["volatility_30d"].notna().any() else 0.12
        notional = 1e8
        rows.append({
            "date": str(g["date"].iloc[-1]),
            "currency_pair": f"USD/{currency}",
            "settlement_window_days": 2,
            "notional_value_usd": notional,
            "fx_volatility_30d": vol30,
            "expected_fx_exposure_usd": notional * vol30 * 0.1,
            **lg,
        })
    return annotate_quality(pd.DataFrame(rows))


def _resolve_cost_of_capital(fred: pd.DataFrame, macro: pd.DataFrame) -> float:
    if not fred.empty and "value_pct" in fred.columns:
        return float(fred["value_pct"].iloc[-1])
    if not fred.empty and "dxy_broad" in fred.columns:
        dxy = fred
    else:
        dxy = pd.DataFrame()
    return estimate_cost_of_capital(macro, dxy)


def _apply_cost_of_capital(df: pd.DataFrame, coc: float) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "cost_of_capital_pct" in out.columns:
        out["cost_of_capital_pct"] = coc
    return out


def load_all_tables(use_mock_fallback: bool = True) -> dict[str, pd.DataFrame]:
    bridged = parent_lab_has_data() or has_real_data()
    mock_ds: dict[str, pd.DataFrame] | None = None

    def _mock_fallback() -> dict[str, pd.DataFrame]:
        nonlocal mock_ds
        if mock_ds is None:
            mock_ds = create_mock_dataset()
        return mock_ds

    if not bridged:
        if use_mock_fallback:
            return create_mock_dataset()
        raise FileNotFoundError("No raw data and mock fallback disabled.")

    imf = load_imf_files()
    macro = load_imf_macro_files()
    bis = load_bis_triennial_files()
    rpw = load_world_bank_rpw_files()
    fred = load_fred_files()
    coc = _resolve_cost_of_capital(fred, macro)

    cpmi_local = load_bis_cpmi_files()
    if cpmi_local.empty:
        cpmi_flows = merge_payment_flows(build_payment_flows_from_cpmi(), build_payment_flows_from_rpw(rpw))
    else:
        cpmi_flows = cpmi_local

    liq_local = load_settlement_liquidity_curated()
    if liq_local.empty:
        liq_parts = [_apply_cost_of_capital(build_liquidity_from_bis(bis, coc), coc)]
        liq_ecb = _apply_cost_of_capital(build_liquidity_from_ecb(max(0.03, coc - 0.01)), coc)
        if not liq_ecb.empty:
            liq_parts.append(liq_ecb)
        liquidity = pd.concat([p for p in liq_parts if not p.empty], ignore_index=True)
    else:
        liquidity = _apply_cost_of_capital(liq_local, coc)

    findex_local = load_world_bank_findex_files()
    access = findex_local if not findex_local.empty else build_access_from_macro(macro)

    finality = load_finality_reference_files()
    fx_exp = _build_fx_exposure_from_imf(imf)
    stress = load_stress_events_curated()

    tables = {
        "payment_flow_observations": cpmi_flows if not cpmi_flows.empty else _mock_fallback()["payment_flow_observations"],
        "settlement_liquidity_table": liquidity if not liquidity.empty else _mock_fallback()["settlement_liquidity_table"],
        "fx_settlement_exposure": fx_exp if not fx_exp.empty else _mock_fallback()["fx_settlement_exposure"],
        "finality_characteristics": finality if not finality.empty else _mock_fallback()["finality_characteristics"],
        "payment_access_and_inclusion": access if not access.empty else _mock_fallback()["payment_access_and_inclusion"],
        "payment_network_stress_events": stress if not stress.empty else _mock_fallback()["payment_network_stress_events"],
    }

    for name, df in tables.items():
        if df.empty:
            continue
        if "mock_data_flag" not in df.columns:
            continue
        if not df["mock_data_flag"].all() and bridged:
            df["observed_vs_estimated_flag"] = df.apply(
                lambda r: "observed" if not r.get("mock_data_flag") else "estimated", axis=1
            )

    tables["_manual_assumptions"] = load_manual_assumptions()
    tables["_cost_of_capital"] = pd.DataFrame([{"cost_of_capital_pct": coc}])
    return tables

"""Load settlement lab data — bridges parent fx_regime_lab raw cache when local raw is empty."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

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
        )
    )


def load_bis_cpmi_files() -> pd.DataFrame:
    p = RAW_DIR / "bis_cpmi" / "cpmi_payment_systems.csv"
    if not p.exists():
        return pd.DataFrame()
    return _load_csv_if_exists(p, "bis_cpmi") or pd.DataFrame()


def load_world_bank_findex_files() -> pd.DataFrame:
    return _load_csv_if_exists(RAW_DIR / "world_bank" / "findex_indicators.csv", "world_bank_findex") or pd.DataFrame()


def load_world_bank_rpw_files() -> pd.DataFrame:
    p = _bridge(RAW_DIR / "world_bank" / "rpw_corridors.csv", PARENT_RAW / "world_bank_rpw" / "rpw_historical_panel.csv")
    return _load_csv_if_exists(p, "world_bank_rpw") or pd.DataFrame()


def load_imf_files() -> pd.DataFrame:
    p = _bridge(RAW_DIR / "imf" / "fx_rates.csv", PARENT_RAW / "imf" / "fx_rates_from_lab.csv")
    df = _load_csv_if_exists(p, "imf")
    if df.empty:
        return df
    if "volatility_30d" not in df.columns and "usd_fx_rate" in df.columns:
        df = df.sort_values("date")
        df["volatility_30d"] = (
            df.groupby("currency")["usd_fx_rate"].pct_change().rolling(30).std() * (252 ** 0.5)
        )
    return df


def load_fred_files() -> pd.DataFrame:
    p = _bridge(RAW_DIR / "fred" / "sofr.csv", PARENT_RAW / "fred" / "dxy_daily.csv")
    return _load_csv_if_exists(p, "fred") or pd.DataFrame()


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


def load_all_tables(use_mock_fallback: bool = True) -> dict[str, pd.DataFrame]:
    mock_ds = create_mock_dataset() if use_mock_fallback else None
    bridged = parent_lab_has_data() or has_real_data()

    if not bridged:
        if use_mock_fallback:
            return create_mock_dataset()
        raise FileNotFoundError("No raw data and mock fallback disabled.")

    imf = load_imf_files()
    fx_exp = _build_fx_exposure_from_imf(imf)
    cpmi = load_bis_cpmi_files()
    findex = load_world_bank_findex_files()

    tables = {
        "payment_flow_observations": cpmi if not cpmi.empty else mock_ds["payment_flow_observations"],
        "settlement_liquidity_table": mock_ds["settlement_liquidity_table"],
        "fx_settlement_exposure": fx_exp if not fx_exp.empty else mock_ds["fx_settlement_exposure"],
        "finality_characteristics": mock_ds["finality_characteristics"],
        "payment_access_and_inclusion": findex if not findex.empty else mock_ds["payment_access_and_inclusion"],
        "payment_network_stress_events": mock_ds["payment_network_stress_events"],
    }

    for name, df in tables.items():
        if not df.empty and not df["mock_data_flag"].all() and bridged:
            df["observed_vs_estimated_flag"] = df.apply(
                lambda r: "observed" if not r.get("mock_data_flag") else "estimated", axis=1
            )

    tables["_manual_assumptions"] = load_manual_assumptions()
    return tables

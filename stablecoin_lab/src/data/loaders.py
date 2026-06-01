"""Load stablecoin lab tables — raw CSV with selective mock fallback."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.curated_bridge import build_remittance_comparison_from_rpw
from src.data.file_discovery import has_real_data
from src.data.mock_data import create_mock_dataset
from src.quality.data_quality import annotate_quality
from src.quality.lineage import attach_lineage, base_lineage, calculate_file_hash
from src.utils.paths import LAB_ROOT, RAW_DIR

PARENT_RAW = LAB_ROOT.parent / "data" / "raw"

SUBDIR_SOURCE_MAP = {
    "stablecoin_supply": "defillama",
    "stablecoin_prices": "coingecko",
    "stablecoin_reserves": "circle_attestation",
    "chain_fees": "chain_data",
    "chain_finality": "chain_data",
    "exchange_liquidity": "exchange_liquidity",
    "defi_liquidity": "defillama",
    "remittance_costs": "world_bank_rpw",
    "fx_rates": "imf_macro",
    "macro": "imf_macro",
    "regulatory_events": "regulatory_events",
    "issuer_attestations": "circle_attestation",
    "manual": "manual_assumptions",
}


def _load_csv_if_exists(path: Path, source_id: str, observed: bool = True) -> pd.DataFrame | None:
    if not path.exists():
        return None
    df = pd.read_csv(path)
    try:
        rel = str(path.relative_to(LAB_ROOT))
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


def _first_csv(subdir: str) -> Path | None:
    folder = RAW_DIR / subdir
    if not folder.exists():
        return None
    files = sorted(folder.glob("*.csv"))
    return files[0] if files else None


def _load_subdir(subdir: str, source_id: str | None = None) -> pd.DataFrame:
    sid = source_id or SUBDIR_SOURCE_MAP.get(subdir, "manual_assumptions")
    path = _first_csv(subdir)
    if path is None:
        return pd.DataFrame()
    df = _load_csv_if_exists(path, sid)
    return df if df is not None else pd.DataFrame()


def load_stablecoin_supply_files() -> pd.DataFrame:
    return _load_subdir("stablecoin_supply", "defillama")


def load_stablecoin_price_files() -> pd.DataFrame:
    return _load_subdir("stablecoin_prices", "defillama")


def load_reserve_attestation_files() -> pd.DataFrame:
    usdc = _load_subdir("issuer_attestations")
    if not usdc.empty:
        return usdc
    return _load_subdir("stablecoin_reserves", "circle_attestation")


def load_chain_fee_files() -> pd.DataFrame:
    return _load_subdir("chain_fees", "chain_data")


def load_chain_finality_files() -> pd.DataFrame:
    finality = _load_subdir("chain_finality", "chain_data")
    if not finality.empty:
        return finality
    return load_chain_fee_files()


def load_off_ramp_files() -> pd.DataFrame:
    manual = RAW_DIR / "manual" / "off_ramp_assumptions.csv"
    if manual.exists():
        return _load_csv_if_exists(manual, "manual_assumptions", observed=False) or pd.DataFrame()
    return pd.DataFrame()


def load_remittance_comparison_files() -> pd.DataFrame:
    curated = _first_csv("remittance_costs")
    if curated is not None:
        df = _load_csv_if_exists(curated, "world_bank_rpw")
        if df is not None and not df.empty:
            if "stablecoin_onramp_fee_pct" in df.columns and df["stablecoin_onramp_fee_pct"].notna().any():
                return df
            if "traditional_fee_pct" in df.columns:
                return df
    parent = PARENT_RAW / "world_bank_rpw" / "rpw_historical_panel.csv"
    if parent.exists():
        rpw = pd.read_csv(parent)
        agg = rpw.groupby(["corridor", "sender_country", "receiver_country"], as_index=False).agg(
            traditional_fee_pct=("fee_pct", "mean"),
            traditional_fx_margin_pct=("fx_margin_pct", "mean"),
            traditional_transfer_speed_days=("transfer_speed_days", "mean"),
            date=("date", "max"),
        )
        agg["traditional_fee_pct"] = agg["traditional_fee_pct"] * 100
        agg["traditional_fx_margin_pct"] = agg["traditional_fx_margin_pct"] * 100
        return build_remittance_comparison_from_rpw(agg)
    return pd.DataFrame()


def load_redemption_files() -> pd.DataFrame:
    path = RAW_DIR / "manual" / "redemption_from_attestations.csv"
    if path.exists():
        df = _load_csv_if_exists(path, "circle_attestation")
        return df if df is not None else pd.DataFrame()
    return pd.DataFrame()


def load_regulatory_events_files() -> pd.DataFrame:
    return _load_subdir("regulatory_events", "regulatory_events")


def load_manual_assumptions() -> pd.DataFrame:
    paths = [
        RAW_DIR / "manual" / "stablecoin_assumptions.csv",
        RAW_DIR / "manual" / "fed_stablecoin_research.csv",
        RAW_DIR / "manual" / "bis_tokenization_references.csv",
    ]
    parts = []
    for path in paths:
        if path.exists():
            df = _load_csv_if_exists(path, "fed_research" if "fed" in path.name else "bis_innovation", observed=True)
            if df is not None and not df.empty:
                parts.append(df)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def _merge_chain_characteristics(fees: pd.DataFrame, finality: pd.DataFrame) -> pd.DataFrame:
    if fees.empty and finality.empty:
        return pd.DataFrame()
    if fees.empty:
        return finality
    if finality.empty:
        return fees
    keys = [c for c in ("date", "blockchain_network") if c in fees.columns and c in finality.columns]
    if not keys:
        return pd.concat([fees, finality], ignore_index=True)
    return fees.merge(finality, on=keys, how="outer", suffixes=("", "_dup"))


def load_all_tables(use_mock_fallback: bool = True) -> dict[str, pd.DataFrame]:
    if not has_real_data() and not use_mock_fallback:
        raise FileNotFoundError("No raw stablecoin data and mock fallback disabled.")

    mock_ds: dict[str, pd.DataFrame] | None = None

    def _mock(name: str) -> pd.DataFrame:
        nonlocal mock_ds
        if not use_mock_fallback:
            return pd.DataFrame()
        if mock_ds is None:
            mock_ds = create_mock_dataset()
        return mock_ds[name]

    supply = load_stablecoin_supply_files()
    peg = load_stablecoin_price_files()
    reserves = load_reserve_attestation_files()
    chain = _merge_chain_characteristics(load_chain_fee_files(), load_chain_finality_files())
    redemption = load_redemption_files()
    off_ramp = load_off_ramp_files()
    remittance = load_remittance_comparison_files()
    regulatory = load_regulatory_events_files()

    tables = {
        "stablecoin_supply": supply if not supply.empty else _mock("stablecoin_supply"),
        "stablecoin_price_peg": peg if not peg.empty else _mock("stablecoin_price_peg"),
        "stablecoin_reserves": reserves if not reserves.empty else _mock("stablecoin_reserves"),
        "blockchain_settlement_characteristics": chain if not chain.empty else _mock("blockchain_settlement_characteristics"),
        "stablecoin_redemption_characteristics": redemption if not redemption.empty else _mock("stablecoin_redemption_characteristics"),
        "off_ramp_characteristics": off_ramp if not off_ramp.empty else _mock("off_ramp_characteristics"),
        "remittance_comparison": remittance if not remittance.empty else _mock("remittance_comparison"),
        "regulatory_events": regulatory if not regulatory.empty else _mock("regulatory_events"),
    }

    tables["_manual_assumptions"] = load_manual_assumptions()
    return tables

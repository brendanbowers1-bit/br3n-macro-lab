"""Build processed settlement lab dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.cleaners import standardize_countries, standardize_currencies, standardize_dates
from src.data.loaders import load_all_tables, load_merchant_fee_panel, load_world_bank_rpw_files
from src.data.curated_bridge import validate_pfi_against_merchant_fees, validate_pfi_against_rpw
from src.features.build_features import build_all_features
from src.indices.finality_quality import calculate_finality_quality_table
from src.indices.operational_liquidity import calculate_operational_liquidity_table
from src.indices.settlement_drag import calculate_settlement_drag_table
from src.models.payment_friction_incidence import calculate_friction_incidence_table
from src.models.payment_network_fragility import calculate_fragility_table
from src.quality.validation import validate_all_tables
from src.utils.paths import FEATURES_DIR, OUTPUTS_DIR, PROCESSED_DIR


def _build_pfi_validation(pfi: pd.DataFrame, flows: pd.DataFrame, tables: dict) -> pd.DataFrame:
    parts = []
    rpw = load_world_bank_rpw_files()
    if not rpw.empty:
        rpw_val = validate_pfi_against_rpw(pfi, rpw)
        if not rpw_val.empty:
            rpw_val["validation_type"] = "rpw_corridor"
            parts.append(rpw_val)
    fees = tables.get("_merchant_fee_panel")
    if fees is None or (isinstance(fees, pd.DataFrame) and fees.empty):
        fees = load_merchant_fee_panel()
    if isinstance(fees, pd.DataFrame) and not fees.empty:
        merch_val = validate_pfi_against_merchant_fees(pfi, fees)
        if not merch_val.empty:
            merch_val["validation_type"] = "merchant_interchange"
            parts.append(merch_val)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def build_settlement_dataset(use_mock_fallback: bool = True) -> dict[str, pd.DataFrame]:
    tables = load_all_tables(use_mock_fallback=use_mock_fallback)
    flows = tables["payment_flow_observations"]
    mock = bool(flows["mock_data_flag"].all()) if not flows.empty else True
    mixed = bool(flows["mock_data_flag"].any() and not mock) if not flows.empty else False

    for name in list(tables.keys()):
        if isinstance(tables[name], pd.DataFrame) and "date" in tables[name].columns:
            tables[name] = standardize_dates(tables[name])
            tables[name] = standardize_countries(tables[name])
            tables[name] = standardize_currencies(tables[name])

    features = build_all_features(tables)
    sdi = calculate_settlement_drag_table(
        tables["payment_flow_observations"],
        tables.get("fx_settlement_exposure", pd.DataFrame()),
    )
    olb = calculate_operational_liquidity_table(tables.get("settlement_liquidity_table", pd.DataFrame()))
    fqi = calculate_finality_quality_table(tables.get("finality_characteristics", pd.DataFrame()))
    pnf = calculate_fragility_table(
        tables["payment_flow_observations"],
        tables.get("settlement_liquidity_table", pd.DataFrame()),
        tables.get("payment_network_stress_events", pd.DataFrame()),
        tables.get("fx_settlement_exposure", pd.DataFrame()),
    )
    pfi = calculate_friction_incidence_table(
        tables["payment_flow_observations"],
        sdi,
        olb,
    )

    out = {
        **tables,
        "features": features,
        "settlement_drag_outputs": sdi,
        "operational_liquidity_outputs": olb,
        "finality_quality_outputs": fqi,
        "payment_fragility_outputs": pnf,
        "friction_incidence_outputs": pfi,
        "_mock_data_flag": pd.DataFrame([{"mock_data_flag": mock, "mixed_mode": mixed}]),
        "_pfi_validation": _build_pfi_validation(pfi, tables.get("payment_flow_observations", pd.DataFrame()), tables),
    }
    out["_validation"] = validate_all_tables(out)
    return out


def save_processed(dataset: dict[str, pd.DataFrame], out_dir: Path | None = None) -> dict[str, Path]:
    out_dir = out_dir or PROCESSED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, df in dataset.items():
        if name.startswith("_") or not isinstance(df, pd.DataFrame):
            continue
        p = out_dir / f"{name}.csv"
        df.to_csv(p, index=False)
        paths[name] = p
    return paths


def save_outputs(dataset: dict[str, pd.DataFrame]) -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    for key in (
        "settlement_drag_outputs", "operational_liquidity_outputs",
        "finality_quality_outputs", "payment_fragility_outputs",
        "friction_incidence_outputs", "features",
    ):
        if key in dataset:
            dataset[key].to_csv(OUTPUTS_DIR / f"{key}.csv", index=False)

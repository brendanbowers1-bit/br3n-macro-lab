"""Build processed stablecoin lab dataset with indices and models."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION
from src.data.cleaners import (
    standardize_dates,
    standardize_network_names,
    standardize_stablecoin_names,
)
from src.data.loaders import load_all_tables
from src.features.build_features import build_all_features
from src.indices.compliance_settlement_drag import calculate_compliance_drag_table
from src.indices.stablecoin_dollarization import calculate_stablecoin_dollarization_table
from src.indices.stablecoin_finality_quality import calculate_stablecoin_finality_quality_table
from src.indices.stablecoin_value_survival import calculate_stablecoin_vsi_table
from src.indices.tokenized_money_singleness import calculate_singleness_table
from src.models.digital_run_velocity import calculate_digital_run_velocity_table
from src.models.settlement_window_compression import calculate_settlement_window_compression_table
from src.models.stablecoin_liquidity_transformation import calculate_liquidity_transformation_table
from src.quality.validation import validate_all_tables
from src.utils.paths import FEATURES_DIR, METADATA_DIR, OUTPUTS_DIR, PROCESSED_DIR

CANONICAL_TABLE_NAMES = (
    "stablecoin_supply",
    "stablecoin_price_peg",
    "stablecoin_reserves",
    "blockchain_settlement_characteristics",
    "stablecoin_redemption_characteristics",
    "off_ramp_characteristics",
    "remittance_comparison",
    "regulatory_events",
)

OUTPUT_KEYS = (
    "features",
    "stablecoin_finality_quality_outputs",
    "settlement_window_compression_outputs",
    "liquidity_transformation_outputs",
    "digital_run_velocity_outputs",
    "stablecoin_dollarization_outputs",
    "tokenized_money_singleness_outputs",
    "compliance_settlement_drag_outputs",
    "stablecoin_value_survival_outputs",
)


def build_stablecoin_dataset(use_mock_fallback: bool = True) -> dict[str, pd.DataFrame]:
    tables = load_all_tables(use_mock_fallback=use_mock_fallback)

    supply = tables.get("stablecoin_supply", pd.DataFrame())
    mock = bool(supply["mock_data_flag"].all()) if not supply.empty and "mock_data_flag" in supply.columns else True
    mixed = False
    if not supply.empty and "mock_data_flag" in supply.columns:
        mixed = bool(supply["mock_data_flag"].any() and not mock)

    for name in CANONICAL_TABLE_NAMES:
        if name not in tables or not isinstance(tables[name], pd.DataFrame):
            continue
        df = tables[name]
        if df.empty:
            continue
        df = standardize_dates(df)
        df = standardize_stablecoin_names(df)
        df = standardize_network_names(df)
        if "methodology_version" not in df.columns:
            df["methodology_version"] = METHODOLOGY_VERSION
        tables[name] = df

    features = build_all_features(tables)
    macro = features.copy()
    if "receiver_country" in macro.columns and "country" not in macro.columns:
        macro["country"] = macro["receiver_country"]

    sfqi = calculate_stablecoin_finality_quality_table(
        tables.get("blockchain_settlement_characteristics", pd.DataFrame()),
        tables.get("stablecoin_reserves"),
        tables.get("stablecoin_redemption_characteristics"),
        tables.get("off_ramp_characteristics"),
        tables.get("stablecoin_price_peg"),
    )
    swc = calculate_settlement_window_compression_table(
        tables.get("remittance_comparison", pd.DataFrame()),
        tables.get("blockchain_settlement_characteristics"),
        tables.get("off_ramp_characteristics"),
    )
    slt = calculate_liquidity_transformation_table(
        tables.get("stablecoin_supply", pd.DataFrame()),
        tables.get("stablecoin_reserves"),
        tables.get("stablecoin_redemption_characteristics"),
    )
    drv = calculate_digital_run_velocity_table(
        tables.get("stablecoin_supply", pd.DataFrame()),
        tables.get("stablecoin_redemption_characteristics"),
        tables.get("stablecoin_price_peg"),
    )
    sdi = calculate_stablecoin_dollarization_table(
        macro,
        tables.get("stablecoin_supply"),
        tables.get("remittance_comparison"),
    )
    sing = calculate_singleness_table(
        tables.get("stablecoin_price_peg", pd.DataFrame()),
        tables.get("stablecoin_reserves"),
        tables.get("stablecoin_redemption_characteristics"),
    )
    csd = calculate_compliance_drag_table(
        tables.get("off_ramp_characteristics", pd.DataFrame()),
        tables.get("blockchain_settlement_characteristics"),
        tables.get("stablecoin_redemption_characteristics"),
    )
    svsi = calculate_stablecoin_vsi_table(tables.get("remittance_comparison", pd.DataFrame()))

    out = {
        **{k: tables[k] for k in CANONICAL_TABLE_NAMES if k in tables},
        "features": features,
        "stablecoin_finality_quality_outputs": sfqi,
        "settlement_window_compression_outputs": swc,
        "liquidity_transformation_outputs": slt,
        "digital_run_velocity_outputs": drv,
        "stablecoin_dollarization_outputs": sdi,
        "tokenized_money_singleness_outputs": sing,
        "compliance_settlement_drag_outputs": csd,
        "stablecoin_value_survival_outputs": svsi,
        "_mock_data_flag": pd.DataFrame([{
            "mock_data_flag": mock,
            "mixed_mode": mixed,
            "methodology_version": METHODOLOGY_VERSION,
            "limitations": LAB_LIMITATIONS,
        }]),
        "_manual_assumptions": tables.get("_manual_assumptions", pd.DataFrame()),
    }
    out["_validation"] = validate_all_tables({k: v for k, v in out.items() if not k.startswith("_")})
    return out


def save_processed(dataset: dict[str, pd.DataFrame], out_dir: Path | None = None) -> dict[str, Path]:
    out_dir = out_dir or PROCESSED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for name in CANONICAL_TABLE_NAMES:
        df = dataset.get(name)
        if not isinstance(df, pd.DataFrame) or df.empty:
            continue
        p = out_dir / f"{name}.csv"
        df.to_csv(p, index=False)
        paths[name] = p
    if "_validation" in dataset:
        vpath = METADATA_DIR / "validation_summary.csv"
        METADATA_DIR.mkdir(parents=True, exist_ok=True)
        dataset["_validation"].to_csv(vpath, index=False)
        paths["_validation"] = vpath
    return paths


def save_outputs(dataset: dict[str, pd.DataFrame]) -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    for key in OUTPUT_KEYS:
        if key in dataset and isinstance(dataset[key], pd.DataFrame) and not dataset[key].empty:
            dataset[key].to_csv(OUTPUTS_DIR / f"{key}.csv", index=False)
    if "_mock_data_flag" in dataset:
        dataset["_mock_data_flag"].to_csv(OUTPUTS_DIR / "provenance_summary.csv", index=False)
    if "_validation" in dataset:
        dataset["_validation"].to_csv(OUTPUTS_DIR / "validation_summary.csv", index=False)

"""Sensitivity analysis for settlement lab models."""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import SENSITIVITY_CASES
from src.data.build_dataset import build_settlement_dataset


def run_sensitivity_analysis() -> pd.DataFrame:
    from src.indices.settlement_drag import calculate_settlement_drag_table
    from src.indices.operational_liquidity import calculate_operational_liquidity_table
    from src.models.payment_friction_incidence import calculate_friction_incidence_table
    from src.data.loaders import load_all_tables

    tables = load_all_tables()
    olb_raw = calculate_operational_liquidity_table(tables.get("settlement_liquidity_table", pd.DataFrame()))
    frames = []
    for case in SENSITIVITY_CASES:
        sdi = calculate_settlement_drag_table(
            tables["payment_flow_observations"],
            tables.get("fx_settlement_exposure"),
            sensitivity_case=case,
        )
        sdi["sensitivity_case"] = case
        pfi = calculate_friction_incidence_table(
            tables["payment_flow_observations"], sdi, olb_raw, sensitivity_case=case,
        )
        pfi["sensitivity_case"] = case
        frames.append(sdi)
        frames.append(pfi.assign(model_name="PFI"))
    return pd.concat(frames, ignore_index=True)


def sensitivity_summary(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty or "settlement_drag_index" not in results.columns:
        return pd.DataFrame()
    sub = results[results["settlement_drag_index"].notna()]
    return (
        sub.groupby("entity", as_index=False)
        .agg(
            sdi_min=("settlement_drag_index", "min"),
            sdi_max=("settlement_drag_index", "max"),
            sdi_mean=("settlement_drag_index", "mean"),
        )
        .assign(sdi_range=lambda d: d["sdi_max"] - d["sdi_min"])
        .sort_values("sdi_mean")
    )

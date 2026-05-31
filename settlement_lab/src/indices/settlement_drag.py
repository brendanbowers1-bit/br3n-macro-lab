"""
Settlement Drag Index (SDI) — economic cost of delayed settlement.

Research-only. Not financial advice. Not operational payment guidance.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import (
    COST_OF_CAPITAL,
    LAB_LIMITATIONS,
    METHODOLOGY_VERSION,
    OPERATIONAL_COST_PER_100,
    FX_EXPOSURE_WEIGHT,
    FAILURE_RATE_WEIGHT,
)

SDI_LIMITATIONS = (
    "SDI estimates settlement drag under stated cost-of-capital and lag assumptions. "
    + LAB_LIMITATIONS
)


def _daily_cost(annual_pct: float) -> float:
    return annual_pct / 365.0


def calculate_settlement_drag_row(
    row: pd.Series,
    fx_exposure_usd: float = 0.0,
    sensitivity_case: str = "baseline",
    spec: str = "risk_adjusted",
) -> dict:
    value = float(row.get("transaction_value_usd", row.get("value_in_transit_usd", 0)) or 0)
    lag = float(row.get("settlement_lag_days", 1) or 1)
    coc = float(row.get("cost_of_capital_pct", COST_OF_CAPITAL[sensitivity_case]))
    fail_rate = float(row.get("failure_rate", 0.001) or 0)

    capital_cost = value * lag * _daily_cost(coc)
    fx_w = FX_EXPOSURE_WEIGHT[sensitivity_case]
    fx_cost = fx_exposure_usd * fx_w if spec != "core" else 0.0
    fail_w = FAILURE_RATE_WEIGHT[sensitivity_case]
    failure_cost = value * fail_rate * fail_w if spec != "core" else 0.0
    op_cost = value * OPERATIONAL_COST_PER_100[sensitivity_case] / 100 if spec == "extended" else 0.0

    total = capital_cost + fx_cost + failure_cost + op_cost
    per_100 = (total / value * 100) if value > 0 else 0.0
    sdi = 100 - min(100, per_100)

    if sdi >= 95:
        interp = "Low settlement drag (estimated)"
    elif sdi >= 85:
        interp = "Moderate settlement drag (estimated)"
    elif sdi >= 70:
        interp = "High settlement drag (estimated)"
    else:
        interp = "Severe settlement drag (estimated)"

    return {
        "settlement_drag_cost_usd": total,
        "settlement_drag_cost_per_100": per_100,
        "settlement_drag_index": sdi,
        "sdi_core": 100 - min(100, (capital_cost / value * 100) if value else 0),
        "sdi_risk_adjusted": 100 - min(100, ((capital_cost + fx_cost + failure_cost) / value * 100) if value else 0),
        "sdi_extended": sdi,
        "capital_cost_usd": capital_cost,
        "fx_exposure_cost_usd": fx_cost,
        "failure_cost_usd": failure_cost,
        "operational_cost_usd": op_cost,
        "interpretation": interp,
        "sensitivity_case": sensitivity_case,
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": SDI_LIMITATIONS,
        "data_quality_score": row.get("data_quality_score"),
        "data_quality_grade": row.get("data_quality_grade"),
        "mock_data_flag": row.get("mock_data_flag", False),
        "source_id": row.get("source_id"),
    }


def calculate_settlement_drag_table(
    flows: pd.DataFrame,
    fx_exposure: pd.DataFrame | None = None,
    sensitivity_case: str = "baseline",
) -> pd.DataFrame:
    if flows.empty:
        return pd.DataFrame()

    fx_map = {}
    if fx_exposure is not None and not fx_exposure.empty:
        fx_map = fx_exposure.groupby("currency_pair")["expected_fx_exposure_usd"].mean().to_dict()

    agg_cols = {
        "transaction_value_usd": "mean",
        "settlement_lag_days": "mean",
        "failure_rate": "mean",
        "data_quality_score": "mean",
        "data_quality_grade": "first",
        "mock_data_flag": "first",
        "source_id": "first",
    }
    use = {k: v for k, v in agg_cols.items() if k in flows.columns}
    agg = flows.groupby(["country", "payment_system", "rail_type"], as_index=False).agg(use)

    rows = []
    for _, row in agg.iterrows():
        fx_exp = sum(fx_map.values()) / max(len(fx_map), 1) if fx_map else row["transaction_value_usd"] * 0.01
        core = calculate_settlement_drag_row(row, fx_exp, sensitivity_case, spec="core")
        risk = calculate_settlement_drag_row(row, fx_exp, sensitivity_case, spec="risk_adjusted")
        ext = calculate_settlement_drag_row(row, fx_exp, sensitivity_case, spec="extended")
        merged = {**core, **{f"{k}_risk": v for k, v in risk.items() if k.startswith("sdi")}, "sdi_extended": ext["sdi_extended"]}
        merged["entity"] = f"{row['country']} | {row['payment_system']}"
        merged["entity_type"] = "rail"
        merged["country"] = row["country"]
        merged["payment_system"] = row["payment_system"]
        merged["rail_type"] = row["rail_type"]
        rows.append(merged)
    return pd.DataFrame(rows)

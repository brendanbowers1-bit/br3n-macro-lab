"""
Finality Quality Index (FQI) — proximity to final usable value.

Distinguishes authorization, clearing, settlement, availability, legal finality.
Research-only.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION

FQI_WEIGHTS = {
    "legal_finality_score": 0.20,
    "funds_availability_score": 0.20,
    "settlement_speed_score": 0.15,
    "operational_finality_score": 0.15,
    "reconciliation_quality_score": 0.10,
    "low_failure_risk_score": 0.10,
    "low_reversibility_risk_score": 0.10,
}

FQI_LIMITATIONS = (
    "FQI combines legal, operational, and availability dimensions. "
    "Some components may rely on manual assumptions. " + LAB_LIMITATIONS
)


def _speed_score(lag_hours: float) -> float:
    return max(0, min(100, 100 - lag_hours / 24 * 5))


def calculate_finality_quality_row(row: pd.Series) -> dict:
    legal = float(row.get("legal_finality_score", 50) or 50)
    operational = float(row.get("operational_finality_score", 50) or 50)
    funds = float(row.get("funds_availability_score", 50) or 50)
    rev_risk = float(row.get("reversibility_risk_score", 30) or 30)
    recon = float(row.get("reconciliation_quality_score", 50) or 50)
    fail_risk = float(row.get("settlement_failure_risk_score", 20) or 20)
    lag = float(row.get("finality_lag_hours", 24) or 24)

    components = {
        "legal_finality_score": legal,
        "funds_availability_score": funds,
        "settlement_speed_score": _speed_score(lag),
        "operational_finality_score": operational,
        "reconciliation_quality_score": recon,
        "low_failure_risk_score": max(0, 100 - fail_risk),
        "low_reversibility_risk_score": max(0, 100 - rev_risk),
    }
    fqi = sum(components[k] * FQI_WEIGHTS[k] for k in FQI_WEIGHTS)

    if fqi >= 85:
        interp = "High finality quality (estimated)"
    elif fqi >= 70:
        interp = "Usable but delayed (estimated)"
    elif fqi >= 55:
        interp = "Uncertain finality (estimated)"
    else:
        interp = "Fragile finality (estimated)"

    return {
        "finality_quality_index": fqi,
        **components,
        "interpretation": interp,
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": FQI_LIMITATIONS,
        "manual_assumption_flag": row.get("manual_assumption_flag", False),
        "data_quality_score": row.get("data_quality_score"),
        "mock_data_flag": row.get("mock_data_flag", False),
    }


def calculate_finality_quality_table(finality: pd.DataFrame) -> pd.DataFrame:
    if finality.empty:
        return pd.DataFrame()
    rows = []
    for _, row in finality.iterrows():
        calc = calculate_finality_quality_row(row)
        calc["entity"] = f"{row.get('country', '')} | {row.get('payment_system', '')}"
        calc["entity_type"] = "rail"
        calc["country"] = row.get("country")
        calc["rail_type"] = row.get("rail_type")
        rows.append({**row.to_dict(), **calc})
    return pd.DataFrame(rows)

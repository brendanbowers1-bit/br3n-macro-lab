"""
Compliance Settlement Drag Index — compliance as the real settlement window.

Research-only. Not investment advice.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import (
    COMPLIANCE_DELAY_HOURS,
    LAB_LIMITATIONS,
    METHODOLOGY_VERSION,
    OFF_RAMP_TIME_HOURS,
    REDEMPTION_TIME_HOURS,
)

CSD_LIMITATIONS = (
    "Compliance drag measures institutional delay beyond ledger confirmation. "
    "Effective finality hours use stated compliance, off-ramp, and redemption assumptions. "
    + LAB_LIMITATIONS
)


def _clamp(score: float) -> float:
    return max(0.0, min(100.0, float(score)))


def calculate_compliance_drag_row(
    row: pd.Series,
    sensitivity_case: str = "baseline",
) -> dict:
    ledger_secs = float(
        row.get("average_confirmation_time_seconds", row.get("ledger_finality_seconds", 12)) or 12
    )
    compliance_hours = float(
        row.get("compliance_delay_hours", COMPLIANCE_DELAY_HOURS[sensitivity_case]) or COMPLIANCE_DELAY_HOURS[sensitivity_case]
    )
    off_ramp_hours = float(
        row.get("estimated_off_ramp_time_hours", OFF_RAMP_TIME_HOURS[sensitivity_case])
        or OFF_RAMP_TIME_HOURS[sensitivity_case]
    )
    redemption_hours = float(
        row.get("estimated_redemption_time_hours", REDEMPTION_TIME_HOURS[sensitivity_case])
        or REDEMPTION_TIME_HOURS[sensitivity_case]
    )
    legal_hours = float(row.get("legal_finality_hours", 0) or 0)

    ledger_hours = ledger_secs / 3600
    compliance_drag_hours = compliance_hours + off_ramp_hours + redemption_hours + legal_hours
    effective_hours = ledger_hours + compliance_drag_hours

    drag_ratio = compliance_drag_hours / max(effective_hours, 0.001)
    index = _clamp(100 - min(100, drag_ratio * 100 + compliance_drag_hours * 2))

    if index >= 85:
        interp = "Low compliance drag (estimated)"
    elif index >= 70:
        interp = "Moderate drag (estimated)"
    elif index >= 50:
        interp = "High drag (estimated)"
    else:
        interp = "Compliance dominates settlement (estimated)"

    return {
        "ledger_finality_seconds": ledger_secs,
        "ledger_finality_hours": ledger_hours,
        "compliance_drag_hours": compliance_drag_hours,
        "effective_economic_finality_hours": effective_hours,
        "compliance_drag_index": index,
        "compliance_delay_hours": compliance_hours,
        "off_ramp_time_hours": off_ramp_hours,
        "redemption_time_hours": redemption_hours,
        "legal_finality_hours": legal_hours,
        "ledger_vs_effective_gap_hours": compliance_drag_hours,
        "interpretation": interp,
        "sensitivity_case": sensitivity_case,
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": CSD_LIMITATIONS,
        "data_quality_score": row.get("data_quality_score"),
        "mock_data_flag": row.get("mock_data_flag", False),
    }


def calculate_compliance_drag_table(
    off_ramp: pd.DataFrame,
    chain: pd.DataFrame | None = None,
    redemption: pd.DataFrame | None = None,
    sensitivity_case: str = "baseline",
) -> pd.DataFrame:
    if off_ramp.empty:
        return pd.DataFrame()

    chain_map = {}
    if chain is not None and not chain.empty:
        chain_map = chain.groupby("blockchain_network")["average_confirmation_time_seconds"].mean().to_dict()

    redemption_map = {}
    if redemption is not None and not redemption.empty:
        redemption_map = redemption.groupby("stablecoin")["estimated_redemption_time_hours"].mean().to_dict()

    rows = []
    for _, row in off_ramp.iterrows():
        merged = row.to_dict()
        network = row.get("blockchain_network", "Ethereum")
        stablecoin = row.get("stablecoin", "USDC")
        if network in chain_map:
            merged["average_confirmation_time_seconds"] = chain_map[network]
        if stablecoin in redemption_map:
            merged["estimated_redemption_time_hours"] = redemption_map[stablecoin]
        calc = calculate_compliance_drag_row(pd.Series(merged), sensitivity_case)
        calc["entity"] = f"{row.get('corridor', stablecoin)} | {stablecoin}"
        calc["entity_type"] = "corridor"
        calc["corridor"] = row.get("corridor")
        calc["stablecoin"] = stablecoin
        calc["country"] = row.get("country")
        rows.append({**merged, **calc})
    return pd.DataFrame(rows)

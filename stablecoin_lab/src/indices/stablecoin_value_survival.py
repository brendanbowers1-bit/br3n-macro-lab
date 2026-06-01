"""
Stablecoin Value Survival Index — usable local purchasing power on stablecoin rails.

Extends Bowers Frontier VSI logic to stablecoin remittance corridors.
Research-only. Not investment advice.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import (
    DEPEG_RISK_PENALTY_BPS,
    LAB_LIMITATIONS,
    METHODOLOGY_VERSION,
)

SVSI_LIMITATIONS = (
    "Stablecoin VSI estimates value survival under stated fee, spread, and delay assumptions. "
    "Does not assume stablecoins are cheaper than traditional rails. "
    + LAB_LIMITATIONS
)


def _clamp(score: float) -> float:
    return max(0.0, min(100.0, float(score)))


def _pct(val: float) -> float:
    return max(float(val or 0), 0.0)


def calculate_stablecoin_vsi_row(
    row: pd.Series,
    sensitivity_case: str = "baseline",
) -> dict:
    onramp = _pct(row.get("stablecoin_onramp_fee_pct", 0.015))
    spread = _pct(row.get("stablecoin_fx_spread_pct", row.get("stablecoin_spread_pct", 0.002)))
    chain = _pct(row.get("stablecoin_chain_fee_pct", 0.001))
    bridge = _pct(row.get("bridge_fee_pct", 0))
    offramp = _pct(row.get("stablecoin_offramp_fee_pct", 0.01))
    local_fx = _pct(row.get("local_fx_spread_pct", 0.005))
    depeg_bps = DEPEG_RISK_PENALTY_BPS[sensitivity_case]
    depeg = depeg_bps / 10000
    compliance_hours = float(row.get("compliance_delay_hours", row.get("stablecoin_effective_finality_hours", 4)) or 4)
    if "stablecoin_effective_finality_hours" in row and pd.notna(row.get("stablecoin_effective_finality_hours")):
        compliance_hours = float(row["stablecoin_effective_finality_hours"])
    compliance_cost = min(compliance_hours / 24 * 0.005, 0.02)
    redemption = _pct(row.get("redemption_friction_pct", 0.002))
    inflation = _pct(row.get("local_inflation_yoy", 0.04))
    hold_days = compliance_hours / 24
    inflation_loss = min(inflation * hold_days / 365, 0.03)

    components = {
        "onramp_fee_loss_pct": onramp,
        "stablecoin_spread_loss_pct": spread,
        "chain_fee_loss_pct": chain,
        "bridge_fee_loss_pct": bridge,
        "offramp_fee_loss_pct": offramp,
        "local_fx_spread_loss_pct": local_fx,
        "compliance_delay_cost_pct": compliance_cost,
        "redemption_friction_loss_pct": redemption,
        "depeg_risk_penalty_pct": depeg,
        "inflation_erosion_pct": inflation_loss,
    }
    total_loss = min(sum(components.values()), 0.50)
    stablecoin_vsi = _clamp(100 * (1 - total_loss))

    trad_fee = _pct(row.get("traditional_fee_pct", 0.05))
    trad_fx = _pct(row.get("traditional_fx_margin_pct", 0.03))
    trad_days = float(row.get("traditional_transfer_speed_days", 2) or 2)
    trad_timing = min(trad_days * 0.003, 0.02)
    trad_loss = min(trad_fee + trad_fx + trad_timing, 0.50)
    traditional_vsi = _clamp(100 * (1 - trad_loss))

    advantage = _clamp(stablecoin_vsi - traditional_vsi + 50)
    value_delta = (stablecoin_vsi - traditional_vsi)

    if stablecoin_vsi >= 95:
        interp = "High stablecoin value survival (estimated)"
    elif stablecoin_vsi >= traditional_vsi:
        interp = "Stablecoin rail competitive with traditional (estimated)"
    elif stablecoin_vsi >= 80:
        interp = "Moderate stablecoin value leakage (estimated)"
    else:
        interp = "Stablecoin rail underperforms traditional on costs (estimated)"

    return {
        "stablecoin_vsi": stablecoin_vsi,
        "traditional_vsi": traditional_vsi,
        "stablecoin_advantage_score": advantage,
        "value_saved_or_lost_per_100": value_delta,
        "total_stablecoin_loss_pct": total_loss,
        "total_traditional_loss_pct": trad_loss,
        "real_usable_value_delivered_pct": 1 - total_loss,
        **components,
        "interpretation": interp,
        "sensitivity_case": sensitivity_case,
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": SVSI_LIMITATIONS,
        "data_quality_score": row.get("data_quality_score"),
        "mock_data_flag": row.get("mock_data_flag", False),
    }


def calculate_stablecoin_vsi_table(
    remittance: pd.DataFrame,
    sensitivity_case: str = "baseline",
) -> pd.DataFrame:
    if remittance.empty:
        return pd.DataFrame()

    rows = []
    for _, row in remittance.iterrows():
        calc = calculate_stablecoin_vsi_row(row, sensitivity_case)
        calc["entity"] = row.get("corridor", f"{row.get('sender_country')}→{row.get('receiver_country')}")
        calc["entity_type"] = "corridor"
        calc["corridor"] = row.get("corridor")
        calc["stablecoin"] = row.get("stablecoin", "USDC")
        calc["sender_country"] = row.get("sender_country")
        calc["receiver_country"] = row.get("receiver_country")
        rows.append({**row.to_dict(), **calc})
    return pd.DataFrame(rows)

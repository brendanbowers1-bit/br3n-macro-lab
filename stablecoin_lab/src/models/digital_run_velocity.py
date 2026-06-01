"""
Digital Run Velocity Model — run propagation conditions, not run prediction.

Research-only. Not investment advice. Does not predict runs.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION

DRV_LIMITATIONS = (
    "Digital run velocity is a risk-conditions composite, not a run forecast. "
    "Does not predict redemption timing, magnitude, or probability. "
    + LAB_LIMITATIONS
)


def _clamp(score: float) -> float:
    return max(0.0, min(100.0, float(score)))


def _run_regime(score: float) -> str:
    if score < 35:
        return "low"
    if score < 55:
        return "elevated"
    if score < 75:
        return "high"
    return "extreme"


def calculate_digital_run_velocity_row(row: pd.Series) -> dict:
    transferability = float(row.get("24_7_transferability_score", row.get("transferability_score", 90)) or 90)
    exchange_liq = float(row.get("exchange_liquidity_score", 60) or 60)
    redemption_access = float(row.get("redemption_access_score", 55) or 55)
    info_speed = float(row.get("social_media_information_speed_proxy", 70) or 70)
    market_depth = float(row.get("market_depth_score", 55) or 55)
    composability = float(row.get("smart_contract_composability_score", 50) or 50)
    redemption_gates = 1.0 if row.get("redemption_gate_flag") else 0.0
    banking_hours = 1.0 if row.get("banking_hours_dependency_flag") else 0.0
    regulatory = float(row.get("regulatory_intervention_risk", 30) or 30)

    score = 0.0
    drivers = []

    score += transferability * 0.20
    if transferability > 80:
        drivers.append("always_on_transferability")

    score += (100 - exchange_liq) * 0.15
    if exchange_liq < 50:
        drivers.append("thin_exchange_liquidity")

    score += (100 - redemption_access) * 0.15
    if redemption_access < 45:
        drivers.append("limited_redemption_access")

    score += info_speed * 0.10
    if info_speed > 65:
        drivers.append("fast_information_propagation")

    score += (100 - market_depth) * 0.10
    score += composability * 0.10
    if composability > 60:
        drivers.append("defi_composability")

    if redemption_gates:
        score -= 15
        drivers.append("redemption_gates_present")
    if banking_hours:
        score -= 8
        drivers.append("banking_hours_dependency")
    score += regulatory * 0.10

    digital_run_velocity_score = _clamp(score)
    regime = _run_regime(digital_run_velocity_score)

    sensitivity_low = _clamp(digital_run_velocity_score - 10)
    sensitivity_high = _clamp(digital_run_velocity_score + 10)

    return {
        "digital_run_velocity_score": digital_run_velocity_score,
        "run_regime": regime,
        "sensitivity_score_low": sensitivity_low,
        "sensitivity_score_high": sensitivity_high,
        "top_drivers": "; ".join(drivers) or "none",
        "interpretation": f"Run-velocity conditions {regime} — not a run prediction (estimated)",
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": DRV_LIMITATIONS,
        "data_quality_score": row.get("data_quality_score"),
        "mock_data_flag": row.get("mock_data_flag", False),
    }


def calculate_digital_run_velocity_table(
    supply: pd.DataFrame,
    redemption: pd.DataFrame | None = None,
    peg: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if supply.empty:
        return pd.DataFrame()

    redemption_map = {}
    if redemption is not None and not redemption.empty:
        redemption_map = redemption.groupby("stablecoin").agg(
            redemption_gate_flag=("redemption_gate_flag", "max"),
            banking_hours_dependency_flag=("banking_hours_dependency_flag", "max"),
            estimated_redemption_time_hours=("estimated_redemption_time_hours", "mean"),
        ).to_dict("index")

    peg_map = {}
    if peg is not None and not peg.empty and "stablecoin" in peg.columns:
        peg_cols = {"peg_deviation_bps": ("peg_deviation_bps", "mean")}
        if "depeg_event_flag" in peg.columns:
            peg_cols["depeg_event_flag"] = ("depeg_event_flag", "max")
        peg_map = peg.groupby("stablecoin").agg(**peg_cols).to_dict("index")

    rows = []
    agg = supply.groupby("stablecoin", as_index=False).agg(
        supply_usd=("supply_usd", "sum"),
        data_quality_score=("data_quality_score", "mean"),
        data_quality_grade=("data_quality_grade", "first"),
        mock_data_flag=("mock_data_flag", "first"),
        source_id=("source_id", "first"),
    )
    for _, row in agg.iterrows():
        stablecoin = row["stablecoin"]
        merged = row.to_dict()
        merged["exchange_liquidity_score"] = max(30, 80 - merged["supply_usd"] / 1e10)
        merged["redemption_access_score"] = 70
        if stablecoin in redemption_map:
            merged.update(redemption_map[stablecoin])
            merged["redemption_access_score"] = _clamp(
                90 - redemption_map[stablecoin].get("estimated_redemption_time_hours", 24)
            )
        if stablecoin in peg_map and peg_map[stablecoin].get("depeg_event_flag"):
            merged["regulatory_intervention_risk"] = 50
        calc = calculate_digital_run_velocity_row(pd.Series(merged))
        calc["entity"] = stablecoin
        calc["entity_type"] = "stablecoin"
        calc["stablecoin"] = stablecoin
        rows.append({**merged, **calc})
    return pd.DataFrame(rows)

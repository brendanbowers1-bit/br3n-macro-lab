"""
Settlement Window Compression Model (SWC) — risk redistribution when windows collapse.

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

SWC_LIMITATIONS = (
    "SWC estimates net settlement compression benefit under stated assumptions. "
    "Faster ledger settlement may increase liquidity pressure and run-speed fragility. "
    + LAB_LIMITATIONS
)


def _clamp(score: float) -> float:
    return max(0.0, min(100.0, float(score)))


def calculate_settlement_window_compression_row(
    row: pd.Series,
    sensitivity_case: str = "baseline",
) -> dict:
    trad_hours = float(row.get("traditional_settlement_window_hours", 48) or 48)
    ledger_secs = float(row.get("stablecoin_ledger_finality_seconds", 12) or 12)
    effective_hours = float(
        row.get(
            "effective_economic_finality_hours",
            ledger_secs / 3600
            + COMPLIANCE_DELAY_HOURS[sensitivity_case]
            + OFF_RAMP_TIME_HOURS[sensitivity_case]
            + REDEMPTION_TIME_HOURS[sensitivity_case],
        )
        or effective_default(row, sensitivity_case, ledger_secs)
    )
    prefunding = float(row.get("liquidity_prefunding_requirement", 0.15) or 0.15)
    fail_risk = float(row.get("failure_risk", 0.002) or 0.002)
    op_risk = float(row.get("operational_risk_score", 30) or 30)
    run_risk = float(row.get("run_speed_risk", 40) or 40)
    compliance_hours = float(
        row.get("compliance_delay_hours", COMPLIANCE_DELAY_HOURS[sensitivity_case])
        or COMPLIANCE_DELAY_HOURS[sensitivity_case]
    )

    time_reduction = max(0, (trad_hours - effective_hours) / max(trad_hours, 0.001))
    settlement_time_reduction_pct = min(time_reduction * 100, 100)

    counterparty_reduction = _clamp(time_reduction * 80 + (1 - fail_risk * 100) * 20)
    fx_reduction = _clamp(time_reduction * 60)
    working_capital = _clamp(time_reduction * 70 + (1 - prefunding) * 15)

    liquidity_pressure = _clamp(prefunding * 100 + run_risk * 0.3)
    operational_fragility = _clamp(op_risk + fail_risk * 500)
    compliance_drag = _clamp(compliance_hours / max(trad_hours, 1) * 100)
    run_speed_increase = _clamp(run_risk + (1 - time_reduction) * 20)

    swc_core = _clamp(
        settlement_time_reduction_pct * 0.35
        + counterparty_reduction * 0.35
        + working_capital * 0.30
    )
    swc_risk_adjusted = _clamp(swc_core - liquidity_pressure * 0.25 - operational_fragility * 0.20 + 25)
    swc_extended = _clamp(swc_risk_adjusted - run_speed_increase * 0.20 - compliance_drag * 0.15 + 15)

    net_benefit = swc_extended
    if net_benefit >= 75:
        interp = "Net settlement compression benefit (estimated)"
    elif net_benefit >= 55:
        interp = "Mixed compression — risk redistributed (estimated)"
    elif net_benefit >= 40:
        interp = "Limited net benefit after institutional frictions (estimated)"
    else:
        interp = "Compression increases fragility under this spec (estimated)"

    return {
        "settlement_time_reduction_pct": settlement_time_reduction_pct,
        "counterparty_risk_reduction_score": counterparty_reduction,
        "fx_exposure_reduction_score": fx_reduction,
        "working_capital_benefit_score": working_capital,
        "liquidity_pressure_increase_score": liquidity_pressure,
        "operational_fragility_score": operational_fragility,
        "compliance_drag_score": compliance_drag,
        "run_speed_increase_score": run_speed_increase,
        "net_settlement_compression_benefit_score": net_benefit,
        "swc_core": swc_core,
        "swc_risk_adjusted": swc_risk_adjusted,
        "swc_extended": swc_extended,
        "traditional_settlement_window_hours": trad_hours,
        "stablecoin_ledger_finality_seconds": ledger_secs,
        "effective_economic_finality_hours": effective_hours,
        "interpretation": interp,
        "sensitivity_case": sensitivity_case,
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": SWC_LIMITATIONS,
        "data_quality_score": row.get("data_quality_score"),
        "mock_data_flag": row.get("mock_data_flag", False),
    }


def effective_default(row: pd.Series, sensitivity_case: str, ledger_secs: float) -> float:
    return (
        ledger_secs / 3600
        + COMPLIANCE_DELAY_HOURS[sensitivity_case]
        + OFF_RAMP_TIME_HOURS[sensitivity_case]
        + REDEMPTION_TIME_HOURS[sensitivity_case]
    )


def calculate_settlement_window_compression_table(
    remittance: pd.DataFrame,
    chain: pd.DataFrame | None = None,
    off_ramp: pd.DataFrame | None = None,
    sensitivity_case: str = "baseline",
) -> pd.DataFrame:
    if remittance.empty:
        return pd.DataFrame()

    chain_secs = 12.0
    if chain is not None and not chain.empty:
        chain_secs = float(chain["average_confirmation_time_seconds"].mean())

    rows = []
    for _, row in remittance.iterrows():
        merged = row.to_dict()
        merged["stablecoin_ledger_finality_seconds"] = chain_secs
        merged["traditional_settlement_window_hours"] = float(row.get("traditional_transfer_speed_days", 2) or 2) * 24
        merged["effective_economic_finality_hours"] = float(
            row.get("stablecoin_effective_finality_hours", effective_default(pd.Series(merged), sensitivity_case, chain_secs))
        )
        if off_ramp is not None and not off_ramp.empty:
            match = off_ramp[off_ramp["corridor"] == row.get("corridor")]
            if not match.empty:
                merged["compliance_delay_hours"] = match["compliance_delay_hours"].mean()
        calc = calculate_settlement_window_compression_row(pd.Series(merged), sensitivity_case)
        calc["entity"] = row.get("corridor", "unknown")
        calc["entity_type"] = "corridor"
        calc["corridor"] = row.get("corridor")
        rows.append({**merged, **calc})
    return pd.DataFrame(rows)

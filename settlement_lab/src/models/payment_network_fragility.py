"""
Payment Network Fragility Model (PNF) — settlement stress → disruption risk.

Research-only. Not operational guidance.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION

PNF_LIMITATIONS = (
    "PNF is a composite stress indicator, not a real-time monitoring system. "
    + LAB_LIMITATIONS
)


def _regime(score: float) -> str:
    if score >= 80:
        return "normal"
    if score >= 65:
        return "watchlist"
    if score >= 50:
        return "stressed"
    if score >= 35:
        return "fragile"
    return "crisis"


def calculate_fragility_row(
    lag: float,
    fail_rate: float,
    liq_ratio: float,
    fx_vol: float,
    volume_shock: float = 0.0,
    incident: bool = False,
) -> dict:
    score = 100.0
    drivers = []

    score -= min(lag * 8, 25)
    if lag > 1:
        drivers.append("elevated_settlement_lag")

    score -= min(fail_rate * 5000, 20)
    if fail_rate > 0.002:
        drivers.append("rising_failure_rate")

    score -= min((1 - liq_ratio) * 30, 25) if liq_ratio < 1 else 0
    if liq_ratio < 0.15:
        drivers.append("low_liquidity_buffer")

    score -= min(fx_vol * 50, 15)
    if fx_vol > 0.12:
        drivers.append("fx_volatility")

    score -= min(abs(volume_shock) * 20, 10)
    if incident:
        score -= 15
        drivers.append("operational_incident")

    score = max(0, min(100, score))
    return {
        "payment_network_fragility_score": score,
        "fragility_regime": _regime(score),
        "drivers": "; ".join(drivers) or "none",
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": PNF_LIMITATIONS,
    }


def calculate_fragility_table(
    flows: pd.DataFrame,
    liquidity: pd.DataFrame,
    stress_events: pd.DataFrame,
    fx_exposure: pd.DataFrame,
) -> pd.DataFrame:
    if flows.empty:
        return pd.DataFrame()

    liq_ratio_map = {}
    if not liquidity.empty:
        liq = liquidity.copy()
        liq["ratio"] = liq["liquidity_buffer_usd"] / liq["average_daily_settlement_value_usd"].replace(0, 1)
        liq_ratio_map = liq.groupby("payment_system")["ratio"].mean().to_dict()

    fx_vol = float(fx_exposure["fx_volatility_30d"].mean()) if not fx_exposure.empty else 0.12

    agg = flows.groupby(["country", "payment_system"], as_index=False).agg(
        settlement_lag_days=("settlement_lag_days", "mean"),
        failure_rate=("failure_rate", "mean"),
        data_quality_score=("data_quality_score", "mean"),
        mock_data_flag=("mock_data_flag", "first"),
        source_id=("source_id", "first"),
    )

    rows = []
    for _, row in agg.iterrows():
        ps = row["payment_system"]
        lr = liq_ratio_map.get(ps, 0.2)
        incident = not stress_events.empty and (stress_events["country"] == row["country"]).any()
        calc = calculate_fragility_row(
            row["settlement_lag_days"], row["failure_rate"], lr, fx_vol, incident=incident,
        )
        calc["entity"] = f"{row['country']} | {ps}"
        calc["entity_type"] = "payment_system"
        calc["country"] = row["country"]
        calc["payment_system"] = ps
        calc["data_quality_score"] = row["data_quality_score"]
        calc["data_quality_grade"] = row.get("data_quality_grade", "Demo only")
        calc["mock_data_flag"] = row["mock_data_flag"]
        calc["source_id"] = row.get("source_id", "MOCK_DEMO_ONLY")
        calc["methodology_version"] = METHODOLOGY_VERSION
        rows.append(calc)
    return pd.DataFrame(rows)

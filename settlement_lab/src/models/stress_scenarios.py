"""Stress scenarios for Payment Network Fragility."""

from __future__ import annotations

import pandas as pd

from src.models.payment_network_fragility import calculate_fragility_row

SCENARIOS = [
    ("fx_volatility_shock", {"fx_vol_mult": 2.0, "lag_add": 0}),
    ("settlement_bank_outage", {"fx_vol_mult": 1.0, "lag_add": 1.0, "incident": True}),
    ("liquidity_buffer_reduction", {"liq_mult": 0.5, "lag_add": 0}),
    ("cross_border_disruption", {"fx_vol_mult": 1.5, "lag_add": 0.5, "volume_shock": -0.2}),
    ("interest_rate_shock", {"coc_add": 0.03, "lag_add": 0}),
    ("failed_payment_spike", {"fail_mult": 3.0, "lag_add": 0.2}),
]


def run_stress_scenarios(baseline: pd.DataFrame) -> pd.DataFrame:
    if baseline.empty:
        return pd.DataFrame()

    rows = []
    for _, row in baseline.iterrows():
        pre_score = row["payment_network_fragility_score"]
        lag = 1.0
        fail = 0.001
        liq = 0.2
        fx = 0.12

        for sid, params in SCENARIOS:
            post = calculate_fragility_row(
                lag + params.get("lag_add", 0),
                fail * params.get("fail_mult", 1),
                liq * params.get("liq_mult", 1),
                fx * params.get("fx_vol_mult", 1),
                params.get("volume_shock", 0),
                params.get("incident", False),
            )
            rows.append({
                "entity": row["entity"],
                "scenario_id": sid,
                "pre_shock_score": pre_score,
                "post_shock_score": post["payment_network_fragility_score"],
                "delta_score": post["payment_network_fragility_score"] - pre_score,
                "post_regime": post["fragility_regime"],
                "drivers": post["drivers"],
                "interpretation": f"Under {sid}, fragility score changes by {post['payment_network_fragility_score'] - pre_score:.1f} points (estimated).",
            })
    return pd.DataFrame(rows)

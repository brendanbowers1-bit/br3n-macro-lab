"""Exploratory empirical tests — associations only, not causal claims."""

from __future__ import annotations

import pandas as pd

INSUFFICIENT = "Insufficient official data for credible inference. This result is descriptive only."


def run_empirical_tests(features: pd.DataFrame, mock_flag: bool = True) -> dict:
    if mock_flag or len(features) < 20:
        return {"warning": INSUFFICIENT, "tests": pd.DataFrame()}

    tests = []
    pairs = [
        ("H1", "operational_liquidity_burden_score", "settlement_lag_days", "negative"),
        ("H2", "payment_network_fragility_score", "finality_quality_index", "negative"),
        ("H3", "settlement_drag_cost_per_100", "cost_of_capital_pct", "positive"),
    ]
    for hid, y, x, sign in pairs:
        if y not in features.columns or x not in features.columns:
            continue
        sub = features[[x, y]].dropna()
        if len(sub) < 8:
            continue
        rho = sub[x].corr(sub[y], method="spearman")
        tests.append({
            "hypothesis_id": hid,
            "x": x, "y": y,
            "spearman_rho": round(rho, 3),
            "expected_sign": sign,
            "n": len(sub),
            "interpretation": "associated with" if abs(rho) > 0.25 else "weak association",
        })
    return {
        "warning": INSUFFICIENT if mock_flag else None,
        "tests": pd.DataFrame(tests),
    }

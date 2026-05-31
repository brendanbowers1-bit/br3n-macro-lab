"""Exploratory empirical tests — associations only, not causal claims."""

from __future__ import annotations

import pandas as pd

INSUFFICIENT = "Insufficient official data for credible inference. This result is descriptive only."


def run_empirical_tests(
    features: pd.DataFrame,
    mock_flag: bool = True,
    pfi_validation: pd.DataFrame | None = None,
) -> dict:
    if mock_flag:
        return {
            "warning": INSUFFICIENT,
            "tests": pd.DataFrame(),
            "pfi_validation": pfi_validation if pfi_validation is not None else pd.DataFrame(),
        }
    if len(features) < 20:
        return {"warning": INSUFFICIENT, "tests": pd.DataFrame(), "pfi_validation": pfi_validation or pd.DataFrame()}

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
    out = {
        "warning": None,
        "tests": pd.DataFrame(tests),
        "pfi_validation": pfi_validation if pfi_validation is not None else pd.DataFrame(),
    }
    if pfi_validation is not None and not pfi_validation.empty:
        within = (pfi_validation["validation_status"] == "within_2pp").mean()
        out["pfi_validation_summary"] = f"{within:.0%} corridors within 2pp of RPW observed costs"
    return out

"""Exploratory empirical tests — associations only, not causal claims."""

from __future__ import annotations

import pandas as pd

from src.research.hypotheses import HYPOTHESES

INSUFFICIENT = (
    "Insufficient official data for credible inference. "
    "This result is descriptive only."
)


def _spearman_test(features: pd.DataFrame, hid: str, y: str, x: str, sign: str) -> dict | None:
    if y not in features.columns or x not in features.columns:
        return None
    sub = features[[x, y]].dropna()
    if len(sub) < 8:
        return None
    rho = sub[x].corr(sub[y], method="spearman")
    aligned = (sign == "positive" and rho > 0.15) or (sign == "negative" and rho < -0.15) or (sign == "mixed")
    return {
        "hypothesis_id": hid,
        "x": x,
        "y": y,
        "spearman_rho": round(float(rho), 3),
        "expected_sign": sign,
        "n": len(sub),
        "interpretation": "associated with" if aligned and abs(rho) > 0.25 else "weak or inconsistent association",
        "causal_claim": False,
    }


def run_empirical_tests(
    features: pd.DataFrame,
    mock_flag: bool = True,
) -> dict:
    if mock_flag or features.empty:
        return {
            "warning": INSUFFICIENT,
            "tests": pd.DataFrame(),
            "hypotheses_tested": len(HYPOTHESES),
            "limitations": "Mock or insufficient data — descriptive demo only. No causal claims.",
        }

    if len(features) < 20:
        return {
            "warning": INSUFFICIENT,
            "tests": pd.DataFrame(),
            "hypotheses_tested": len(HYPOTHESES),
            "limitations": "Sample too small for credible inference.",
        }

    test_specs = [
        ("H1", "economic_finality_score", "ledger_finality_seconds", "mixed"),
        ("H2", "stablecoin_advantage_score", "off_ramp_fee_loss_pct", "negative"),
        ("H3", "peg_deviation_bps", "reserve_liquidity_score", "negative"),
        ("H4", "stablecoin_dollarization_index", "local_inflation_yoy", "positive"),
        ("H5", "effective_economic_finality_hours", "compliance_delay_hours", "positive"),
    ]

    alt_columns = {
        "ledger_finality_seconds": ["average_confirmation_time_seconds", "ledger_finality_seconds"],
        "off_ramp_fee_loss_pct": ["stablecoin_offramp_fee_pct", "off_ramp_fee_loss_pct"],
        "reserve_liquidity_score": ["reserve_liquidity_score"],
        "local_inflation_yoy": ["local_inflation_yoy", "inflation_yoy"],
        "compliance_delay_hours": ["compliance_delay_hours", "compliance_delay_cost_pct"],
    }

    tests = []
    for hid, y, x, sign in test_specs:
        cols = alt_columns.get(x, [x])
        for col in cols:
            if col in features.columns:
                result = _spearman_test(features, hid, y, col, sign)
                if result:
                    tests.append(result)
                break

    return {
        "warning": None,
        "tests": pd.DataFrame(tests),
        "hypotheses_tested": len(HYPOTHESES),
        "limitations": (
            "Spearman associations only — not causal identification. "
            "Controls listed in hypotheses.py are not fully implemented in bivariate tests."
        ),
    }

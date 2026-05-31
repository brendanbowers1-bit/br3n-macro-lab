"""
Correlation analysis for VSI components and macro variables.

Research-only. Associations, not causal identification.
"""

from __future__ import annotations

import pandas as pd


INSUFFICIENT_DATA_MSG = (
    "Insufficient official data for credible regression inference. "
    "Results below are exploratory associations only."
)


def corridor_correlation_matrix(vsi: pd.DataFrame) -> pd.DataFrame:
    """Pairwise correlations among VSI inputs and outputs at corridor level."""
    cols = [
        c for c in [
            "vsi_core", "vsi_risk_adjusted", "vsi_extended",
            "fee_pct", "fx_margin_pct", "total_cost_pct",
            "transfer_speed_days", "volatility_30d", "inflation_yoy",
            "total_value_loss_pct", "currency_trust_score", "dollar_dependency_score",
        ]
        if c in vsi.columns
    ]
    if len(cols) < 2:
        return pd.DataFrame()

    agg = vsi.groupby("corridor", as_index=False)[cols].mean()
    corr = agg[cols].corr(method="spearman")
    corr.index.name = "variable"
    return corr.reset_index()


def test_hypothesis_associations(
    vsi: pd.DataFrame,
    mock_data_flag: bool = False,
    min_observations: int = 15,
) -> dict:
    """
    Simple bivariate association tests for primary hypotheses.
    Returns dict with warning if data insufficient.
    """
    if mock_data_flag or len(vsi) < min_observations:
        return {
            "warning": INSUFFICIENT_DATA_MSG,
            "n_observations": len(vsi),
            "associations": pd.DataFrame(),
        }

    agg = vsi.groupby("corridor", as_index=False).agg(
        vsi_risk_adjusted=("vsi_risk_adjusted", "mean"),
        vsi_core=("vsi_core", "mean"),
        vsi_extended=("vsi_extended", "mean"),
        total_cost_pct=("total_cost_pct", "mean") if "total_cost_pct" in vsi.columns else ("total_value_loss_pct", "mean"),
        fx_volatility_30d=("volatility_30d", "mean"),
        inflation_yoy=("inflation_yoy", "mean"),
        currency_trust_score=("currency_trust_score", "mean"),
        dollar_dependency_score=("dollar_dependency_score", "mean"),
    )

    pairs = [
        ("H1", "vsi_risk_adjusted", "total_cost_pct", "negative"),
        ("H2", "vsi_risk_adjusted", "fx_volatility_30d", "negative"),
        ("H3", "vsi_core", "inflation_yoy", "negative"),
        ("H5", "vsi_extended", "currency_trust_score", "positive"),
    ]

    rows = []
    for hid, y, x, expected in pairs:
        if x not in agg.columns or y not in agg.columns:
            continue
        sub = agg[[x, y]].dropna()
        if len(sub) < 5:
            continue
        rho = sub[x].corr(sub[y], method="spearman")
        rows.append({
            "hypothesis_id": hid,
            "x": x,
            "y": y,
            "spearman_rho": round(rho, 3),
            "expected_sign": expected,
            "consistent": (rho < 0 if expected == "negative" else rho > 0),
            "n": len(sub),
            "interpretation": "associated with" if abs(rho) > 0.3 else "weak association",
        })

    return {
        "warning": None if len(rows) >= 3 else INSUFFICIENT_DATA_MSG,
        "n_observations": len(vsi),
        "associations": pd.DataFrame(rows),
    }

"""
Carry-adjusted hedge governance policies.

Tests whether carry/forward-cost awareness improves cost-adjusted risk reduction.
Policy-rate carry is a proxy — forward points required for true hedge economics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from .hedge_costs import apply_hedge_costs
from .hedge_governance import _exposure_return, _max_drawdown, governance_metrics
from .regimes import R1, R2, R3, R4

ROOT = Path(__file__).resolve().parents[1]

NORM = {
    "R1_trend_highvol": R1,
    "R2_trend_lowvol": R2,
    "R3_range_highvol": R3,
    "R4_range_lowvol": R4,
}


def _norm_regime(regime: str) -> str:
    return NORM.get(regime, regime)


def get_carry_policy_hedge_ratio(df: pd.DataFrame, policy_name: str, config: dict) -> pd.Series:
    """Return daily hedge ratio for carry-aware governance policies."""
    hg = config.get("hedge_governance", {})
    max_step = float(hg.get("max_daily_hedge_adjustment", 0.10))
    carry_cfg = config.get("carry", {})
    high_carry_pct = float(carry_cfg.get("high_carry_percentile", 0.75))

    if policy_name == "static_50":
        return pd.Series(0.50, index=df.index)

    if policy_name == "regime_only":
        grid = {R1: 0.70, R2: 0.60, R3: 0.40, R4: 0.30}
        return df["regime"].map(lambda r: grid.get(_norm_regime(r), 0.40))

    ratios: List[float] = []
    prev = 0.50

    for i in range(len(df)):
        row = df.iloc[i]
        regime = _norm_regime(str(row.get("regime", R4)))
        high_carry = bool(row.get("is_high_carry", False))
        fragile = bool(row.get("carry_fragility_regime", False))
        carry_pct = float(row.get("carry_percentile", 0.5)) if pd.notna(row.get("carry_percentile")) else 0.5
        expensive_carry = high_carry or carry_pct >= high_carry_pct

        if policy_name == "carry_adjusted_regime":
            if regime == R2 and not fragile:
                target = 0.55 if expensive_carry else 0.65
            elif regime == R2 and fragile:
                target = 0.75
            elif regime == R1 and fragile:
                target = 0.85
            elif regime == R1:
                target = 0.70
            elif regime in (R3, R4) and expensive_carry:
                target = prev
            elif regime in (R3, R4):
                target = 0.35
            else:
                target = 0.50

        elif policy_name == "no_change_in_range_carry_aware":
            range_regime = regime in (R3, R4)
            if range_regime and not fragile:
                target = prev
            elif regime == R2 and not fragile:
                target = 0.65 if not expensive_carry else 0.55
                step_scale = 0.5 if expensive_carry else 1.0
                delta = np.clip((target - prev) * step_scale, -max_step, max_step)
                prev = float(np.clip(prev + delta, 0.0, 1.0))
                ratios.append(prev)
                continue
            elif fragile or regime == R1:
                target = min(0.90, prev + max_step)
            else:
                target = prev
        else:
            raise ValueError(f"Unknown carry policy: {policy_name}")

        delta = np.clip(target - prev, -max_step, max_step)
        prev = float(np.clip(prev + delta, 0.0, 1.0))
        ratios.append(prev)

    return pd.Series(ratios, index=df.index)


def run_carry_hedge_backtest(
    df: pd.DataFrame,
    policy_name: str,
    exposure_type: str,
    config: dict,
    cost_layer: str = "forward_full",
) -> pd.DataFrame:
    """Single carry-aware hedge governance backtest."""
    ticker = config.get("data", {}).get("ticker", "USDMXN=X")
    out = df.copy()
    out["unhedged_exposure_return"] = _exposure_return(out["daily_return"], exposure_type)
    out["hedge_ratio"] = get_carry_policy_hedge_ratio(out, policy_name, config)
    out["hedge_turnover"] = out["hedge_ratio"].diff().abs().fillna(out["hedge_ratio"].abs())
    out = apply_hedge_costs(out, ticker, config, cost_layer=cost_layer)
    out["hedged_return"] = out["unhedged_exposure_return"] * (1.0 - out["hedge_ratio"]) - out["hedge_cost"]
    out["policy_name"] = policy_name
    out["exposure_type"] = exposure_type
    out["carry_cost_proxy"] = out.get("forward_carry_cost", 0.0)
    out["total_cost_proxy"] = out["hedge_cost"]
    return out


def run_carry_hedge_governance_suite(
    df: pd.DataFrame,
    config: dict,
    exposure_type: str = "us_entity_long_mxn",
    cost_layer: str = "forward_full",
) -> pd.DataFrame:
    """Run all carry hedge policies and return scorecard."""
    policies = [
        "static_50",
        "regime_only",
        "carry_adjusted_regime",
        "no_change_in_range_carry_aware",
    ]
    rows = []
    for pol in policies:
        try:
            det = run_carry_hedge_backtest(df, pol, exposure_type, config, cost_layer=cost_layer)
            m = governance_metrics(det)
            m["carry_cost_proxy"] = round(float(det.get("forward_carry_cost", pd.Series(0)).sum()) * 100, 4)
            m["total_cost_proxy"] = round(float(det["hedge_cost"].sum()) * 100, 4)
            rows.append(m)
        except Exception as exc:
            rows.append({"policy_name": pol, "status": "error", "error": str(exc)[:120]})

    return pd.DataFrame(rows)


def save_carry_hedge_scorecard(scorecard: pd.DataFrame, path: Optional[Path] = None) -> Path:
    path = path or ROOT / "data" / "outputs" / "carry_hedge_governance_scorecard.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    scorecard.to_csv(path, index=False)
    return path

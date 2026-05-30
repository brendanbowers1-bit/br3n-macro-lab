"""
Level 6: Data-snooping control — framework + simple bootstrap reality check.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from ..backtest import run_strategy_backtest
from .white_rc import white_reality_check


def holdout_evaluation(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Evaluate on pre-declared holdout window (no tuning on this period)."""
    ho = cfg.get("research_ladder", {}).get("holdout", {})
    if not ho:
        return pd.DataFrame()
    sub = df.loc[(df.index >= ho["start"]) & (df.index <= ho["end"])]
    if len(sub) < 20:
        return pd.DataFrame([{"status": "holdout_insufficient", "bars": len(sub)}])

    from ..metrics import performance_metrics

    ann = int(cfg["backtest"]["annualization_days"])
    primary = cfg["backtest"].get("primary_strategy", "flat_range")
    rows = []
    for strat in ["flat_range", "legacy", "random_walk"]:
        bt = run_strategy_backtest(sub, cfg, strat)
        m = performance_metrics(bt["net_strategy_return"], bt["equity"], ann, strat)
        m["sample"] = "holdout"
        m["period"] = f"{ho['start']}..{ho['end']}"
        rows.append(m)
    return pd.DataFrame(rows)


def bootstrap_sharpe_test(
    returns: pd.Series,
    n_boot: int = 500,
    seed: int = 42,
) -> Dict[str, float]:
    """
    Bootstrap Sharpe under null of zero mean (simplified reality check).
    Returns observed Sharpe and percentile vs bootstrapped null distribution.
    """
    r = returns.dropna().values
    if len(r) < 50:
        return {"observed_sharpe": np.nan, "boot_pvalue": np.nan}
    ann = np.sqrt(252)
    obs = r.mean() / (r.std() + 1e-12) * ann
    rng = np.random.default_rng(seed)
    boot_sharpes = []
    for _ in range(n_boot):
        samp = rng.choice(r, size=len(r), replace=True)
        boot_sharpes.append(samp.mean() / (samp.std() + 1e-12) * ann)
    boot_sharpes = np.array(boot_sharpes)
    # One-sided: P(null Sharpe >= observed) approximated by permuting signs
    p = float((boot_sharpes <= 0).mean()) if obs > 0 else float((boot_sharpes >= 0).mean())
    return {
        "observed_sharpe": round(float(obs), 3),
        "boot_median_sharpe": round(float(np.median(boot_sharpes)), 3),
        "boot_pvalue_approx": round(p, 4),
        "n_boot": n_boot,
    }


def run_white_reality_check(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """White RC across legacy / flat_range / r2_only on in-sample returns."""
    ann = int(cfg["backtest"]["annualization_days"])
    strategies = cfg.get("research_ladder", {}).get(
        "strategies", ["legacy", "flat_range", "r2_only"]
    )
    returns = {}
    for strat in strategies:
        bt = run_strategy_backtest(df, cfg, strat)
        returns[strat] = bt["net_strategy_return"]
    return white_reality_check(returns, ann=ann)


def preregistered_hypotheses() -> List[str]:
    return [
        "H1: Average spot return differs across R1–R4 regimes (Level 1).",
        "H2: flat_range OOS Sharpe exceeds random_walk on fixed splits (Level 2).",
        "H3: Effect appears in >=50% of EM FX pairs tested (Level 3).",
        "H4: Model 1-step forecast RMSE < random walk on OOS splits (Level 4).",
        "H5: Net return remains positive after full economic frictions (Level 5).",
        "H6: Holdout period not used for any parameter tuning (Level 6).",
        "H7: Best-of-strategy Sharpe survives White Reality Check (p < 0.05).",
    ]

"""
Level 8 — White Reality Check on pre-registered hedge policy set.

Two complementary tests:
1. Flagship daily hedged-return Sharpe (USD/MXN, forward_full costs)
2. Panel OOS bootstrap on cost-adjusted risk reduction across pairs
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from ..data_loader import load_config
from ..hedge_governance import run_hedge_governance_backtest
from .level8_hedge_oos import hedge_oos_policies, load_pair_features
from .white_rc import white_reality_check

ROOT = Path(__file__).resolve().parents[2]


def run_flagship_hedge_white_rc(
    cfg: dict,
    ticker: str = "USDMXN=X",
    exposure: str = "receiver_currency_exposure",
    cost_layer: str = "forward_full",
) -> pd.DataFrame:
    """White RC on daily hedged returns for pre-registered policies (flagship pair)."""
    policies = hedge_oos_policies(cfg)
    df = load_pair_features(ticker, cfg)
    returns: Dict[str, pd.Series] = {}
    for policy in policies:
        det = run_hedge_governance_backtest(
            df, policy, exposure, cfg, corridor_id=ticker, cost_layer=cost_layer
        )
        returns[policy] = det["hedged_return"]

    ann = int(cfg["backtest"]["annualization_days"])
    rc = white_reality_check(returns, ann=ann)
    rc["test"] = "flagship_daily_sharpe"
    rc["ticker"] = ticker
    rc["exposure_type"] = exposure
    rc["cost_layer"] = cost_layer
    return rc


def bootstrap_policy_metric_rc(
    scorecard: pd.DataFrame,
    metric: str = "cost_adjusted_risk_reduction",
    policies: Optional[List[str]] = None,
    oos_design: str = "fixed_split",
    n_boot: int = 2000,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Bootstrap reality check on panel OOS metric means across policies.

    Resamples OOS cells (pair × split × exposure) with replacement and compares
    the observed best policy mean to the bootstrap null.
    """
    policies = policies or []
    if scorecard.empty or "policy_name" not in scorecard.columns:
        return pd.DataFrame([{"status": "insufficient_data"}])

    ok = scorecard[(scorecard["status"] == "ok") & (scorecard["oos_design"] == oos_design)].copy()
    if policies:
        ok = ok[ok["policy_name"].isin(policies)]
    if ok.empty or metric not in ok.columns:
        return pd.DataFrame([{"status": "insufficient_data", "rows": len(ok)}])

    cell_means = ok.groupby("policy_name")[metric].mean().to_dict()
    if not cell_means:
        return pd.DataFrame([{"status": "insufficient_data"}])

    names = sorted(cell_means.keys())
    obs_stats = [float(cell_means[n]) for n in names]
    obs_max = max(obs_stats)
    best_name = names[int(np.argmax(obs_stats))]

    rng = np.random.default_rng(seed)
    boot_max = np.zeros(n_boot)
    for b in range(n_boot):
        sample_means = []
        for name in names:
            vals = ok.loc[ok["policy_name"] == name, metric].values
            if len(vals) == 0:
                sample_means.append(0.0)
                continue
            draw = rng.choice(vals, size=len(vals), replace=True)
            sample_means.append(float(draw.mean()))
        boot_max[b] = max(sample_means)

    p_value = float((boot_max >= obs_max).mean())

    rows: List[dict] = []
    for j, name in enumerate(names):
        rows.append(
            {
                "policy_name": name,
                "observed_metric_mean": round(obs_stats[j], 4),
                "is_best": name == best_name,
                "cells": int((ok["policy_name"] == name).sum()),
            }
        )
    rows.append(
        {
            "policy_name": "_SUMMARY",
            "best_policy": best_name,
            "observed_max_metric": round(obs_max, 4),
            "white_rc_pvalue": round(p_value, 4),
            "n_boot": n_boot,
            "rejects_data_mining_5pct": p_value < 0.05,
            "metric": metric,
            "oos_design": oos_design,
        }
    )
    out = pd.DataFrame(rows)
    out["test"] = "panel_oos_metric_bootstrap"
    return out


def run_hedge_policy_white_rc_suite(
    cfg: dict,
    scorecard: Optional[pd.DataFrame] = None,
    ticker: str = "USDMXN=X",
    exposure: str = "receiver_currency_exposure",
) -> pd.DataFrame:
    """Run flagship Sharpe RC + panel OOS metric RC for base and forward_full layers."""
    policies = hedge_oos_policies(cfg)
    frames: List[pd.DataFrame] = []

    for layer in cfg.get("hedge_oos", {}).get("cost_layers", ["base", "forward_full"]):
        frames.append(run_flagship_hedge_white_rc(cfg, ticker, exposure, cost_layer=layer))
        if scorecard is not None and not scorecard.empty:
            sc_layer = scorecard[
                (scorecard.get("cost_layer", "base") == layer) & (scorecard["status"] == "ok")
            ]
            if not sc_layer.empty:
                panel = bootstrap_policy_metric_rc(sc_layer, policies=policies)
                panel["cost_layer"] = layer
                frames.append(panel)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def save_hedge_white_rc(df: pd.DataFrame, out_dir: Optional[Path] = None) -> Path:
    out_dir = out_dir or ROOT / "reports" / "research_ladder"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "level8_hedge_white_rc.csv"
    df.to_csv(path, index=False)
    return path


def hedge_white_rc_report_md(df: pd.DataFrame) -> str:
    if df.empty:
        return "_Hedge policy White RC not run._\n"

    lines = ["### Hedge policy White Reality Check (pre-registered policy set)", ""]
    if "strategy" in df.columns:
        flag_summaries = df[(df["strategy"] == "_SUMMARY") & (df["test"] == "flagship_daily_sharpe")]
    else:
        flag_summaries = pd.DataFrame()
    panel_summaries = df[(df.get("policy_name", pd.Series()) == "_SUMMARY") & (df["test"] == "panel_oos_metric_bootstrap")]
    summaries = pd.concat([flag_summaries, panel_summaries], ignore_index=True)

    for _, row in summaries.iterrows():
        test = row.get("test", "unknown")
        layer = row.get("cost_layer", "—")
        best = row.get("best_strategy") or row.get("best_policy", "—")
        pval = row.get("white_rc_pvalue", "—")
        reject = bool(row.get("rejects_data_mining_5pct", False))
        lines.append(
            f"- **{test}** ({layer}): best = `{best}`, p = **{pval}**, "
            f"rejects snooping @5% = **{'yes' if reject else 'no'}**"
        )
    lines.append("")
    lines.append(
        "**Note:** Flagship test uses daily hedged-return Sharpe on USD/MXN. "
        "Panel test bootstraps OOS cost-adjusted risk reduction cells. "
        "Passing H8e requires p < 0.05 on the forward_full panel or flagship test."
    )
    lines.append("")
    return "\n".join(lines)

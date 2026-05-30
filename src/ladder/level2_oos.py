"""
Level 2: Out-of-sample — does strategy beat random walk on unseen data?
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd

from ..backtest import run_strategy_backtest
from ..metrics import performance_metrics


def _slice(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    return df.loc[(df.index >= start) & (df.index <= end)].copy()


def run_fixed_splits(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    splits = cfg.get("research_ladder", {}).get("level2_splits", [])
    ann = int(cfg["backtest"]["annualization_days"])
    strategies = cfg.get("research_ladder", {}).get(
        "strategies", ["legacy", "flat_range", "r2_only"]
    )
    rows: List[dict] = []

    for sp in splits:
        train = _slice(df, sp["train_start"], sp["train_end"])
        test = _slice(df, sp["test_start"], sp["test_end"])
        if len(test) < 30:
            rows.append(
                {
                    "split": sp["name"],
                    "status": "insufficient_test_data",
                    "test_bars": len(test),
                    "test_start": sp["test_start"],
                    "test_end": sp["test_end"],
                }
            )
            continue

        for strat in strategies + ["random_walk"]:
            bt_te = run_strategy_backtest(test, cfg, strat)
            m = performance_metrics(
                bt_te["net_strategy_return"], bt_te["equity"], ann, strat
            )
            rows.append(
                {
                    "split": sp["name"],
                    "sample": "test",
                    "train_bars": len(train),
                    "test_bars": len(test),
                    "test_period": f"{sp['test_start']}..{sp['test_end']}",
                    "strategy": strat,
                    "total_return_pct": m["total_return_pct"],
                    "sharpe": m["sharpe"],
                    "max_drawdown_pct": m["max_drawdown_pct"],
                    "beats_random_walk_sharpe": None,
                }
            )

        # Compare primary vs random_walk on this test window
        primary = cfg["backtest"].get("primary_strategy", "flat_range")
        rw = [r for r in rows if r.get("split") == sp["name"] and r.get("strategy") == "random_walk"]
        pr = [r for r in rows if r.get("split") == sp["name"] and r.get("strategy") == primary]
        if rw and pr:
            pr[-1]["beats_random_walk_sharpe"] = pr[-1]["sharpe"] > rw[-1]["sharpe"]

    return pd.DataFrame(rows)


def oos_summary(oos_df: pd.DataFrame, primary: str = "flat_range") -> pd.DataFrame:
    if oos_df.empty:
        return oos_df
    sub = oos_df[(oos_df["sample"] == "test") & (oos_df["strategy"].isin([primary, "random_walk"]))]
    if sub.empty:
        return sub
    return sub.pivot_table(
        index=["split", "test_period"],
        columns="strategy",
        values=["sharpe", "total_return_pct"],
        aggfunc="first",
    )

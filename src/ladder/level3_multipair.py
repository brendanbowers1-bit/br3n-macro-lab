"""
Level 3: Multi-pair — does regime logic work outside USD/MXN?
Includes full-sample scorecard and fixed-split OOS per pair.
"""

from __future__ import annotations

from typing import List

import pandas as pd

from ..backtest import scorecard
from ..data_loader import load_pair_prices
from ..features import build_features
from ..regimes import classify_regimes
from .level2_oos import run_fixed_splits


def load_pair_panel(ticker: str, years: int, force_refresh: bool = False) -> pd.DataFrame:
    px, _ = load_pair_prices(ticker, years, force_refresh=force_refresh)
    return px


def run_multipair(
    cfg: dict,
    tickers: List[str] | None = None,
    force_refresh: bool = False,
) -> pd.DataFrame:
    tickers = tickers or cfg.get("research_ladder", {}).get("pairs", [cfg["data"]["ticker"]])
    years = int(cfg["data"]["history_years"])
    primary = cfg["backtest"].get("primary_strategy", "flat_range")
    rows = []

    for ticker in tickers:
        try:
            px = load_pair_panel(ticker, years, force_refresh=force_refresh)
            df = classify_regimes(build_features(px, cfg), cfg)
            sc = scorecard(df, cfg)
            sc["ticker"] = ticker
            sc["bars"] = len(df)
            sc["start"] = str(df.index.min().date())
            sc["end"] = str(df.index.max().date())
            flat = sc[sc["strategy"] == primary].iloc[0]
            rw = sc[sc["strategy"] == "random_walk"].iloc[0]
            sc["primary_beats_rw"] = flat["sharpe"] > rw["sharpe"]
            rows.append(sc)
        except Exception as exc:
            rows.append(
                pd.DataFrame(
                    [{"ticker": ticker, "strategy": "ERROR", "error": str(exc)[:120]}]
                )
            )

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def run_multipair_oos(
    cfg: dict,
    tickers: List[str] | None = None,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """Fixed OOS splits (Level 2 design) applied to each pair."""
    tickers = tickers or cfg.get("research_ladder", {}).get("pairs", [cfg["data"]["ticker"]])
    years = int(cfg["data"]["history_years"])
    primary = cfg["backtest"].get("primary_strategy", "flat_range")
    rows: List[pd.DataFrame] = []

    for ticker in tickers:
        try:
            px = load_pair_panel(ticker, years, force_refresh=force_refresh)
            df = classify_regimes(build_features(px, cfg), cfg)
            oos = run_fixed_splits(df, cfg)
            if oos.empty:
                continue
            oos["ticker"] = ticker
            test = oos[oos["sample"] == "test"].copy()
            if not test.empty:
                rw = test[test["strategy"] == "random_walk"][["split", "sharpe"]].rename(
                    columns={"sharpe": "rw_sharpe"}
                )
                pr = test[test["strategy"] == primary][["split", "sharpe", "total_return_pct"]].rename(
                    columns={
                        "sharpe": "primary_sharpe",
                        "total_return_pct": "primary_return_pct",
                    }
                )
                merged = pr.merge(rw, on="split", how="left")
                merged["beats_rw"] = merged["primary_sharpe"] > merged["rw_sharpe"]
                merged["ticker"] = ticker
                rows.append(merged)
        except Exception as exc:
            rows.append(
                pd.DataFrame(
                    [
                        {
                            "ticker": ticker,
                            "split": "ERROR",
                            "error": str(exc)[:120],
                        }
                    ]
                )
            )

    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    return out


def multipair_oos_by_pair(oos_df: pd.DataFrame) -> pd.DataFrame:
    """Per pair: how many OOS splits beat random walk."""
    if oos_df.empty or "beats_rw" not in oos_df.columns:
        return pd.DataFrame()
    valid = oos_df[oos_df["split"] != "ERROR"]
    by_pair = (
        valid.groupby("ticker")["beats_rw"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "splits_beating_rw", "count": "splits_total"})
        .reset_index()
    )
    by_pair["all_splits_beat_rw"] = by_pair["splits_beating_rw"] == by_pair["splits_total"]
    return by_pair


def multipair_oos_aggregate(oos_df: pd.DataFrame) -> pd.DataFrame:
    """One-row summary across all pair×split OOS cells."""
    if oos_df.empty or "beats_rw" not in oos_df.columns:
        return pd.DataFrame()
    valid = oos_df[oos_df["split"] != "ERROR"]
    return pd.DataFrame(
        [
            {
                "cells": len(valid),
                "beats_rw_cells": int(valid["beats_rw"].sum()),
                "pct_beats_rw": round(100 * valid["beats_rw"].mean(), 1) if len(valid) else 0,
                "pairs_tested": valid["ticker"].nunique(),
            }
        ]
    )

"""
Backtest engine with transaction costs, full output columns, walk-forward.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .metrics import performance_metrics
from .regimes import R1, R2, R3, R4, RANGE_REGIMES, TREND_REGIMES


@dataclass
class WalkForwardFold:
    fold: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp


def _lag(series: pd.Series, days: int) -> pd.Series:
    return series.shift(days).fillna(0.0)


def signal_legacy(df: pd.DataFrame) -> pd.Series:
    sig = pd.Series(0, index=df.index, dtype=int)
    sig.loc[df["ma20"] > df["ma60"]] = 1
    sig.loc[df["ma20"] < df["ma60"]] = -1
    return sig


def signal_flat_range(df: pd.DataFrame) -> pd.Series:
    sig = pd.Series(0, index=df.index, dtype=int)
    in_trend = df["regime"].isin(TREND_REGIMES)
    sig.loc[in_trend & (df["ma20"] > df["ma60"])] = 1
    sig.loc[in_trend & (df["ma20"] < df["ma60"])] = -1
    return sig


def signal_r2_only(df: pd.DataFrame) -> pd.Series:
    sig = pd.Series(0, index=df.index, dtype=int)
    in_r2 = df["regime"] == R2
    sig.loc[in_r2 & (df["ma20"] > df["ma60"])] = 1
    sig.loc[in_r2 & (df["ma20"] < df["ma60"])] = -1
    return sig


def signal_buy_and_hold(df: pd.DataFrame) -> pd.Series:
    return pd.Series(1, index=df.index, dtype=int)


def signal_random_walk(df: pd.DataFrame) -> pd.Series:
    """Flat benchmark — no predictive edge."""
    return pd.Series(0, index=df.index, dtype=int)


SIGNAL_FUNCS = {
    "legacy": signal_legacy,
    "flat_range": signal_flat_range,
    "r2_only": signal_r2_only,
    "buy_and_hold": signal_buy_and_hold,
    "random_walk": signal_random_walk,
}


def position_from_signal(
    df: pd.DataFrame,
    strategy: str,
    cfg: dict,
) -> pd.Series:
    sig = SIGNAL_FUNCS[strategy](df)
    lag = int(cfg["backtest"]["execution_lag_days"])
    pos = _lag(sig.astype(float), lag)
    max_pos = float(cfg["risk"]["max_position"])
    if not cfg["risk"].get("allow_short", True):
        pos = pos.clip(0, max_pos)
    else:
        pos = pos.clip(-max_pos, max_pos)
    if strategy == "flat_range":
        pos.loc[df["regime"].isin(RANGE_REGIMES)] = 0.0
    elif strategy == "r2_only":
        pos.loc[df["regime"] != R2] = 0.0
    return pos


def build_output_frame(df: pd.DataFrame, cfg: dict, strategy: str = "flat_range") -> pd.DataFrame:
    """Full column set for primary strategy export."""
    bt = df.copy()
    bt["signal"] = SIGNAL_FUNCS[strategy](bt)
    bt["position"] = position_from_signal(bt, strategy, cfg)

    pos_bh = position_from_signal(bt, "buy_and_hold", cfg)
    pos_rw = position_from_signal(bt, "random_walk", cfg)

    bt["daily_return"] = bt["daily_return"]
    bt["gross_strategy_return"] = bt["position"] * bt["daily_return"]
    turnover = bt["position"].diff().abs().fillna(bt["position"].abs())
    cost_bps = float(cfg["backtest"]["transaction_cost_bps"])
    bt["transaction_cost"] = turnover * (cost_bps / 10_000.0)
    bt["net_strategy_return"] = bt["gross_strategy_return"] - bt["transaction_cost"]
    bt["buy_hold_return"] = pos_bh * bt["daily_return"]
    bt["random_walk_return"] = pos_rw * bt["daily_return"]

    eq0 = float(cfg["backtest"]["starting_equity"])
    bt["equity_strategy_gross"] = eq0 * (1.0 + bt["gross_strategy_return"]).cumprod()
    bt["equity_strategy_net"] = eq0 * (1.0 + bt["net_strategy_return"]).cumprod()
    bt["equity_buy_hold"] = eq0 * (1.0 + bt["buy_hold_return"]).cumprod()
    bt["equity_random_walk"] = eq0 * (1.0 + bt["random_walk_return"]).cumprod()
    return bt


def run_strategy_backtest(df: pd.DataFrame, cfg: dict, strategy: str) -> pd.DataFrame:
    bt = df.copy()
    bt["position"] = position_from_signal(bt, strategy, cfg)
    bt["gross_strategy_return"] = bt["position"] * bt["daily_return"]
    turnover = bt["position"].diff().abs().fillna(bt["position"].abs())
    cost_bps = float(cfg["backtest"]["transaction_cost_bps"])
    bt["transaction_cost"] = turnover * (cost_bps / 10_000.0)
    bt["net_strategy_return"] = bt["gross_strategy_return"] - bt["transaction_cost"]
    eq0 = float(cfg["backtest"]["starting_equity"])
    bt["equity"] = eq0 * (1.0 + bt["net_strategy_return"]).cumprod()
    bt["turnover"] = turnover
    return bt


def scorecard(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    rows = []
    ann = int(cfg["backtest"]["annualization_days"])
    for name in ["buy_and_hold", "legacy", "flat_range", "r2_only", "random_walk"]:
        bt = run_strategy_backtest(df, cfg, name)
        m = performance_metrics(bt["net_strategy_return"], bt["equity"], ann, name)
        m["trades"] = int(bt["turnover"].gt(0).sum())
        m["pct_flat"] = round(float((bt["position"] == 0).mean()) * 100, 1)
        m["total_cost_pct"] = round(float(bt["transaction_cost"].sum()) * 100, 3)
        rows.append(m)
    return pd.DataFrame(rows)


def generate_walk_forward_folds(index: pd.DatetimeIndex, cfg: dict) -> List[WalkForwardFold]:
    if not cfg["backtest"].get("walk_forward_enabled", True):
        return []
    train_y = int(cfg["backtest"]["train_years"])
    test_y = int(cfg["backtest"]["test_years"])
    folds = []
    train_end = index.min() + pd.DateOffset(years=train_y) - pd.Timedelta(days=1)
    fold_id = 0
    while True:
        test_start = train_end + pd.Timedelta(days=1)
        test_end = test_start + pd.DateOffset(years=test_y) - pd.Timedelta(days=1)
        if test_start > index.max():
            break
        if test_end > index.max():
            test_end = index.max()
        train_start = train_end - pd.DateOffset(years=train_y) + pd.Timedelta(days=1)
        folds.append(
            WalkForwardFold(fold_id, train_start, train_end, test_start, test_end)
        )
        fold_id += 1
        train_end = train_end + pd.DateOffset(years=test_y)
        if test_end >= index.max():
            break
    return folds


def walk_forward_scorecard(df: pd.DataFrame, cfg: dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """In-sample train metrics vs OOS test for legacy and flat_range."""
    folds = generate_walk_forward_folds(df.index, cfg)
    if not folds:
        return pd.DataFrame(), pd.DataFrame()

    is_rows, oos_rows = [], []
    ann = int(cfg["backtest"]["annualization_days"])

    for fold in folds:
        train = df.loc[(df.index >= fold.train_start) & (df.index <= fold.train_end)]
        test = df.loc[(df.index >= fold.test_start) & (df.index <= fold.test_end)]
        if len(test) < 30:
            continue
        for strat in ["legacy", "flat_range"]:
            bt_tr = run_strategy_backtest(train, cfg, strat)
            bt_te = run_strategy_backtest(test, cfg, strat)
            m_is = performance_metrics(bt_tr["net_strategy_return"], bt_tr["equity"], ann, strat)
            m_oos = performance_metrics(bt_te["net_strategy_return"], bt_te["equity"], ann, strat)
            m_is.update({"fold": fold.fold, "sample": "in_sample", "period": f"{fold.train_start.date()}_{fold.train_end.date()}"})
            m_oos.update({"fold": fold.fold, "sample": "out_of_sample", "period": f"{fold.test_start.date()}_{fold.test_end.date()}"})
            is_rows.append(m_is)
            oos_rows.append(m_oos)

    return pd.DataFrame(is_rows), pd.DataFrame(oos_rows)

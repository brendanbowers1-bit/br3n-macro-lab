"""
Level 4: Forecast-error testing vs random walk (zero forecast).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import math

import numpy as np
import pandas as pd

from ..backtest import position_from_signal, SIGNAL_FUNCS


def _forecast_from_train(
    test: pd.DataFrame,
    train: pd.DataFrame,
    strategy: str,
    cfg: dict,
) -> pd.Series:
    """Regime-conditional mean return forecast from train, applied on test."""
    pos = position_from_signal(test, strategy, cfg)
    if "regime" not in train.columns:
        regime_means = train["daily_return"].mean()
        return pos * regime_means
    regime_means = train.groupby("regime")["daily_return"].mean()
    pred = pd.Series(0.0, index=test.index)
    for reg, mu in regime_means.items():
        pred.loc[test["regime"] == reg] = pos.loc[test["regime"] == reg] * mu
    # Fallback: signal * train overall mean
    pred = pred.fillna(pos * train["daily_return"].mean())
    return pred


def forecast_errors(
    actual: pd.Series,
    predicted: pd.Series,
) -> Dict[str, float]:
    a = actual.dropna()
    p = predicted.reindex(a.index).fillna(0)
    err = a - p
    mae = float(np.abs(err).mean())
    rmse = float(np.sqrt((err ** 2).mean()))
    # Directional accuracy (non-zero moves)
    mask = a != 0
    if mask.sum() > 0:
        da = float((np.sign(p[mask]) == np.sign(a[mask])).mean() * 100)
    else:
        da = np.nan
    return {"mae": mae, "rmse": rmse, "directional_accuracy_pct": da, "n": int(len(a))}


def diebold_mariano(
    e1: np.ndarray,
    e2: np.ndarray,
    h: int = 1,
) -> Tuple[float, float]:
    """
    DM test: H0 equal forecast accuracy.
    e1, e2 are loss series (e.g. squared errors). Uses squared-error loss differential.
    Returns (dm_stat, p_value_two_sided).
    """
    d = e1 - e2
    T = len(d)
    if T < 10:
        return np.nan, np.nan
    d_bar = d.mean()
    # Newey-West style variance with h-1 lags
    gamma0 = np.var(d, ddof=1)
    var_d = gamma0 / T
    if h > 1:
        for lag in range(1, h):
            w = 1 - lag / h
            cov = np.cov(d[lag:], d[:-lag])[0, 1] if len(d) > lag else 0
            var_d += 2 * w * cov / T
    stat = d_bar / np.sqrt(var_d + 1e-12)
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(stat) / math.sqrt(2))))
    return float(stat), float(p)


def run_forecast_tests(
    df: pd.DataFrame,
    cfg: dict,
    splits: List[dict] | None = None,
) -> pd.DataFrame:
    splits = splits or cfg.get("research_ladder", {}).get("level2_splits", [])
    strategy = cfg["backtest"].get("primary_strategy", "flat_range")
    rows = []

    for sp in splits:
        train = df.loc[(df.index >= sp["train_start"]) & (df.index <= sp["train_end"])]
        test = df.loc[(df.index >= sp["test_start"]) & (df.index <= sp["test_end"])]
        if len(test) < 30 or len(train) < 60:
            continue

        if "fwd_return_1d" in test.columns:
            actual = test["fwd_return_1d"]
        else:
            actual = test["daily_return"].shift(-1)
        actual = actual.dropna()
        test = test.loc[actual.index]
        train = train.dropna(subset=["daily_return"])
        pred_model = _forecast_from_train(test, train, strategy, cfg).reindex(actual.index)
        pred_rw = pd.Series(0.0, index=actual.index)

        em = forecast_errors(actual, pred_model)
        er = forecast_errors(actual, pred_rw)

        e1 = (actual - pred_model).dropna().values ** 2
        e2 = (actual - pred_rw).reindex(actual.index).fillna(0).values ** 2
        dm_stat, dm_p = diebold_mariano(e1, e2)

        rows.append(
            {
                "split": sp["name"],
                "test_period": f"{sp['test_start']}..{sp['test_end']}",
                "strategy": strategy,
                "mae_model": em["mae"],
                "rmse_model": em["rmse"],
                "dir_acc_model_pct": em["directional_accuracy_pct"],
                "mae_rw": er["mae"],
                "rmse_rw": er["rmse"],
                "dir_acc_rw_pct": er["directional_accuracy_pct"],
                "dm_stat": dm_stat,
                "dm_pvalue": dm_p,
                "model_beats_rw_mae": em["mae"] < er["mae"],
                "clark_west_note": "CW not run — use when nested OLS forecast; rules are non-nested here.",
            }
        )

    return pd.DataFrame(rows)

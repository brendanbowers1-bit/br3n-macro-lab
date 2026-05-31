"""
Walk-forward validation and model comparison for the FX research terminal.

Uses expanding/rolling train windows — no random shuffled splits.
"""

from __future__ import annotations

from typing import Callable, Iterable

import numpy as np
import pandas as pd

from src.features.fx_terminal_features import FEATURE_COLUMNS, get_model_matrix
from src.models.baselines import BaseFXModel, RidgeReturnModel, clone_baseline_model, get_baseline_models, signals_to_dataframe


def generate_walk_forward_splits(
    dates: pd.Series,
    train_years: int = 5,
    test_years: int = 1,
) -> list[dict]:
    """Generate non-overlapping walk-forward train/test date ranges."""
    dates = pd.to_datetime(dates).sort_values().unique()
    if len(dates) < 252:
        mid = len(dates) // 2
        return [{"train_end": dates[mid - 1], "test_start": dates[mid], "test_end": dates[-1]}]

    splits = []
    start = dates[0]
    while True:
        train_end = start + pd.DateOffset(years=train_years)
        test_start = train_end + pd.Timedelta(days=1)
        test_end = test_start + pd.DateOffset(years=test_years)
        if test_end > dates[-1]:
            test_end = dates[-1]
        if test_start >= test_end:
            break
        splits.append(
            {
                "train_start": start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
            }
        )
        start = test_start
        if start >= dates[-1] - pd.DateOffset(years=test_years):
            break
    return splits


def _strategy_returns(signals: pd.DataFrame, features: pd.DataFrame, horizon: int) -> pd.Series:
    """Simple directional strategy returns for scoring."""
    ret_col = f"forward_return_{horizon}d"
    merged = signals.merge(features[["date", "pair", ret_col]], on=["date", "pair"], how="left")
    direction = merged["signal"].map({"long": 1, "short": -1, "neutral": 0}).fillna(0)
    return direction * merged[ret_col].fillna(0)


def _score_returns(rets: pd.Series) -> dict:
    rets = rets.dropna()
    if rets.empty:
        return {
            "hit_rate": np.nan,
            "average_return": np.nan,
            "volatility": np.nan,
            "information_ratio": np.nan,
            "max_drawdown": np.nan,
            "number_of_trades": 0,
            "sharpe_like": np.nan,
        }
    trades = rets[rets != 0]
    cum = (1 + rets).cumprod()
    dd = cum / cum.cummax() - 1
    vol = rets.std() * np.sqrt(252 / max(len(rets) / len(rets.index.unique()), 1))
    ir = rets.mean() / rets.std() * np.sqrt(252) if rets.std() > 0 else np.nan
    return {
        "hit_rate": float((trades > 0).mean()) if len(trades) else np.nan,
        "average_return": float(rets.mean()),
        "volatility": float(rets.std()),
        "information_ratio": float(ir) if not np.isnan(ir) else np.nan,
        "max_drawdown": float(dd.min()),
        "number_of_trades": int((rets != 0).sum()),
        "sharpe_like": float(ir) if not np.isnan(ir) else np.nan,
    }


def run_walk_forward_for_model(
    model: BaseFXModel,
    features: pd.DataFrame,
    pair: str,
    horizon: int = 5,
    train_years: int = 5,
    test_years: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Walk-forward OOS evaluation for one model and pair.

    Returns (signals_df, metrics_row_df).
    """
    pair_df = features[features["pair"] == pair].copy()
    pair_df["date"] = pd.to_datetime(pair_df["date"])
    splits = generate_walk_forward_splits(pair_df["date"], train_years, test_years)
    all_signals = []

    for split in splits:
        train = pair_df[pair_df["date"] <= split["train_end"]]
        test = pair_df[(pair_df["date"] >= split["test_start"]) & (pair_df["date"] <= split["test_end"])]
        if len(train) < 100 or len(test) < 20:
            continue
        X_train, y_dir, y_ret = get_model_matrix(train, horizon=horizon)
        X_test, _, _ = get_model_matrix(test, horizon=horizon)
        meta_test = test.loc[X_test.index].reset_index(drop=True)
        X_test = X_test.reset_index(drop=True)

        if isinstance(model, RidgeReturnModel):
            model.fit(X_train, y_dir, y_ret)
        else:
            model.fit(X_train, y_dir)

        sigs = model.predict_signals(X_test, meta_test, horizon=horizon)
        all_signals.extend(sigs)

    sig_df = signals_to_dataframe(all_signals)
    if sig_df.empty:
        metrics = pd.DataFrame(
            [
                {
                    "model": model.name,
                    "pair": pair,
                    "horizon": horizon,
                    **_score_returns(pd.Series(dtype=float)),
                }
            ]
        )
        return sig_df, metrics

    rets = _strategy_returns(sig_df, pair_df, horizon)
    metrics = pd.DataFrame(
        [
            {
                "model": model.name,
                "pair": pair,
                "horizon": horizon,
                **_score_returns(rets),
            }
        ]
    )
    return sig_df, metrics


def run_model_comparison(
    features: pd.DataFrame,
    pairs: Iterable[str] | None = None,
    horizon: int = 5,
    train_years: int = 5,
    test_years: int = 1,
    models: list[BaseFXModel] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compare all baseline models across pairs.

    Returns (all_signals, comparison_report).
    """
    pairs = list(pairs) if pairs else sorted(features["pair"].unique())
    models = models or get_baseline_models()
    metric_rows = []
    all_sigs = []

    for pair in pairs:
        for model in models:
            fresh = clone_baseline_model(model)
            sig_df, metrics = run_walk_forward_for_model(
                fresh, features, pair, horizon, train_years, test_years
            )
            if not sig_df.empty:
                all_sigs.append(sig_df)
            metric_rows.append(metrics)

    comparison = pd.concat(metric_rows, ignore_index=True) if metric_rows else pd.DataFrame()
    signals = pd.concat(all_sigs, ignore_index=True) if all_sigs else pd.DataFrame()
    return signals, comparison

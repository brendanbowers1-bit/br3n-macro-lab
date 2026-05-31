"""Risk metrics for walk-forward backtests."""

from __future__ import annotations

import numpy as np
import pandas as pd


def sharpe_ratio(returns: pd.Series, ann_factor: float = 252) -> float:
    r = returns.dropna()
    if r.std() == 0 or r.empty:
        return float("nan")
    return float(r.mean() / r.std() * np.sqrt(ann_factor))


def sortino_ratio(returns: pd.Series, ann_factor: float = 252) -> float:
    r = returns.dropna()
    downside = r[r < 0]
    if downside.std() == 0 or r.empty:
        return float("nan")
    return float(r.mean() / downside.std() * np.sqrt(ann_factor))


def max_drawdown(equity_curve: pd.Series) -> float:
    if equity_curve.empty:
        return float("nan")
    dd = equity_curve / equity_curve.cummax() - 1
    return float(dd.min())


def win_loss_stats(returns: pd.Series) -> dict:
    wins = returns[returns > 0]
    losses = returns[returns < 0]
    return {
        "win_rate": float((returns > 0).mean()) if len(returns) else float("nan"),
        "average_win": float(wins.mean()) if len(wins) else float("nan"),
        "average_loss": float(losses.mean()) if len(losses) else float("nan"),
        "profit_factor": float(wins.sum() / abs(losses.sum())) if len(losses) and losses.sum() != 0 else float("nan"),
    }


def classification_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict:
    from sklearn.metrics import accuracy_score, precision_score, recall_score

    yt = y_true.astype(int)
    yp = y_pred.astype(int)
    return {
        "accuracy": float(accuracy_score(yt, yp)),
        "precision": float(precision_score(yt, yp, zero_division=0)),
        "recall": float(recall_score(yt, yp, zero_division=0)),
    }

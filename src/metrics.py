"""Performance metrics for backtest scorecards."""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


def performance_metrics(
    returns: pd.Series,
    equity: pd.Series,
    ann_days: int = 252,
    label: str = "strategy",
) -> Dict[str, float]:
    r = returns.dropna()
    if r.empty:
        return {"strategy": label, "total_return_pct": 0.0, "sharpe": 0.0}
    years = len(r) / ann_days
    total_ret = equity.iloc[-1] - 1.0
    ann_ret = (1.0 + total_ret) ** (1.0 / max(years, 1e-9)) - 1.0
    ann_vol = float(r.std() * np.sqrt(ann_days))
    sharpe = float(r.mean() / (r.std() + 1e-12) * np.sqrt(ann_days))
    dd = equity / equity.cummax() - 1.0
    return {
        "strategy": label,
        "total_return_pct": round(total_ret * 100, 2),
        "ann_return_pct": round(ann_ret * 100, 2),
        "ann_vol_pct": round(ann_vol * 100, 2),
        "sharpe": round(sharpe, 3),
        "max_drawdown_pct": round(float(dd.min()) * 100, 2),
        "win_rate_pct": round(float((r > 0).mean()) * 100, 1),
    }

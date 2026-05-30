"""
Random-walk validity map by regime.

Tests when random-walk assumptions appear more or less plausible.
Metrics decide labels — no hardcoded regime conclusions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .regimes import ALL_REGIMES

ROOT = Path(__file__).resolve().parents[1]


def _autocorr(series: pd.Series, lag: int) -> float:
    s = series.dropna()
    if len(s) < lag + 5:
        return float("nan")
    return float(s.autocorr(lag=lag))


def _validity_label(avg_ret: float, ac1: float, pct_pos: float, vol: float) -> str:
    drift_small = abs(avg_ret) < 0.0003
    ac_near_zero = np.isnan(ac1) or abs(ac1) < 0.05
    balanced = 0.45 <= pct_pos <= 0.55

    if drift_small and ac_near_zero and balanced:
        return "Random-walk-like"
    if (not drift_small or (not ac_near_zero and not np.isnan(ac1))) and vol < 15:
        return "Potential structure"
    if vol >= 12 and (drift_small or ac_near_zero):
        return "High-risk noise"
    if not drift_small or not ac_near_zero:
        return "Potential structure"
    return "High-risk noise"


def _interpretation(label: str) -> str:
    return {
        "Random-walk-like": "Directional metrics near random-walk benchmarks; static hedge may dominate.",
        "Potential structure": "Some trend or autocorrelation — conditional models may warrant testing OOS.",
        "High-risk noise": "Elevated vol with weak direction — avoid over-adjusting hedge ratios.",
    }.get(label, "Review regime metrics manually.")


def build_random_walk_validity_map(
    df: pd.DataFrame,
    corridor_id: Optional[str] = None,
) -> pd.DataFrame:
    """Compute regime-specific random-walk validity statistics."""
    rows = []
    ann = np.sqrt(252)

    for regime in ALL_REGIMES:
        sub = df[df["regime"] == regime]
        if sub.empty:
            continue
        rets = sub["daily_return"].dropna()
        n = len(rets)
        avg = float(rets.mean())
        vol = float(rets.std() * ann * 100)
        pct_pos = float((rets > 0).mean())
        ac1 = _autocorr(rets, 1)
        ac5 = _autocorr(rets, 5)
        bias = "positive" if avg > 0 else "negative" if avg < 0 else "neutral"
        label = _validity_label(avg, ac1, pct_pos, vol)

        rows.append(
            {
                "corridor_id": corridor_id,
                "regime": regime,
                "observations": n,
                "average_daily_return": round(avg, 6),
                "annualized_volatility": round(vol, 3),
                "directional_bias": bias,
                "autocorrelation_1d": round(ac1, 4) if not np.isnan(ac1) else None,
                "autocorrelation_5d": round(ac5, 4) if not np.isnan(ac5) else None,
                "percent_positive_days": round(pct_pos * 100, 2),
                "random_walk_validity_label": label,
                "interpretation": _interpretation(label),
            }
        )

    return pd.DataFrame(rows)


def save_validity_map(
    validity_df: pd.DataFrame,
    out_dir: Optional[Path] = None,
    filename: str = "random_walk_validity_map.csv",
) -> Path:
    out_dir = out_dir or ROOT / "data" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    validity_df.to_csv(path, index=False)
    return path

"""
R1 vs R2 trend quality comparison.

Research question: Are high-volatility trends (R1) liquidation/stress rather than
information-rich structure like R2?

Research-only — not investment advice.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .regimes import R1, R2

ROOT = Path(__file__).resolve().parents[1]


def _max_drawdown(returns: pd.Series) -> float:
    if returns.empty:
        return float("nan")
    cum = (1.0 + returns.fillna(0)).cumprod()
    peak = cum.cummax()
    dd = (cum / peak - 1.0).min()
    return float(dd * 100)


def _continuation_rate(sub: pd.DataFrame) -> float:
    """Share of days where return sign matches trend direction."""
    if sub.empty or "trend_direction" not in sub.columns:
        return float("nan")
    aligned = np.sign(sub["daily_return"]) == sub["trend_direction"]
    valid = sub["daily_return"].notna()
    if valid.sum() == 0:
        return float("nan")
    return float(aligned[valid].mean())


def _reversal_rate(sub: pd.DataFrame, window: int = 5) -> float:
    """Share of rolling windows where cumulative return flips sign vs prior window."""
    rets = sub["daily_return"].dropna()
    if len(rets) < window * 2:
        return float("nan")
    roll = rets.rolling(window).sum()
    flips = (np.sign(roll) != np.sign(roll.shift(window))).sum()
    return float(flips / max(len(roll.dropna()) - window, 1))


def _mean_optional(sub: pd.DataFrame, col: str) -> Optional[float]:
    if col not in sub.columns or sub[col].isna().all():
        return None
    return round(float(sub[col].mean()), 4)


def _regime_metrics(df: pd.DataFrame, regime: str) -> dict:
    sub = df[df["regime"] == regime].copy()
    rets = sub["daily_return"].dropna()
    ann = np.sqrt(252)
    n = len(sub)

    row = {
        "regime": regime,
        "sample": "full",
        "observations": n,
        "pct_of_sample": round(100.0 * n / len(df), 2) if len(df) else None,
        "annualized_volatility": round(float(rets.std() * ann * 100), 3) if len(rets) else None,
        "average_daily_return_bps": round(float(rets.mean()) * 10000, 2) if len(rets) else None,
        "continuation_probability": round(_continuation_rate(sub), 4) if n else None,
        "reversal_probability_5d": round(_reversal_rate(sub), 4) if n else None,
        "max_drawdown_pct": round(_max_drawdown(rets), 3) if len(rets) else None,
        "autocorrelation_1d": round(float(rets.autocorr(lag=1)), 4) if len(rets) > 5 else None,
        "avg_news_stress": _mean_optional(sub, "news_stress_zscore"),
        "avg_policy_uncertainty": _mean_optional(sub, "policy_uncertainty_index"),
        "carry_fragility_rate": round(float(sub["carry_fragility_regime"].mean()), 4)
        if "carry_fragility_regime" in sub.columns and n
        else None,
        "high_news_stress_rate": round(float(sub["high_news_stress"].mean()), 4)
        if "high_news_stress" in sub.columns and n
        else None,
        "dollar_stress_rate": round(float(sub["dollar_stress"].mean()), 4)
        if "dollar_stress" in sub.columns and n
        else None,
        "flow_window_rate": round(float(sub["flow_pressure_window"].mean()), 4)
        if "flow_pressure_window" in sub.columns and n
        else None,
    }

    if regime == R1:
        row["interpretation"] = (
            "High-volatility trend — often stress, liquidation, or unstable momentum; "
            "use caution rather than trend-following."
        )
    elif regime == R2:
        row["interpretation"] = (
            "Low-volatility trend — candidate information-diffusion regime; "
            "worth testing for structured hedge adjustment (OOS required)."
        )
    else:
        row["interpretation"] = "Review regime metrics manually."

    return row


def build_r1_r2_trend_quality(df: pd.DataFrame, corridor_id: Optional[str] = None) -> pd.DataFrame:
    """Compare R1 vs R2 trend quality metrics."""
    work = df.copy()
    if "date" in work.columns:
        work = work.set_index("date")
    work.index = pd.to_datetime(work.index)

    rows = [_regime_metrics(work, R1), _regime_metrics(work, R2)]
    out = pd.DataFrame(rows)
    if corridor_id:
        out.insert(0, "corridor_id", corridor_id)
    return out


def save_r1_r2_trend_quality(
    comparison: pd.DataFrame,
    out_dir: Optional[Path] = None,
    filename: str = "r1_r2_trend_quality_comparison.csv",
) -> Path:
    out_dir = out_dir or ROOT / "data" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    comparison.to_csv(path, index=False)
    return path


def build_r1_r2_trend_quality_oos(
    df: pd.DataFrame,
    splits: list[dict],
    corridor_id: Optional[str] = None,
) -> pd.DataFrame:
    """R1 vs R2 metrics on OOS test windows only (pre-registered splits)."""
    work = df.copy()
    if "date" in work.columns:
        work = work.set_index("date")
    work.index = pd.to_datetime(work.index)

    rows: list[dict] = []
    for split in splits:
        test_start = split["test_start"]
        test_end = split["test_end"]
        name = split.get("name", f"{test_start}_{test_end}")
        test = work.loc[(work.index >= test_start) & (work.index <= test_end)]
        if len(test) < 20:
            continue
        for regime in (R1, R2):
            m = _regime_metrics(test, regime)
            m["split"] = name
            m["sample"] = "oos_test"
            m["test_period"] = f"{test_start}..{test_end}"
            rows.append(m)

    out = pd.DataFrame(rows)
    if corridor_id and not out.empty:
        out.insert(0, "corridor_id", corridor_id)
    return out

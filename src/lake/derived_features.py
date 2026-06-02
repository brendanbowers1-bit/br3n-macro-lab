"""Derived FX and corridor feature helpers for canonical USD/MXN table."""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_fx_features(spot: pd.Series) -> pd.DataFrame:
    """1d/5d returns, 20d vol, and volatility regime from USD/MXN spot."""
    spot = pd.to_numeric(spot, errors="coerce")
    ret_1d = spot.pct_change()
    ret_5d = spot.pct_change(5)
    vol_20d = ret_1d.rolling(20, min_periods=10).std() * np.sqrt(252)

    regime = pd.Series("unknown", index=spot.index, dtype="object")
    valid_vol = vol_20d.dropna()
    if len(valid_vol) >= 20:
        low = valid_vol.quantile(0.33)
        high = valid_vol.quantile(0.67)
        regime = np.where(vol_20d <= low, "low", np.where(vol_20d >= high, "high", "medium"))
        regime = pd.Series(regime, index=spot.index)
        regime[vol_20d.isna()] = "unknown"

    return pd.DataFrame(
        {
            "usd_return_1d": ret_1d,
            "usd_return_5d": ret_5d,
            "volatility_20d": vol_20d,
            "volatility_regime": regime,
        }
    )


def compute_spread_proxy_bps(fx_margin_pct: pd.Series) -> pd.Series:
    """Convert RPW FX margin percent to basis-point spread proxy."""
    return pd.to_numeric(fx_margin_pct, errors="coerce") * 10_000


def compute_liquidity_proxy(vol_20d: pd.Series, spread_bps: pd.Series) -> pd.Series:
    """Higher vol and spread → lower liquidity proxy (0–1 scale)."""
    vol = pd.to_numeric(vol_20d, errors="coerce")
    spread = pd.to_numeric(spread_bps, errors="coerce")
    vol_rank = vol.rank(pct=True)
    spread_rank = spread.rank(pct=True)
    stress = (vol_rank.fillna(0.5) + spread_rank.fillna(0.5)) / 2
    return (1 - stress).clip(0, 1)


def apply_flag_series(dates: pd.DatetimeIndex, flag_dates: pd.Series) -> np.ndarray:
    if flag_dates.empty:
        return np.zeros(len(dates), dtype=bool)
    flagged = set(pd.to_datetime(flag_dates).dt.normalize())
    return np.array([d.normalize() in flagged for d in dates], dtype=bool)

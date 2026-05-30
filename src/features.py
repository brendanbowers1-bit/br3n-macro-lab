"""Feature engineering: returns, MAs, volatility, flags."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_features(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    fc = cfg["features"]
    out = df.copy()
    out["daily_return"] = out["price"].pct_change()
    out["fwd_return_1d"] = out["price"].pct_change().shift(-1)
    out["fwd_return_5d"] = out["price"].pct_change(5).shift(-5)

    out["ma20"] = out["price"].rolling(fc["ma_short"]).mean()
    out["ma60"] = out["price"].rolling(fc["ma_long"]).mean()
    out["ma_spread"] = out["ma20"] - out["ma60"]
    out["ma_spread_pct"] = out["ma20"] / out["ma60"] - 1.0

    out["realized_vol_20d"] = (
        out["daily_return"].rolling(fc["realized_vol_window"]).std() * np.sqrt(252)
    )
    win = fc.get("vol_percentile_window", 252)
    out["realized_vol_percentile"] = out["realized_vol_20d"].rolling(win, min_periods=60).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
    )
    thresh = fc["vol_percentile_threshold"]
    out["high_vol_flag"] = out["realized_vol_percentile"] > thresh
    out["low_vol_flag"] = ~out["high_vol_flag"]

    trend_thr = cfg["regimes"]["trend_threshold"]
    if cfg["regimes"].get("use_absolute_ma_spread", True):
        out["trend_flag"] = (out["ma_spread_pct"].abs() > trend_thr).astype(int)
    else:
        out["trend_flag"] = (out["ma_spread_pct"] > trend_thr).astype(int) | (
            out["ma_spread_pct"] < -trend_thr
        ).astype(int)
    out["trend_direction"] = np.where(out["ma20"] > out["ma60"], 1, -1)
    return out.dropna()

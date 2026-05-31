"""
FX terminal feature engineering — no look-ahead bias.

All features use information available as of each date; targets are forward-shifted.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "ret_1d",
    "ret_5d",
    "ret_10d",
    "ret_20d",
    "ret_60d",
    "ma20",
    "ma60",
    "dist_ma20",
    "dist_ma60",
    "vol_10d",
    "vol_20d",
    "vol_60d",
    "drawdown_60d",
    "price_zscore_60d",
    "domestic_policy_rate",
    "foreign_policy_rate",
    "rate_differential",
    "yield_2y_diff",
    "yield_10y_diff",
    "yield_curve_slope_diff",
    "carry_score",
    "vix_change",
    "sp500_return",
    "dxy_trend_20d",
    "em_proxy_return",
    "oil_return",
    "cpi_surprise",
    "growth_surprise",
    "central_bank_tone_score",
    "current_account_score",
    "political_risk_score",
]

TARGET_COLUMNS = [
    "forward_return_5d",
    "forward_return_10d",
    "forward_return_20d",
    "direction_5d",
    "direction_10d",
    "direction_20d",
]


def _rolling_zscore(s: pd.Series, window: int) -> pd.Series:
    mu = s.rolling(window, min_periods=max(5, window // 3)).mean()
    sd = s.rolling(window, min_periods=max(5, window // 3)).std()
    return (s - mu) / sd.replace(0, np.nan)


def build_pair_features(
    spot: pd.DataFrame,
    macro: pd.DataFrame | None = None,
    rates: pd.DataFrame | None = None,
    sentiment: pd.DataFrame | None = None,
    pair: str | None = None,
) -> pd.DataFrame:
    """
    Build feature table for one pair.

    spot: index=date, column price (or reset with date column)
    """
    df = spot.copy()
    if "date" in df.columns:
        df = df.set_index("date")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    price = df["price"].astype(float)
    out = pd.DataFrame(index=df.index)
    out["pair"] = pair or df.get("pair", pd.Series("", index=df.index)).iloc[0]
    out["spot"] = price

    out["ret_1d"] = price.pct_change(1)
    out["ret_5d"] = price.pct_change(5)
    out["ret_10d"] = price.pct_change(10)
    out["ret_20d"] = price.pct_change(20)
    out["ret_60d"] = price.pct_change(60)

    out["ma20"] = price.rolling(20, min_periods=10).mean()
    out["ma60"] = price.rolling(60, min_periods=20).mean()
    out["dist_ma20"] = price / out["ma20"] - 1.0
    out["dist_ma60"] = price / out["ma60"] - 1.0

    out["vol_10d"] = out["ret_1d"].rolling(10, min_periods=5).std() * np.sqrt(252)
    out["vol_20d"] = out["ret_1d"].rolling(20, min_periods=10).std() * np.sqrt(252)
    out["vol_60d"] = out["ret_1d"].rolling(60, min_periods=20).std() * np.sqrt(252)

    roll_max = price.rolling(60, min_periods=20).max()
    out["drawdown_60d"] = price / roll_max - 1.0
    out["price_zscore_60d"] = _rolling_zscore(price, 60)

    # Targets — forward only (no look-ahead in features)
    out["forward_return_5d"] = price.pct_change(5).shift(-5)
    out["forward_return_10d"] = price.pct_change(10).shift(-10)
    out["forward_return_20d"] = price.pct_change(20).shift(-20)
    out["direction_5d"] = (out["forward_return_5d"] > 0).astype(int)
    out["direction_10d"] = (out["forward_return_10d"] > 0).astype(int)
    out["direction_20d"] = (out["forward_return_20d"] > 0).astype(int)

    if macro is not None and not macro.empty:
        m = macro.copy()
        m["date"] = pd.to_datetime(m["date"])
        m = m.sort_values("date").drop_duplicates("date")
        m_idx = m.set_index("date")
        merged = out.join(m_idx, how="left")
        if "vix" in merged.columns:
            merged["vix_change"] = merged["vix"].pct_change()
        if "sp500_return" not in merged.columns and "sp500" in merged.columns:
            merged["sp500_return"] = merged["sp500"].pct_change()
        if "dxy" in merged.columns:
            merged["dxy_trend_20d"] = merged["dxy"].pct_change(20)
        if "em_proxy" in merged.columns:
            merged["em_proxy_return"] = merged["em_proxy"].pct_change()
        if "oil" in merged.columns:
            merged["oil_return"] = merged["oil"].pct_change()
        if "us_2y" in merged.columns and "us_10y" in merged.columns:
            merged["yield_2y_diff"] = merged["us_2y"]
            merged["yield_10y_diff"] = merged["us_10y"]
            merged["yield_curve_slope_diff"] = merged["us_10y"] - merged["us_2y"]
        out = merged

    if rates is not None and not rates.empty:
        r = rates.copy()
        r["date"] = pd.to_datetime(r["date"])
        if pair:
            r = r[r["pair"] == pair]
        r = r.sort_values("date").drop_duplicates("date").set_index("date")
        for col in ("domestic_policy_rate", "foreign_policy_rate", "rate_differential", "carry_score"):
            if col in r.columns:
                out[col] = r[col].reindex(out.index).ffill()

    if sentiment is not None and not sentiment.empty:
        s = sentiment.copy()
        s["date"] = pd.to_datetime(s["date"])
        s = s.sort_values("date").drop_duplicates("date").set_index("date")
        for col in (
            "cpi_surprise",
            "growth_surprise",
            "central_bank_tone_score",
            "current_account_score",
            "political_risk_score",
        ):
            if col in s.columns:
                out[col] = s[col].reindex(out.index).ffill()

    out = out.reset_index().rename(columns={"index": "date"})
    if "date" not in out.columns and out.index.name == "date":
        out = out.reset_index()

    # Fill placeholder columns
    for col in FEATURE_COLUMNS:
        if col not in out.columns:
            out[col] = 0.0

    return out


def build_multi_pair_feature_table(
    market: pd.DataFrame,
    macro: pd.DataFrame | None = None,
    rates: pd.DataFrame | None = None,
    sentiment: pd.DataFrame | None = None,
    pairs: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Stacked feature table for all pairs."""
    pairs = list(pairs) if pairs else sorted(market["pair"].unique())
    frames = []
    for pair in pairs:
        sub = market[market["pair"] == pair][["date", "price"]].copy()
        if sub.empty:
            continue
        r_pair = rates[rates["pair"] == pair] if rates is not None and "pair" in rates.columns else rates
        feats = build_pair_features(sub, macro=macro, rates=r_pair, sentiment=sentiment, pair=pair)
        frames.append(feats)
    if not frames:
        return pd.DataFrame()
    table = pd.concat(frames, ignore_index=True)
    table["date"] = pd.to_datetime(table["date"])
    return table.sort_values(["pair", "date"]).reset_index(drop=True)


def get_model_matrix(
    df: pd.DataFrame,
    horizon: int = 5,
    feature_cols: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """
    Return X, y_direction, y_return for modeling.

    Drops rows with NaN targets or insufficient history.
    """
    feature_cols = feature_cols or FEATURE_COLUMNS
    direction_col = f"direction_{horizon}d"
    return_col = f"forward_return_{horizon}d"
    use = df.copy()
    use[feature_cols] = use[feature_cols].fillna(0)
    use = use.dropna(subset=[direction_col, return_col])
    X = use[feature_cols].astype(float)
    y_dir = use[direction_col].astype(int)
    y_ret = use[return_col].astype(float)
    return X, y_dir, y_ret

"""
Carry-aware models for FX Lab model zoo.

Carry is a regime/risk feature — not a magic trading signal.
Policy-rate carry is a proxy; forward points required for true hedge economics.
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np
import pandas as pd

from .carry_features import carry_data_available
from .model_zoo import (
    OUTPUT_COLS,
    _build_output,
    _build_output_with_position,
    _zero_series,
    normalize_signal,
)
from .regimes import R1, R2, R3, R4, RANGE_REGIMES, TREND_REGIMES


def _carry_favor(df: pd.DataFrame) -> pd.Series:
    """True when foreign currency has yield advantage (high carry for MXN vs USD)."""
    if "is_high_carry" in df.columns:
        return df["is_high_carry"].astype(bool)
    if "carry_proxy" in df.columns and df["carry_proxy"].notna().any():
        med = df["carry_proxy"].median()
        return df["carry_proxy"] > med
    if "mx_rate" in df.columns and "us_rate" in df.columns:
        return (df["mx_rate"] - df["us_rate"]) > (df["mx_rate"] - df["us_rate"]).median()
    raise ValueError("missing_carry_data")


def _low_vol(df: pd.DataFrame, cfg: dict) -> pd.Series:
    thresh = float(cfg.get("features", {}).get("vol_percentile_threshold", 0.60))
    if "realized_vol_percentile" in df.columns:
        return df["realized_vol_percentile"] < thresh
    if "high_vol_flag" in df.columns:
        return ~df["high_vol_flag"].astype(bool)
    return pd.Series(True, index=df.index)


def carry_proxy_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """
    Favor high-yield currency when vol is low; flatten when vol high.

    USD/MXN: high MXN carry → short USD/MXN (signal -1) when favoring MXN carry position.
    Research framing: carry as regime feature, not guaranteed alpha.
    """
    if not carry_data_available(df):
        raise ValueError("missing_carry_data")

    carry_favor = _carry_favor(df)
    low_vol = _low_vol(df, cfg)
    sig = _zero_series(df).astype(int)
    # High MXN carry + low vol: favor MXN (short USD/MXN for long-MXN carry holder lens → signal -1 for pair)
    # Lab convention: +1 = long USD/MXN; high MXN carry means MXN yield — short pair to hold MXN vs USD
    sig.loc[low_vol & carry_favor] = -1
    sig.loc[~low_vol] = 0
    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "carry_proxy_model", "hybrid", sig, fc_ret)


def carry_regime_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """
    Trade carry only in R2/R4 stable regimes; flat during fragility or R1/R3.
    """
    if not carry_data_available(df):
        raise ValueError("missing_carry_data")

    carry_favor = _carry_favor(df)
    fragile = df.get("carry_fragility_regime", pd.Series(False, index=df.index)).astype(bool)
    stable_carry = df["regime"].isin([R2, R4]) | df["regime"].astype(str).str.match(r"R[24]_", na=False)
    avoid = df["regime"].isin([R1, R3]) | df["regime"].astype(str).str.match(r"R[13]_", na=False)

    sig = _zero_series(df).astype(int)
    sig.loc[stable_carry & carry_favor & ~fragile] = -1
    sig.loc[avoid | fragile] = 0
    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "carry_regime_model", "hybrid", sig, fc_ret)


def carry_fragility_risk_off_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """
    High carry + fragility → risk-off / reduce carry exposure (hedge framing).
    """
    if not carry_data_available(df):
        raise ValueError("missing_carry_data")

    fragile = df.get("carry_fragility_regime", pd.Series(False, index=df.index)).astype(bool)
    sig = _zero_series(df).astype(int)
    sig.loc[fragile] = 0
    hr = pd.Series(0.50, index=df.index)
    hr.loc[fragile] = 0.80
    return _build_output(df, "carry_fragility_risk_off_model", "hedge_governance", sig, hedge_ratio=hr)


def r2_carry_confirmed_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """
    R2 trend only when carry supports direction.

    USD/MXN: MA20 < MA60 + high MXN carry → short USD/MXN (-1).
    Trend against carry → flat or reduced.
    """
    if not carry_data_available(df):
        raise ValueError("missing_carry_data")

    carry_favor = _carry_favor(df)
    in_r2 = (df["regime"] == R2) | df["regime"].astype(str).str.contains("R2", na=False)
    sig = _zero_series(df).astype(int)

    down_trend = df["ma20"] < df["ma60"]
    up_trend = df["ma20"] > df["ma60"]

    sig.loc[in_r2 & down_trend & carry_favor] = -1
    sig.loc[in_r2 & up_trend & carry_favor] = 0
    sig.loc[in_r2 & up_trend & ~carry_favor] = 1
    sig.loc[in_r2 & down_trend & ~carry_favor] = 0

    mag = df["daily_return"].rolling(60, min_periods=20).mean().shift(1).fillna(0.0)
    fc_ret = sig.astype(float) * mag
    return _build_output(df, "r2_carry_confirmed_model", "hybrid", sig, fc_ret)


def carry_adjusted_hedge_model(df: pd.DataFrame, cfg: dict, **kwargs: Any) -> pd.DataFrame:
    """
    Hedge-governance: carry and fragility adjust target hedge ratios.
    """
    if not carry_data_available(df):
        raise ValueError("missing_carry_data")

    hg = cfg.get("hedge_governance", {})
    max_step = float(hg.get("max_daily_hedge_adjustment", 0.10))
    targets = {R1: 0.75, R2: 0.65, R3: 0.35, R4: 0.30}
    norm_map = {
        "R1_trend_highvol": R1,
        "R2_trend_lowvol": R2,
        "R3_range_highvol": R3,
        "R4_range_lowvol": R4,
    }

    ratios = []
    prev = 0.50
    for i, regime in enumerate(df["regime"]):
        r = norm_map.get(regime, regime)
        target = targets.get(r, 0.50)
        row = df.iloc[i]
        fragile = bool(row.get("carry_fragility_regime", False))
        high_carry = bool(row.get("is_high_carry", False))
        expensive_carry = high_carry and not fragile

        if fragile:
            target = min(0.90, target + 0.15)
        elif r in (R3, R4) and expensive_carry:
            target = prev
        elif r == R2 and high_carry and not fragile:
            target = 0.60

        delta = float(np.clip(target - prev, -max_step, max_step))
        prev = float(np.clip(prev + delta, 0.0, 1.0))
        ratios.append(prev)

    hr = pd.Series(ratios, index=df.index)
    sig = _zero_series(df).astype(int)
    return _build_output(df, "carry_adjusted_hedge_model", "hedge_governance", sig, hedge_ratio=hr)


CARRY_MODEL_REGISTRY = {
    "carry_proxy_model": {
        "func": carry_proxy_model,
        "required_columns": ["daily_return"],
        "optional_any": ["carry_proxy", "is_high_carry", "mx_rate"],
    },
    "carry_regime_model": {
        "func": carry_regime_model,
        "required_columns": ["regime", "daily_return"],
        "optional_any": ["carry_proxy", "is_high_carry", "carry_fragility_regime"],
    },
    "carry_fragility_risk_off_model": {
        "func": carry_fragility_risk_off_model,
        "required_columns": ["daily_return"],
        "optional_any": ["carry_fragility_regime", "carry_proxy"],
    },
    "r2_carry_confirmed_model": {
        "func": r2_carry_confirmed_model,
        "required_columns": ["regime", "ma20", "ma60", "daily_return"],
        "optional_any": ["carry_proxy", "is_high_carry"],
    },
    "carry_adjusted_hedge_model": {
        "func": carry_adjusted_hedge_model,
        "required_columns": ["regime"],
        "optional_any": ["carry_proxy", "is_high_carry", "carry_fragility_regime"],
    },
}

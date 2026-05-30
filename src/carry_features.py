"""
Interest-rate carry features for FX regime research.

Carry is a regime/risk/hedge-cost feature — not a magic trading signal.
Policy-rate differentials are proxies; forward points are required for true hedge economics.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .regimes import R1, R2, R3, R4

logger = logging.getLogger(__name__)

CARRY_PLACEHOLDER_COLUMNS = [
    "domestic_policy_rate",
    "foreign_policy_rate",
    "carry_proxy",
    "carry_proxy_annualized",
    "carry_zscore",
    "carry_percentile",
    "is_high_carry",
    "is_low_carry",
    "carry_change_20d",
    "carry_compression",
    "carry_widening",
    "carry_fragility_regime",
    "carry_adjusted_regime",
]


def add_carry_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    """Add carry columns as NaN/False when no rate data exists."""
    out = df.copy()
    for col in CARRY_PLACEHOLDER_COLUMNS:
        if col in out.columns:
            continue
        if col.startswith("is_") or col.endswith("_regime"):
            out[col] = False if col != "carry_adjusted_regime" else "no_carry_data"
        else:
            out[col] = np.nan
    if "carry_adjusted_regime" in out.columns:
        out.loc[out["carry_adjusted_regime"].isna(), "carry_adjusted_regime"] = "no_carry_data"
    return out


def load_fred_rate_series(series_id: str, feature_name: str) -> pd.DataFrame:
    """
    Load FRED rate series via public graph CSV (no API key required).

    Returns: date, {feature_name}
    """
    from .macro_loader import fetch_fred_series

    s = fetch_fred_series(series_id)
    out = pd.DataFrame({feature_name: s}).dropna()
    out.index.name = "date"
    return out.reset_index()


def merge_rate_series(
    market_df: pd.DataFrame,
    domestic_rates: Optional[pd.DataFrame] = None,
    foreign_rates: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Merge policy rates onto market data by date.

    WARNING: Forward-fill rates for lower-frequency series. Use only for
    published/lagged policy rates — not for unreleased future rate data.
    """
    out = market_df.copy()
    if "date" not in out.columns:
        out = out.reset_index()
    out["date"] = pd.to_datetime(out["date"])
    out = out.sort_values("date")

    for rates, col in ((domestic_rates, "domestic_policy_rate"), (foreign_rates, "foreign_policy_rate")):
        if rates is None or rates.empty:
            continue
        rd = rates.copy()
        if "date" not in rd.columns:
            rd = rd.reset_index()
        rd["date"] = pd.to_datetime(rd["date"])
        rd = rd.sort_values("date").drop_duplicates("date", keep="last")
        val_col = [c for c in rd.columns if c != "date"][0]
        rd = rd.rename(columns={val_col: col})
        out = pd.merge_asof(out, rd[["date", col]], on="date", direction="backward")
        out[col] = out[col].ffill()

    return out


def compute_carry_proxy(
    df: pd.DataFrame,
    domestic_col: str = "domestic_policy_rate",
    foreign_col: str = "foreign_policy_rate",
) -> pd.DataFrame:
    """
    carry_proxy = foreign_policy_rate - domestic_policy_rate (USD/foreign pair).

    For USD/MXN: Mexico rate minus U.S. rate.

    This is a simplified proxy — not executable forward points.
    """
    out = df.copy()
    if domestic_col not in out.columns or foreign_col not in out.columns:
        return out
    out["carry_proxy"] = out[foreign_col] - out[domestic_col]
    out["carry_proxy_annualized"] = out["carry_proxy"]
    return out


def _has_carry_data(df: pd.DataFrame) -> bool:
    if "carry_proxy" in df.columns and df["carry_proxy"].notna().any():
        return True
    if "mx_rate" in df.columns and "us_rate" in df.columns:
        return df["mx_rate"].notna().any() and df["us_rate"].notna().any()
    return False


def _ensure_rate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map legacy mx_rate/us_rate to domestic/foreign if needed."""
    out = df.copy()
    if "domestic_policy_rate" not in out.columns and "us_rate" in out.columns:
        out["domestic_policy_rate"] = out["us_rate"]
    if "foreign_policy_rate" not in out.columns and "mx_rate" in out.columns:
        out["foreign_policy_rate"] = out["mx_rate"]
    return compute_carry_proxy(out)


def add_carry_features(df: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, dict]:
    """
    Master function: compute carry features or add placeholders.

    Returns (dataframe, status_dict).
    """
    carry_cfg = config.get("carry", {})
    status: Dict[str, Any] = {
        "enabled": carry_cfg.get("enabled", False),
        "carry_data_available": False,
        "placeholders_only": False,
        "domestic_rate_source": None,
        "foreign_rate_source": None,
        "errors": [],
    }

    if not carry_cfg.get("enabled", True):
        return add_carry_placeholders(df), status

    out = df.copy()
    if "date" not in out.columns:
        out = out.reset_index()
    out["date"] = pd.to_datetime(out["date"])

    domestic_series = carry_cfg.get("domestic_rate_series", "FEDFUNDS")
    foreign_series = carry_cfg.get("foreign_rate_series")
    if not foreign_series:
        foreign_series = config.get("macro", {}).get("fred", {}).get("mx_rate", "INTGSBMXM193N")

    domestic_df = None
    foreign_df = None

    if carry_cfg.get("use_policy_rate_proxy", True):
        if "domestic_policy_rate" not in out.columns or out["domestic_policy_rate"].isna().all():
            try:
                domestic_df = load_fred_rate_series(domestic_series, "domestic_policy_rate")
                status["domestic_rate_source"] = f"FRED:{domestic_series}"
            except Exception as exc:
                status["errors"].append(f"domestic rate: {exc}")
        else:
            status["domestic_rate_source"] = "existing_column"

        if "foreign_policy_rate" not in out.columns or out["foreign_policy_rate"].isna().all():
            if foreign_series:
                try:
                    foreign_df = load_fred_rate_series(foreign_series, "foreign_policy_rate")
                    status["foreign_rate_source"] = f"FRED:{foreign_series}"
                except Exception as exc:
                    status["errors"].append(f"foreign rate: {exc}")
        else:
            status["foreign_rate_source"] = "existing_column"

    out = merge_rate_series(out, domestic_df, foreign_df)
    out = _ensure_rate_columns(out)

    if not _has_carry_data(out):
        out = add_carry_placeholders(out)
        status["placeholders_only"] = True
        return out, status

    status["carry_data_available"] = True
    z_window = int(carry_cfg.get("carry_zscore_window", 252))
    high_pct = float(carry_cfg.get("high_carry_percentile", 0.75))
    comp_thresh = float(carry_cfg.get("carry_compression_threshold", -0.25))

    cp = out["carry_proxy"]
    roll = cp.rolling(z_window, min_periods=max(20, z_window // 4))
    out["carry_zscore"] = ((cp - roll.mean()) / roll.std().replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
    out["carry_percentile"] = cp.rolling(z_window, min_periods=max(20, z_window // 4)).apply(
        lambda x: float(pd.Series(x).rank(pct=True).iloc[-1]) if len(x) else np.nan,
        raw=False,
    )
    out["is_high_carry"] = out["carry_percentile"] >= high_pct
    out["is_low_carry"] = out["carry_percentile"] <= (1.0 - high_pct)
    out["carry_change_20d"] = cp.diff(20)
    out["carry_compression"] = out["carry_change_20d"] < comp_thresh
    out["carry_widening"] = out["carry_change_20d"] > abs(comp_thresh)

    out = build_carry_fragility_regime(out, config)
    out = build_carry_adjusted_regime(out)

    return out, status


def build_carry_fragility_regime(df: pd.DataFrame, config: Optional[dict] = None) -> pd.DataFrame:
    """
    carry_fragility_regime = high carry + (high vol OR news stress OR dollar stress).

    Carry fragility means carry may be crowded or vulnerable — not a trading signal.
    """
    cfg = config or {}
    carry_cfg = cfg.get("carry", {})
    vol_pct = float(carry_cfg.get("carry_fragility_vol_percentile", 0.75))

    out = df.copy()
    high_carry = out.get("is_high_carry", pd.Series(False, index=out.index)).astype(bool)
    fragility = pd.Series(False, index=out.index)

    if "realized_vol_percentile" in out.columns:
        fragility = fragility | (out["realized_vol_percentile"] >= vol_pct)
    elif "high_vol_flag" in out.columns:
        fragility = fragility | out["high_vol_flag"].astype(bool)

    if "news_stress_regime" in out.columns:
        fragility = fragility | out["news_stress_regime"].astype(bool)

    for col in ("dollar_stress", "risk_off"):
        if col in out.columns:
            fragility = fragility | out[col].astype(bool)

    out["carry_fragility_regime"] = high_carry & fragility
    return out


def build_carry_adjusted_regime(df: pd.DataFrame) -> pd.DataFrame:
    """Combine spot regime with carry state into interpretable labels."""
    out = df.copy()
    labels: List[str] = []

    regime_aliases = {
        "R1_trend_highvol": R1,
        "R2_trend_lowvol": R2,
        "R3_range_highvol": R3,
        "R4_range_lowvol": R4,
    }

    for idx, row in out.iterrows():
        raw = str(row.get("regime", ""))
        regime = regime_aliases.get(raw, raw)
        if pd.isna(row.get("carry_proxy")):
            labels.append("no_carry_data")
            continue

        high = bool(row.get("is_high_carry", False))
        fragile = bool(row.get("carry_fragility_regime", False))
        low = bool(row.get("is_low_carry", False))

        if regime == R2 and high and not fragile:
            labels.append("R2_high_carry_stable")
        elif regime == R2 and high and fragile:
            labels.append("R2_high_carry_fragile")
        elif regime == R1 and high and fragile:
            labels.append("R1_high_carry_stress")
        elif regime in (R3, R4) and low:
            labels.append("R4_low_carry_noise")
        elif regime == R2 and not high:
            labels.append("R2_low_carry")
        else:
            labels.append(f"{regime}_carry_neutral")

    out["carry_adjusted_regime"] = labels
    return out


def carry_data_available(df: pd.DataFrame) -> bool:
    """True if carry_proxy or rate spread columns have usable data."""
    return _has_carry_data(df)

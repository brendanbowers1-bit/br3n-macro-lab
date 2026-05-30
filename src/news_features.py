"""
News and uncertainty features for FX regime research.

News is a regime/risk modifier — not a direct price prediction engine.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

NEWS_PLACEHOLDER_COLUMNS = [
    "news_intensity_1d",
    "news_intensity_7d",
    "news_intensity_zscore",
    "policy_uncertainty_index",
    "geopolitical_risk_index",
    "central_bank_news_flag",
    "inflation_news_flag",
    "election_news_flag",
    "commodity_news_flag",
    "country_specific_news_flag",
    "news_stress_regime",
]


def add_static_news_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add placeholder news columns when no live news data is available.

    Numeric columns → NaN; boolean flags → False; news_stress_regime → False.
    """
    out = df.copy()
    for col in NEWS_PLACEHOLDER_COLUMNS:
        if col in out.columns:
            continue
        if col.endswith("_flag") or col == "news_stress_regime":
            out[col] = False
        else:
            out[col] = np.nan
    return out


def load_fred_uncertainty_csv(series_id: str, feature_name: str) -> pd.DataFrame:
    """
    Load a FRED uncertainty series via public graph CSV (no API key required).

    Returns dataframe with columns: date, {feature_name}.
    """
    from .macro_loader import fetch_fred_series

    s = fetch_fred_series(series_id)
    out = pd.DataFrame({feature_name: s}).dropna()
    out.index.name = "date"
    return out.reset_index()


def merge_news_features(
    market_df: pd.DataFrame,
    news_df_list: List[pd.DataFrame],
    *,
    forward_fill: bool = True,
) -> pd.DataFrame:
    """
    Merge news feature frames onto market data by date.

    WARNING: Forward-fill is only for lower-frequency indices published with lag.
    Do not use forward-fill on same-day news that would not have been known at close.
    Prefer merge_asof with direction='backward' for point-in-time safety.
    """
    out = market_df.copy()
    if "date" not in out.columns:
        out = out.reset_index()
    out["date"] = pd.to_datetime(out["date"])
    out = out.sort_values("date")

    for news_df in news_df_list:
        if news_df is None or news_df.empty:
            continue
        nd = news_df.copy()
        if "date" not in nd.columns:
            nd = nd.reset_index()
        nd["date"] = pd.to_datetime(nd["date"])
        nd = nd.sort_values("date").drop_duplicates("date", keep="last")

        feat_cols = [c for c in nd.columns if c != "date"]
        merged = pd.merge_asof(
            out.sort_values("date"),
            nd.sort_values("date"),
            on="date",
            direction="backward",
        )
        out = merged
        if forward_fill:
            for c in feat_cols:
                if c in out.columns:
                    out[c] = out[c].ffill()

    if out.index.name == "date" or "date" in out.columns:
        pass
    return out


def build_news_stress_regime(df: pd.DataFrame, config: Optional[dict] = None) -> pd.DataFrame:
    """
    Classify news_stress_regime from intensity, uncertainty, and CB flags.

    True when any of:
    - news_intensity_zscore > threshold (default 2)
    - policy_uncertainty_index above rolling 80th percentile
    - geopolitical_risk_index above rolling 80th percentile
    - central_bank_news_flag during high-vol regime (realized_vol percentile >= 0.6)
    """
    cfg = config or {}
    news_cfg = cfg.get("news", {})
    z_thresh = float(news_cfg.get("stress_zscore_threshold", 2.0))
    roll_window = int(news_cfg.get("rolling_percentile_window", 252))
    vol_pct_thresh = float(cfg.get("features", {}).get("vol_percentile_threshold", 0.60))

    out = df.copy()
    stress = pd.Series(False, index=out.index)

    if "news_intensity_zscore" in out.columns:
        z = out["news_intensity_zscore"]
        stress = stress | (z > z_thresh)

    for col in ("policy_uncertainty_index", "geopolitical_risk_index"):
        if col in out.columns and out[col].notna().any():
            roll = out[col].rolling(roll_window, min_periods=max(20, roll_window // 4))
            p80 = roll.quantile(0.80)
            stress = stress | (out[col] > p80)

    if "central_bank_news_flag" in out.columns:
        cb = out["central_bank_news_flag"].astype(bool)
        if "realized_vol_percentile" in out.columns:
            high_vol = out["realized_vol_percentile"] >= vol_pct_thresh
            stress = stress | (cb & high_vol)
        else:
            stress = stress | cb

    out["news_stress_regime"] = stress.fillna(False)
    return out


def _compute_intensity_zscore(df: pd.DataFrame, col: str = "news_intensity_1d") -> pd.Series:
    if col not in df.columns or df[col].isna().all():
        return pd.Series(np.nan, index=df.index)
    roll = df[col].rolling(60, min_periods=20)
    mu = roll.mean()
    sd = roll.std().replace(0, np.nan)
    return ((df[col] - mu) / sd).replace([np.inf, -np.inf], np.nan)


def add_news_features(df: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, dict]:
    """
    Master function: load available news features or placeholders.

    Returns (enhanced_df, status_dict).
    """
    news_cfg = config.get("news", {})
    status: Dict[str, Any] = {
        "enabled": news_cfg.get("enabled", False),
        "fred_loaded": False,
        "gdelt_loaded": False,
        "placeholders_only": False,
        "features_added": [],
        "fred_series_loaded": [],
        "gdelt_columns": [],
        "errors": [],
    }

    if not news_cfg.get("enabled", True):
        return add_static_news_placeholders(df), status

    out = df.copy()
    if "date" not in out.columns:
        out = out.reset_index()
    out["date"] = pd.to_datetime(out["date"])

    news_frames: List[pd.DataFrame] = []

    if news_cfg.get("use_fred_uncertainty", True):
        fred_map = news_cfg.get("fred_series", {})
        for feat_name, series_id in fred_map.items():
            try:
                fdf = load_fred_uncertainty_csv(series_id, feat_name)
                if feat_name == "us_policy_uncertainty_daily":
                    fdf = fdf.rename(columns={feat_name: "policy_uncertainty_index"})
                news_frames.append(fdf)
                status["fred_loaded"] = True
                status["fred_series_loaded"].append(series_id)
                status["features_added"].append(
                    "policy_uncertainty_index" if feat_name == "us_policy_uncertainty_daily" else feat_name
                )
            except Exception as exc:
                status["errors"].append(f"FRED {series_id}: {exc}")
                logger.warning("FRED uncertainty load failed for %s: %s", series_id, exc)

    if news_cfg.get("use_gdelt", False):
        try:
            from .gdelt_news_loader import build_usdmxn_news_features

            start = str(out["date"].min().date())
            end = str(out["date"].max().date())
            gdf = build_usdmxn_news_features(start, end)
            if not gdf.empty:
                news_frames.append(gdf)
                status["gdelt_loaded"] = True
                status["gdelt_columns"] = [c for c in gdf.columns if c != "date"]
                status["features_added"].extend(status["gdelt_columns"])
            else:
                status["errors"].append("GDELT returned empty dataframe")
        except Exception as exc:
            status["errors"].append(f"GDELT: {exc}")
            logger.warning("GDELT load failed: %s", exc)

    if news_frames:
        out = merge_news_features(out, news_frames)
    elif news_cfg.get("use_placeholders_if_missing", True):
        out = add_static_news_placeholders(out)
        status["placeholders_only"] = True

    if "news_intensity_1d" not in out.columns or out["news_intensity_1d"].isna().all():
        if "total_usdmxn_news_intensity" in out.columns:
            out["news_intensity_1d"] = out["total_usdmxn_news_intensity"]
            out["news_intensity_7d"] = out["total_usdmxn_news_intensity"].rolling(7, min_periods=1).mean()
        elif "policy_uncertainty_index" in out.columns:
            out["news_intensity_1d"] = out["policy_uncertainty_index"]
            out["news_intensity_7d"] = out["policy_uncertainty_index"].rolling(7, min_periods=1).mean()

    if "news_intensity_7d" not in out.columns and "news_intensity_1d" in out.columns:
        out["news_intensity_7d"] = out["news_intensity_1d"].rolling(7, min_periods=1).mean()

    out["news_intensity_zscore"] = _compute_intensity_zscore(out)
    out = build_news_stress_regime(out, config)

    for col in NEWS_PLACEHOLDER_COLUMNS:
        if col not in out.columns:
            if col.endswith("_flag") or col == "news_stress_regime":
                out[col] = False
            else:
                out[col] = np.nan

    status["features_added"] = list(
        dict.fromkeys(status["features_added"] + [c for c in NEWS_PLACEHOLDER_COLUMNS if c in out.columns])
    )
    return out, status

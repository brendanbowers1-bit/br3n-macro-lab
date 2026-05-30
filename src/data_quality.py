"""
Data quality checks for FX price series.

Evaluates completeness, duplicates, and suspicious moves.
Does not imply prototype data is trading-grade.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

SUSPICIOUS_RETURN_THRESHOLD = 0.10  # 10% daily move


def _normalize_df(
    df: pd.DataFrame,
    price_col: str = "price",
    date_col: str = "date",
) -> pd.DataFrame:
    """Return dataframe with datetime index and price column."""
    out = df.copy()
    if date_col in out.columns:
        out[date_col] = pd.to_datetime(out[date_col])
        out = out.set_index(date_col)
    elif not isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index)
    out.index.name = "date"
    if price_col not in out.columns and "close" in out.columns:
        price_col = "close"
    if price_col not in out.columns:
        raise ValueError(f"Price column '{price_col}' not found in dataframe")
    out = out.sort_index()
    return out


def _infer_frequency(index: pd.DatetimeIndex) -> str:
    if len(index) < 3:
        return "unknown"
    deltas = pd.Series(index).diff().dropna().dt.days
    median_days = float(deltas.median())
    if median_days <= 1:
        return "daily"
    if median_days <= 7:
        return "weekly"
    if median_days <= 31:
        return "monthly"
    return "low_frequency"


def run_data_quality_checks(
    df: pd.DataFrame,
    source_name: str,
    price_col: str = "price",
    date_col: str = "date",
) -> Dict[str, Any]:
    """
    Evaluate data quality for a price series.

    Returns dict with observation counts, missing values, suspicious returns,
    and data_quality_flag: OK | WARNING | FAIL.
    """
    if df.empty:
        return {
            "source_name": source_name,
            "observation_count": 0,
            "start_date": None,
            "end_date": None,
            "missing_price_count": 0,
            "missing_price_pct": 100.0,
            "duplicate_date_count": 0,
            "min_price": None,
            "max_price": None,
            "mean_price": None,
            "zero_or_negative_price_count": 0,
            "largest_abs_daily_return": None,
            "suspicious_return_count": 0,
            "weekend_observation_count": 0,
            "inferred_frequency": "unknown",
            "data_quality_flag": "FAIL",
        }

    work = _normalize_df(df, price_col, date_col)
    prices = work[price_col if price_col in work.columns else "close"]

    missing = int(prices.isna().sum())
    n = len(work)
    missing_pct = round(missing / n * 100, 4) if n else 100.0

    dup_count = int(work.index.duplicated().sum())

    valid_prices = prices.dropna()
    zero_neg = int((valid_prices <= 0).sum()) if len(valid_prices) else 0

    rets = valid_prices.pct_change().dropna()
    largest_abs = float(rets.abs().max()) if len(rets) else None
    suspicious = int((rets.abs() > SUSPICIOUS_RETURN_THRESHOLD).sum()) if len(rets) else 0

    weekend = int((work.index.dayofweek >= 5).sum())

    flag = "OK"
    if dup_count > n * 0.01 or missing_pct > 5 or zero_neg > 0:
        flag = "WARNING"
    if missing_pct > 20 or dup_count > n * 0.05 or zero_neg > n * 0.01:
        flag = "FAIL"
    if n == 0:
        flag = "FAIL"
    if suspicious > 0 and flag == "OK":
        flag = "WARNING"

    tier = "unknown"
    tier_number = None
    tier_label = "unknown"
    try:
        from .data_sources import DATA_SOURCE_REGISTRY, get_data_source

        if source_name in DATA_SOURCE_REGISTRY:
            enriched = get_data_source(source_name)
            tier = enriched["tier"]
            tier_number = enriched["tier_number"]
            tier_label = enriched["tier_label"]
        elif source_name in ("fred_h10", "fred"):
            enriched = get_data_source("fred")
            tier = enriched["tier"]
            tier_number = enriched["tier_number"]
            tier_label = enriched["tier_label"]
    except Exception:
        pass

    return {
        "source_name": source_name,
        "data_tier": tier,
        "tier_number": tier_number,
        "tier_label": tier_label,
        "observation_count": n,
        "start_date": str(work.index.min().date()) if n else None,
        "end_date": str(work.index.max().date()) if n else None,
        "missing_price_count": missing,
        "missing_price_pct": missing_pct,
        "duplicate_date_count": dup_count,
        "min_price": round(float(valid_prices.min()), 6) if len(valid_prices) else None,
        "max_price": round(float(valid_prices.max()), 6) if len(valid_prices) else None,
        "mean_price": round(float(valid_prices.mean()), 6) if len(valid_prices) else None,
        "zero_or_negative_price_count": zero_neg,
        "largest_abs_daily_return": round(largest_abs, 6) if largest_abs is not None else None,
        "suspicious_return_count": suspicious,
        "weekend_observation_count": weekend,
        "inferred_frequency": _infer_frequency(work.index),
        "data_quality_flag": flag,
    }


def save_data_quality_report(
    report_dict: Union[Dict[str, Any], pd.DataFrame],
    path: Optional[Path] = None,
) -> Path:
    """Save quality report to CSV (or JSON if path ends with .json)."""
    path = path or ROOT / "data" / "outputs" / "data_quality_report.csv"
    path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(report_dict, pd.DataFrame):
        report_dict.to_csv(path, index=False)
        return path

    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(report_dict, indent=2), encoding="utf-8")
    else:
        pd.DataFrame([report_dict]).to_csv(path, index=False)
    return path

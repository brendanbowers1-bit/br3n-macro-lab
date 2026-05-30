"""
Public calendar flow proxies for remittance-heavy FX corridors.

These are crude public proxies — NOT actual order-flow or payment data.
Exploratory only; not causal evidence of private flow pressure.
"""

from __future__ import annotations

import calendar
from typing import Any, Dict, Optional

import pandas as pd

from .corridors import get_corridor


def _ensure_datetime(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"])
        out = out.set_index("date", drop=False)
    elif not isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index)
        out["date"] = out.index
    else:
        out["date"] = out.index
    return out


def _days_from_payday(day: int) -> bool:
    anchors = [1, 15, 30, 31]
    return any(abs(day - a) <= 2 for a in anchors)


def _is_month_end_series(dt: pd.Series, n_days: int = 3) -> pd.Series:
    return dt.dt.is_month_end | (dt.dt.days_in_month - dt.dt.day < n_days)


def _is_month_start_series(dt: pd.Series, n_days: int = 3) -> pd.Series:
    return dt.dt.day <= n_days


def _is_quarter_end_series(dt: pd.Series) -> pd.Series:
    return dt.dt.is_quarter_end


def _is_year_end_series(dt: pd.Series) -> pd.Series:
    """December 15 through December 31."""
    return (dt.dt.month == 12) & (dt.dt.day >= 15)


def _add_generic_proxies(out: pd.DataFrame) -> pd.DataFrame:
    dt = out["date"]
    out["day_of_week"] = dt.dt.dayofweek
    out["day_of_month"] = dt.dt.day
    out["month"] = dt.dt.month
    out["is_month_end"] = _is_month_end_series(dt)
    out["is_month_start"] = _is_month_start_series(dt)
    out["is_quarter_end"] = _is_quarter_end_series(dt)
    out["is_year_end"] = _is_year_end_series(dt)
    out["is_first_half_month"] = out["day_of_month"] <= 15
    out["is_second_half_month"] = out["day_of_month"] > 15
    out["is_payday_window"] = out["day_of_month"].apply(_days_from_payday)
    out["is_us_tax_refund_season"] = out["month"].isin([2, 3, 4])
    out["is_christmas_season"] = out["month"].eq(12)
    out["is_school_fee_season"] = out["month"].isin([1, 8])
    return out


def _corridor_specific_proxies(out: pd.DataFrame, corridor_id: str) -> pd.DataFrame:
    """Add corridor-specific calendar proxies (exploratory, not causal)."""
    m = out["month"]
    d = out["day_of_month"]

    out["is_mothers_day_window"] = False
    out["is_semana_santa_proxy"] = False
    out["is_diwali_proxy"] = False
    out["is_ramadan_eid_proxy"] = False
    out["is_local_holiday_placeholder"] = False
    out["is_extended_christmas_proxy"] = False

    if corridor_id == "US_MX":
        out["is_mothers_day_window"] = (m == 5) & (d <= 15)
        out["is_semana_santa_proxy"] = ((m == 3) & (d >= 15)) | ((m == 4) & (d <= 15))

    elif corridor_id in ("US_IN", "GULF_IN_PROXY"):
        out["is_diwali_proxy"] = ((m == 10) & (d >= 15)) | ((m == 11) & (d <= 15))
        out["is_school_fee_season"] = m.isin([1, 8])
        if corridor_id == "GULF_IN_PROXY":
            # Approximate Ramadan/Eid window — not lunar-accurate without proper calendar data
            out["is_ramadan_eid_proxy"] = m.isin([3, 4, 5, 6])

    elif corridor_id == "US_PH":
        out["is_extended_christmas_proxy"] = m.isin([9, 10, 11, 12])
        out["is_school_fee_season"] = m.isin([5, 6, 8])

    elif corridor_id in ("US_CO", "US_BR", "US_GT"):
        out["is_local_holiday_placeholder"] = out["is_christmas_season"] | out["is_month_end"]

    return out


def add_corridor_flow_proxies(
    df: pd.DataFrame,
    corridor_id: str,
    corridor_metadata: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Add generic and corridor-specific public flow-proxy columns.

    Public calendar proxies are NOT actual order-flow or payment-flow data.
    """
    meta = corridor_metadata or get_corridor(corridor_id)
    out = _ensure_datetime(df)
    out = _add_generic_proxies(out)
    out = _corridor_specific_proxies(out, corridor_id)

    proxy_cols = [
        "is_payday_window",
        "is_us_tax_refund_season",
        "is_christmas_season",
        "is_school_fee_season",
        "is_mothers_day_window",
        "is_semana_santa_proxy",
        "is_diwali_proxy",
        "is_ramadan_eid_proxy",
        "is_extended_christmas_proxy",
        "is_local_holiday_placeholder",
        "is_month_end",
        "is_quarter_end",
        "is_year_end",
    ]
    existing = [c for c in proxy_cols if c in out.columns]
    out["is_flow_pressure_window"] = out[existing].any(axis=1)
    out["flow_corridor"] = corridor_id
    out["official_pair_label"] = meta.get("official_pair_label", "")
    return out


def add_calendar_flow_proxies(
    df: pd.DataFrame,
    corridor: str = "US_MX",
) -> pd.DataFrame:
    """Backward-compatible wrapper for USD/MXN and legacy corridor strings."""
    cid = corridor.replace("USD_MXN", "US_MX").replace("USD_MXN", "US_MX")
    if cid not in ("US_MX", "US_IN", "US_PH", "US_CO", "US_BR", "US_GT", "GULF_IN_PROXY"):
        cid = "US_MX"
    return add_corridor_flow_proxies(df, cid)

"""
Canonical FX market data schema for BR3N Macro Labs.

Every standardized price series should carry provenance columns.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd

REQUIRED_MARKET_COLUMNS = [
    "date",
    "price",
    "currency_pair",
    "source",
    "data_tier",
    "frequency",
    "price_type",
    "price_convention",
    "downloaded_at",
]

OPTIONAL_MARKET_COLUMNS = [
    "bid",
    "ask",
    "mid",
    "forward_1m",
    "forward_3m",
    "implied_vol_1m",
    "policy_rate_domestic",
    "policy_rate_foreign",
    "carry_proxy",
    "remittance_proxy",
    "flow_pressure_window",
    "missing_value_policy",
    "limitations",
]


def validate_market_schema(df: pd.DataFrame) -> List[str]:
    """Return list of missing required columns (empty if valid)."""
    missing: List[str] = []
    work = df.reset_index() if isinstance(df.index, pd.DatetimeIndex) and "date" not in df.columns else df.copy()
    if "date" not in work.columns and work.index.name == "date":
        work = work.reset_index()
    for col in REQUIRED_MARKET_COLUMNS:
        if col not in work.columns:
            missing.append(col)
    return missing


def standardize_market_dataframe(
    df: pd.DataFrame,
    metadata: Dict[str, Any],
    *,
    price_col: str = "price",
    date_col: str = "date",
) -> pd.DataFrame:
    """
    Ensure canonical market schema: datetime date, numeric price, metadata columns.

    - sorts by date
    - drops duplicate dates (keeps last)
    - drops rows with missing price
    """
    out = df.copy()

    if date_col in out.columns:
        out[date_col] = pd.to_datetime(out[date_col])
        out = out.set_index(date_col)
    elif not isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index)

    out.index.name = "date"
    out = out.sort_index()

    if price_col not in out.columns and "close" in out.columns:
        price_col = "close"
    if price_col not in out.columns:
        raise ValueError(f"Price column '{price_col}' not found")

    out["price"] = pd.to_numeric(out[price_col], errors="coerce")
    out = out[~out.index.duplicated(keep="last")]
    out = out.dropna(subset=["price"])

    meta = dict(metadata)
    meta.setdefault("downloaded_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    meta.setdefault("frequency", "daily")
    meta.setdefault("price_type", "close")
    meta.setdefault("missing_value_policy", "drop_na_price")

    for key in REQUIRED_MARKET_COLUMNS:
        if key in ("date", "price"):
            continue
        if key in meta:
            out[key] = meta[key]

    if "limitations" in meta:
        out["limitations"] = meta["limitations"]

    out = out.reset_index()
    keep = ["date", "price"] + [c for c in REQUIRED_MARKET_COLUMNS if c not in ("date", "price")]
    keep += [c for c in OPTIONAL_MARKET_COLUMNS if c in out.columns]
    keep = list(dict.fromkeys(keep))
    return out[keep]

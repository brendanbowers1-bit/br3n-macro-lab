"""
Academic-grade FX loaders — FRED / Federal Reserve H.10.

Uses public CSV endpoints (no API key required for graph CSV).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from .data_loader import _trim_years, attach_source_metadata
from .data_schema import standardize_market_dataframe
from .data_sources import FRED_H10_USDMXN_SERIES, get_source_metadata
from .macro_loader import fetch_fred_series

# Confirm series ID before academic publication (H.10 USD/MXN daily).
USDMXN_FRED_SERIES = FRED_H10_USDMXN_SERIES
USDMXN_CURRENCY_PAIR = "USD/MXN"
USDMXN_PRICE_CONVENTION = "Mexican pesos per U.S. dollar"


def load_fred_csv_series(
    series_id: str,
    currency_pair: str,
    price_convention: str,
    *,
    years: int = 25,
    source_key: str = "fred_h10",
) -> pd.DataFrame:
    """
    Download FRED graph CSV and return standardized market dataframe.

    URL: https://fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES_ID

    Raises RuntimeError with yfinance fallback hint on failure.
    """
    meta = get_source_metadata(source_key)
    try:
        s = fetch_fred_series(series_id, timeout=60, retries=3)
    except Exception as exc:
        raise RuntimeError(
            f"FRED CSV download failed for {series_id}: {exc}. "
            "Fallback: set data.preferred_source to 'yfinance' or use load_or_fetch() prototype path."
        ) from exc

    if s.empty:
        raise RuntimeError(
            f"FRED series {series_id} returned no data. "
            "Confirm series ID. Fallback: yfinance USDMXN=X."
        )

    df = pd.DataFrame({"price": s}).dropna()
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    df = _trim_years(df.sort_index(), years)

    metadata = {
        "currency_pair": currency_pair,
        "source": source_key,
        "data_tier": meta.get("architecture_tier", "academic"),
        "frequency": "daily",
        "price_type": "official_public_rate",
        "price_convention": price_convention,
        "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "limitations": meta.get("warning", "Daily official rate; not bid/ask or executable."),
    }
    return standardize_market_dataframe(df, metadata)


def load_usdmxn_fred_h10(years: int = 25) -> pd.DataFrame:
    """
    Load USD/MXN from FRED H.10 series DEXMXUS.

    Confirm FRED series ID (DEXMXUS) before academic publication.
    """
    return load_fred_csv_series(
        USDMXN_FRED_SERIES,
        USDMXN_CURRENCY_PAIR,
        USDMXN_PRICE_CONVENTION,
        years=years,
        source_key="fred_h10",
    )


def load_usdmxn_fred_h10_indexed(years: int = 25) -> pd.DataFrame:
    """Same as load_usdmxn_fred_h10 but indexed by date with lab metadata columns."""
    std = load_usdmxn_fred_h10(years=years)
    df = std.set_index("date")
    return attach_source_metadata(
        df[["price"]],
        source="fred_h10",
        data_tier="academic",
        tier_number=1,
        price_type="official_public_rate",
        convention=f"USD/MXN ({USDMXN_FRED_SERIES}, H.10 via FRED)",
    )

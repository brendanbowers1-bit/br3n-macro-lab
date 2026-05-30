"""
Tier 1 official spot loaders — free public sources (FRED / H.10).

Not trading-grade (no bid/ask). Suitable for academic-grade research reruns.
"""

from __future__ import annotations

import os
from pathlib import Path
from io import StringIO
from typing import List, Optional, Tuple

import pandas as pd
import requests

from .data_loader import attach_source_metadata, _trim_years
from .data_sources import FRED_H10_USDMXN_SERIES, get_data_source
from .macro_loader import fetch_fred_series

ROOT = Path(__file__).resolve().parents[1]

OFFICIAL_RAW_CSV = ROOT / "data" / "raw" / "USDMXN_official_tier1.csv"

OFFICIAL_USDMXN_SERIES = {
    "fred_h10": FRED_H10_USDMXN_SERIES,
}


def _fetch_fred_api_csv(series_id: str, api_key: str, timeout: int = 30) -> pd.Series:
    """FRED REST API — more reliable than graph CSV when you have a free API key."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    r = requests.get(
        url,
        params={
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "csv",
        },
        timeout=timeout,
    )
    r.raise_for_status()
    raw = pd.read_csv(StringIO(r.text))
    raw.columns = [str(c).strip().lower() for c in raw.columns]
    date_col = "date" if "date" in raw.columns else raw.columns[0]
    val_col = "value" if "value" in raw.columns else raw.columns[-1]
    raw[date_col] = pd.to_datetime(raw[date_col])
    s = raw.set_index(date_col)[val_col].replace(".", pd.NA).astype(float)
    s.index.name = "date"
    return s.sort_index().dropna()


def _load_manual_official_csv() -> pd.Series | None:
    """Optional vendor file: data/raw/USDMXN_official_tier1.csv (date, price)."""
    if not OFFICIAL_RAW_CSV.exists():
        return None
    raw = pd.read_csv(OFFICIAL_RAW_CSV)
    raw.columns = [str(c).lower() for c in raw.columns]
    date_col = "date" if "date" in raw.columns else raw.columns[0]
    price_col = "price" if "price" in raw.columns else raw.columns[1]
    raw[date_col] = pd.to_datetime(raw[date_col])
    s = raw.set_index(date_col)[price_col].astype(float)
    s.index.name = "date"
    print(f"  Using manual Tier 1 CSV: {OFFICIAL_RAW_CSV}")
    return s.sort_index().dropna()


def fetch_official_usdmxn(
    years: int = 25,
    series_id: str = FRED_H10_USDMXN_SERIES,
) -> pd.DataFrame:
    """
    Fetch official USD/MXN spot from FRED (Federal Reserve H.10 daily rate).

    Series DEXMXUS: Mexican pesos per 1 U.S. dollar (same convention as lab USD/MXN).
    Tier 1 — official / academic-grade. Not executable; no bid/ask.
    """
    errors: List[str] = []
    s: pd.Series | None = None
    api_key = os.environ.get("FRED_API_KEY", "").strip()

    sources: List[tuple] = [
        ("manual raw CSV", _load_manual_official_csv),
    ]
    if api_key:
        sources.append(
            ("FRED API", lambda: _fetch_fred_api_csv(series_id, api_key, timeout=30))
        )
    sources.append(
        ("FRED graph CSV", lambda: fetch_fred_series(series_id, timeout=25, retries=2))
    )

    for name, fn in sources:
        try:
            s = fn()
            if s is not None and not s.empty:
                print(f"  Tier 1 source: {name}")
                break
        except Exception as exc:
            errors.append(f"{name}: {exc}")
            s = None

    if s is None or s.empty:
        msg = "; ".join(errors) if errors else "no source returned data"
        raise RuntimeError(
            f"Could not fetch Tier 1 USD/MXN ({series_id}). {msg}. "
            f"Options: (1) set FRED_API_KEY env var — free at fred.stlouisfed.org/docs/api/api_key.html "
            f"(2) place CSV at {OFFICIAL_RAW_CSV} (3) retry when FRED is up"
        )
    df = pd.DataFrame({"price": s}).dropna()
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    df = _trim_years(df.sort_index(), years)
    meta = get_data_source("fed_h10")
    return attach_source_metadata(
        df,
        source="fred_h10",
        tier_number=meta["tier_number"],
        price_type="official_daily",
        convention=f"USD/MXN ({series_id}, H.10 via FRED)",
    )


def load_or_fetch_official_usdmxn(
    years: int = 25,
    force_refresh: bool = False,
) -> Tuple[pd.DataFrame, Path]:
    """Load cached Tier 1 USD/MXN or fetch from FRED."""
    proc_dir = ROOT / "data" / "processed"
    proc_dir.mkdir(parents=True, exist_ok=True)
    path = proc_dir / "USDMXN_X_official_tier1.csv"

    if path.exists() and not force_refresh:
        cached = pd.read_csv(path, parse_dates=[0], index_col=0)
        cached.index.name = "date"
        return cached, path

    df = fetch_official_usdmxn(years=years)
    df.to_csv(path)
    print(
        f"Saved Tier 1 official USD/MXN: {len(df)} rows -> {path} "
        f"({df.index.min().date()} to {df.index.max().date()})"
    )
    return df, path

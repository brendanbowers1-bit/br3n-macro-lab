"""
BIS effective exchange rate loader (Tier 1 official macro FX context).

Fetches nominal broad effective exchange rate indices from BIS public statistics.
Not bilateral spot — useful for macro competitiveness and broad FX pressure research.
"""

from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

from .data_loader import attach_source_metadata, _trim_years

ROOT = Path(__file__).resolve().parents[1]
BIS_EER_CACHE = ROOT / "data" / "processed" / "bis_eer_mexico.csv"

BIS_EER_ZIP_URL = "https://www.bis.org/statistics/eer/WS_EER_csv_col.zip"

# BIS REF_AREA codes (nominal broad EER, daily where available)
COUNTRY_CODES = {
    "MX": "MX",
    "MEXICO": "MX",
    "US": "US",
    "BR": "BR",
    "IN": "IN",
}


def fetch_bis_nominal_eer(
    country_code: str = "MX",
    years: int = 25,
    timeout: int = 90,
) -> pd.DataFrame:
    """
    Download BIS nominal broad effective exchange rate (column CSV) for a country.

    Returns dataframe with price column (index level, not bilateral spot).
    """
    code = COUNTRY_CODES.get(country_code.upper(), country_code.upper())
    r = requests.get(BIS_EER_ZIP_URL, timeout=timeout)
    r.raise_for_status()

    with zipfile.ZipFile(BytesIO(r.content)) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            raise RuntimeError("No CSV found in BIS EER zip archive")
        raw = pd.read_csv(zf.open(csv_names[0]))

    # BIS column-format CSV: first col is date/time, country codes as headers
    raw.columns = [str(c).strip() for c in raw.columns]
    date_col = raw.columns[0]
    raw[date_col] = pd.to_datetime(raw[date_col], errors="coerce")
    raw = raw.dropna(subset=[date_col])

    col = None
    for candidate in (code, f"{code}N", f"{code}_N"):
        if candidate in raw.columns:
            col = candidate
            break
    if col is None:
        matches = [c for c in raw.columns if c.upper().startswith(code)]
        col = matches[0] if matches else None
    if col is None:
        raise RuntimeError(
            f"Country code {code} not found in BIS EER CSV. "
            f"Available columns sample: {raw.columns[:12].tolist()}"
        )

    s = pd.to_numeric(raw[col], errors="coerce")
    df = pd.DataFrame({"price": s.values}, index=raw[date_col].values)
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    df = df.dropna().sort_index()
    df = _trim_years(df, years)

    return attach_source_metadata(
        df,
        source="bis_eer",
        tier_number=1,
        price_type="nominal_broad_eer_index",
        convention=f"BIS nominal broad EER ({code})",
    )


def load_or_fetch_bis_mexico_eer(
    years: int = 25,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """Load cached BIS Mexico EER or fetch from BIS."""
    if BIS_EER_CACHE.exists() and not force_refresh:
        cached = pd.read_csv(BIS_EER_CACHE, parse_dates=[0], index_col=0)
        cached.index.name = "date"
        return cached

    df = fetch_bis_nominal_eer("MX", years=years)
    BIS_EER_CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(BIS_EER_CACHE)
    print(f"Saved BIS Mexico EER: {len(df)} rows -> {BIS_EER_CACHE}")
    return df

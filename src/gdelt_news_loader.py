"""
Optional GDELT open-news loader for exploratory news intensity features.

GDELT data is open and exploratory; validate before academic claims.
Research-only — not a trading signal source.
"""

from __future__ import annotations

import logging
from io import StringIO
from typing import Optional
from urllib.parse import quote

import pandas as pd
import requests

logger = logging.getLogger(__name__)

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"


def build_gdelt_query_url(
    query: str,
    start_date: str,
    end_date: str,
    max_records: int = 250,
) -> str:
    """
    Build a documented GDELT DOC 2.0 timeline URL for daily article volume.

    mode=timelinevol returns daily counts; format=csv for pandas parsing.
    """
    q = quote(query)
    # GDELT expects YYYYMMDDHHMMSS; use day boundaries
    start = start_date.replace("-", "") + "000000"
    end = end_date.replace("-", "") + "235959"
    return (
        f"{GDELT_DOC_API}?query={q}&mode=timelinevol&timelinesmooth=0"
        f"&format=csv&STARTDATETIME={start}&ENDDATETIME={end}&maxrecords={max_records}"
    )


def fetch_gdelt_article_counts(
    query: str,
    start_date: str,
    end_date: str,
    timeout: int = 60,
) -> pd.DataFrame:
    """
    Fetch daily article counts for a GDELT query.

    Returns empty dataframe with warning on failure.
    Columns: date, query, article_count
    """
    url = build_gdelt_query_url(query, start_date, end_date)
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        text = r.text.strip()
        if not text or "error" in text.lower()[:200]:
            logger.warning("GDELT empty or error response for query: %s", query[:60])
            return pd.DataFrame(columns=["date", "query", "article_count"])

        raw = pd.read_csv(StringIO(text))
        raw.columns = [str(c).strip().lower() for c in raw.columns]

        date_col = next((c for c in raw.columns if "date" in c or "datetime" in c), raw.columns[0])
        val_col = next((c for c in raw.columns if "volume" in c or "count" in c or "value" in c), raw.columns[-1])

        raw[date_col] = pd.to_datetime(raw[date_col], errors="coerce")
        out = pd.DataFrame(
            {
                "date": raw[date_col].dt.normalize(),
                "query": query,
                "article_count": pd.to_numeric(raw[val_col], errors="coerce"),
            }
        ).dropna(subset=["date"])
        return out.groupby(["date", "query"], as_index=False)["article_count"].sum()
    except Exception as exc:
        logger.warning("GDELT fetch failed for '%s': %s", query[:40], exc)
        return pd.DataFrame(columns=["date", "query", "article_count"])


COUNTRY_QUERIES = {
    "Mexico": "Mexico economy central bank inflation peso",
    "India": "India rupee RBI inflation",
    "Philippines": "Philippines peso central bank remittances",
    "Colombia": "Colombia peso oil central bank",
    "Brazil": "Brazil real central bank inflation",
}


def build_country_news_intensity(
    country: str,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """Daily news intensity for one country query."""
    query = COUNTRY_QUERIES.get(country, f"{country} economy currency central bank")
    counts = fetch_gdelt_article_counts(query, start_date, end_date)
    if counts.empty:
        return pd.DataFrame(columns=["date", "country_news_intensity"])
    out = counts.groupby("date", as_index=False)["article_count"].sum()
    out = out.rename(columns={"article_count": "country_news_intensity"})
    out["country"] = country
    return out


def build_usdmxn_news_features(start_date: str, end_date: str) -> pd.DataFrame:
    """
    USD/MXN corridor news intensity from multiple GDELT queries.

    GDELT data is open and exploratory; validate before academic claims.
    """
    queries = {
        "mexico_news_intensity": "Mexico peso Banxico inflation",
        "fed_news_intensity": "Federal Reserve dollar rates",
        "election_news_intensity": "Mexico election economy",
        "oil_news_intensity": "oil prices Mexico",
        "trade_news_intensity": "trade tariffs Mexico United States",
    }

    frames = []
    for col, q in queries.items():
        counts = fetch_gdelt_article_counts(q, start_date, end_date)
        if counts.empty:
            continue
        daily = counts.groupby("date", as_index=False)["article_count"].sum()
        daily = daily.rename(columns={"article_count": col})
        frames.append(daily)

    if not frames:
        return pd.DataFrame()

    out = frames[0]
    for f in frames[1:]:
        out = pd.merge(out, f, on="date", how="outer")

    intensity_cols = [c for c in out.columns if c.endswith("_intensity")]
    out[intensity_cols] = out[intensity_cols].fillna(0)
    out["total_usdmxn_news_intensity"] = out[intensity_cols].sum(axis=1)
    out["date"] = pd.to_datetime(out["date"])
    return out.sort_values("date")

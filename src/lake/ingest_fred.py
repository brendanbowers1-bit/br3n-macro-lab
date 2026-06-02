"""Ingest FRED DFEDTARU (Fed funds target upper bound) into data-lake/raw/rates/."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

from src.lake.fred_graph import fetch_fred_graph_csv
from src.lake.paths import FED_POLICY_CSV, FED_POLICY_META, RAW_RATES

FRED_GRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFEDTARU"
SOURCE_ID = "rates_fed_policy"


def ingest_fred_policy_rate(*, min_date: str = "2024-01-01") -> Path:
    """Download FRED CSV and write immutable raw file + sidecar metadata."""
    RAW_RATES.mkdir(parents=True, exist_ok=True)

    content = fetch_fred_graph_csv("DFEDTARU", min_date=min_date)

    dated_name = f"fed_policy_rate_dfedtaru_{date.today().strftime('%Y%m%d')}.csv"
    dated_path = RAW_RATES / dated_name
    dated_path.write_text(content, encoding="utf-8")

    FED_POLICY_CSV.write_text(content, encoding="utf-8")

    meta = {
        "source_id": SOURCE_ID,
        "source_name": "Federal Reserve policy rate (upper bound)",
        "fred_series": "DFEDTARU",
        "url_or_reference": FRED_GRAPH_URL,
        "retrieval_date": date.today().isoformat(),
        "retrieval_method": "fred_public_graph_csv",
        "data_mode": "live",
        "synthetic_flag": False,
        "license_terms_note": "FRED / St. Louis Fed — research use; verify terms for production.",
        "raw_dated_file": dated_name,
        "min_date_filter": min_date,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }
    FED_POLICY_META.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return dated_path

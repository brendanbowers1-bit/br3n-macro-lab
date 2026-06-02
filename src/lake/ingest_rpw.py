"""Build RPW US→Mexico remittance cost proxy for data-lake."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

from src.lake.paths import RAW_REMITTANCES, RPW_COST_CSV, RPW_COST_META, ROOT

RPW_PANEL = ROOT / "data" / "raw" / "world_bank_rpw" / "rpw_historical_panel.csv"
RPW_CURATED = ROOT / "data" / "raw" / "world_bank_rpw" / "rpw_corridors_curated.csv"
SOURCE_ID = "corridor_remittance_cost_proxy"
CORRIDOR = "United States→Mexico"


def _load_rpw_sources() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in (RPW_PANEL, RPW_CURATED):
        if path.exists():
            frames.append(pd.read_csv(path))
    if not frames:
        raise FileNotFoundError(
            f"No RPW source files found under {ROOT / 'data' / 'raw' / 'world_bank_rpw'}"
        )
    df = pd.concat(frames, ignore_index=True)
    df = df[df["corridor"] == CORRIDOR].copy()
    if df.empty:
        raise ValueError(f"No RPW rows for corridor {CORRIDOR}")
    return df


def build_us_mx_rpw_quarterly(df: pd.DataFrame) -> pd.DataFrame:
    """Quarterly corridor cost proxy: min transparent total cost per quarter."""
    work = df.copy()
    work["date"] = pd.to_datetime(work["date"])
    work["total_cost_pct"] = pd.to_numeric(work["total_cost_pct"], errors="coerce")
    work["fee_pct"] = pd.to_numeric(work["fee_pct"], errors="coerce")
    work["fx_margin_pct"] = pd.to_numeric(work["fx_margin_pct"], errors="coerce")
    work = work.dropna(subset=["date", "total_cost_pct"])
    grouped = (
        work.groupby(["date", "quarter"], as_index=False)
        .agg(
            remittance_cost_proxy=("total_cost_pct", "min"),
            fee_pct=("fee_pct", "median"),
            fx_margin_pct=("fx_margin_pct", "median"),
            provider_count=("provider", "count"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )
    grouped["corridor"] = CORRIDOR
    grouped["source_id"] = SOURCE_ID
    return grouped


def ingest_rpw_remittance_cost() -> Path:
    """Write quarterly US→MX RPW cost proxy to data-lake/raw/remittances/."""
    RAW_REMITTANCES.mkdir(parents=True, exist_ok=True)
    df = _load_rpw_sources()
    quarterly = build_us_mx_rpw_quarterly(df)

    dated_name = f"us_mx_rpw_cost_quarterly_{date.today().strftime('%Y%m%d')}.csv"
    dated_path = RAW_REMITTANCES / dated_name
    quarterly.to_csv(dated_path, index=False)
    quarterly.to_csv(RPW_COST_CSV, index=False)

    meta = {
        "source_id": SOURCE_ID,
        "source_name": "US to Mexico remittance cost proxy (RPW)",
        "url_or_reference": "https://remittanceprices.worldbank.org/",
        "upstream_files": [
            str(RPW_PANEL.relative_to(ROOT)),
            str(RPW_CURATED.relative_to(ROOT)),
        ],
        "retrieval_date": date.today().isoformat(),
        "retrieval_method": "derived_from_rpw_panel",
        "data_mode": "live",
        "synthetic_flag": False,
        "license_terms_note": "World Bank RPW — attribution required; verify commercial terms.",
        "raw_dated_file": dated_name,
        "quarters": int(len(quarterly)),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }
    RPW_COST_META.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return dated_path

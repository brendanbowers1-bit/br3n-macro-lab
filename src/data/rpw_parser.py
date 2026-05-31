"""
Parse full World Bank RPW Excel/CSV when manually downloaded.

Drop file as: data/raw/world_bank_rpw/rpw_complete.xlsx (or .csv)

Attribution: The World Bank, Remittance Prices Worldwide
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.paths import RAW_DIR

from .cleaners import clean_percent_columns, dedupe_corridor_prices, enforce_schema, parse_dates, standardize_columns


def find_rpw_bulk_file() -> Path | None:
    d = RAW_DIR / "world_bank_rpw"
    for name in ("rpw_complete.xlsx", "rpw_complete.csv", "RPW_complete.xlsx", "remittance_prices_worldwide.xlsx"):
        p = d / name
        if p.exists():
            return p
    for ext in ("*.xlsx", "*.xls", "*.csv"):
        files = sorted(d.glob(ext))
        for f in files:
            if "curated" not in f.name.lower() and f.stat().st_size > 100_000:
                return f
    return None


def parse_rpw_bulk(path: Path) -> pd.DataFrame:
    """Normalize bulk RPW file to corridor_prices schema."""
    if path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path, sheet_name=0)
    else:
        df = pd.read_csv(path)

    df = standardize_columns(
        df,
        {
            "sending_country": "sender_country",
            "receiving_country": "receiver_country",
            "sending currency": "sender_currency",
            "receiving currency": "receiver_currency",
            "total cost": "total_cost_pct",
            "fee": "fee_pct",
            "fx margin": "fx_margin_pct",
            "fx rate margin": "fx_margin_pct",
            "speed": "transfer_speed_days",
            "amount": "send_amount_usd",
            "collection_date": "date",
            "quarter_year": "quarter",
        },
    )

    if "date" not in df.columns and "quarter" in df.columns:
        df["date"] = pd.to_datetime(df["quarter"].astype(str).str.replace("Q", "-Q"), errors="coerce")

    df = clean_percent_columns(df, ["total_cost_pct", "fee_pct", "fx_margin_pct"])
    if "corridor" not in df.columns and {"sender_country", "receiver_country"}.issubset(df.columns):
        df["corridor"] = df["sender_country"].astype(str) + "→" + df["receiver_country"].astype(str)

    if "transparency_flag" not in df.columns:
        df["transparency_flag"] = True

    df["source"] = "world_bank_rpw_bulk"
    df = parse_dates(df)
    df = dedupe_corridor_prices(df)
    return enforce_schema(df, "corridor_prices", fill_missing=True)

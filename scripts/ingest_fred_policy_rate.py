#!/usr/bin/env python3
"""Ingest FRED DFEDTARU into data-lake/raw/rates/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.lake.ingest_fred import ingest_fred_policy_rate


def main() -> None:
    p = argparse.ArgumentParser(description="Ingest FRED Fed policy rate (DFEDTARU)")
    p.add_argument("--min-date", default="2024-01-01", help="Filter observations from this date")
    args = p.parse_args()

    path = ingest_fred_policy_rate(min_date=args.min_date)
    print(f"Ingested FRED DFEDTARU → {path}")
    print("Pointer updated: data-lake/raw/rates/fed_policy_rate_dfedtaru.csv")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ingest USD/MXN spot into data-lake/raw/fx/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.lake.ingest_banxico import ingest_usd_mxn_spot


def main() -> None:
    p = argparse.ArgumentParser(description="Ingest USD/MXN spot (Banxico SIE or FRED DEXMXUS)")
    p.add_argument("--min-date", default="2024-01-01")
    args = p.parse_args()
    path = ingest_usd_mxn_spot(min_date=args.min_date)
    print(f"Ingested USD/MXN spot → {path}")
    print("Pointer updated: data-lake/raw/fx/usd_mxn_spot.csv")


if __name__ == "__main__":
    main()

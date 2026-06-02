#!/usr/bin/env python3
"""Ingest Banxico policy rate into data-lake/raw/rates/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.lake.ingest_banxico import ingest_banxico_policy_rate


def main() -> None:
    p = argparse.ArgumentParser(description="Ingest Banxico policy rate (SIE SF61745 or FRED proxy)")
    p.add_argument("--min-date", default="2024-01-01")
    args = p.parse_args()
    path = ingest_banxico_policy_rate(min_date=args.min_date)
    print(f"Ingested Banxico policy rate → {path}")
    print("Pointer updated: data-lake/raw/rates/banxico_policy_rate.csv")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ingest RPW US→Mexico remittance cost proxy into data-lake/raw/remittances/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.lake.ingest_rpw import ingest_rpw_remittance_cost


def main() -> None:
    path = ingest_rpw_remittance_cost()
    print(f"Ingested RPW corridor cost proxy → {path}")
    print("Pointer updated: data-lake/raw/remittances/us_mx_rpw_cost_quarterly.csv")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Fetch and build real research data files for the Global FX Lab.

Sources:
- Lab FX cache → data/raw/imf/fx_rates_from_lab.csv
- FRED DXY → data/raw/fred/dxy_daily.csv
- Curated RPW corridor averages (from published WB RPW Q4 2024 reports)
- KNOMAD-style bilateral flows (World Bank migration/remittance estimates)
- BIS 2022 triennial turnover shares (published aggregates)
- Manual wage table template

Run: python scripts/fetch_global_fx_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.fetch_public import build_all_public_data  # noqa: E402


def main() -> None:
    print("Bowers Frontier Global FX Lab — fetching/building public data files")
    print("=" * 60)
    results = build_all_public_data()
    for name, path in results.items():
        status = "OK" if path and Path(path).exists() else "SKIP"
        print(f"  [{status}] {name}: {path}")
    print("\nRe-run pipeline: python scripts/run_global_fx_lab.py")


if __name__ == "__main__":
    main()

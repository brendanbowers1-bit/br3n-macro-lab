#!/usr/bin/env python3
"""Fetch Tier 1 official USD/MXN spot from FRED (H.10 DEXMXUS)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_quality import run_data_quality_checks, save_data_quality_report
from src.data_sources import FRED_H10_USDMXN_SERIES, print_data_source_plan
from src.official_loaders import load_or_fetch_official_usdmxn


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Fetch Tier 1 official USD/MXN (FRED H.10)")
    p.add_argument("--refresh", action="store_true", help="Force re-download from FRED")
    p.add_argument("--years", type=int, default=25)
    args = p.parse_args()

    df, path = load_or_fetch_official_usdmxn(years=args.years, force_refresh=args.refresh)
    report = run_data_quality_checks(df, source_name="fed_h10", price_col="price")
    report_path = save_data_quality_report(report, ROOT / "data" / "outputs" / "data_quality_report_tier1.csv")

    print("\nBR3N Macro Labs — Tier 1 Official USD/MXN")
    print("=" * 50)
    print(f"Series:       {FRED_H10_USDMXN_SERIES} (H.10 via FRED)")
    print(f"Tier:         {report.get('tier_number')} — {report.get('tier_label')}")
    print(f"Observations: {report['observation_count']}")
    print(f"Date range:   {report['start_date']} → {report['end_date']}")
    print(f"Quality flag: {report['data_quality_flag']}")
    print(f"Saved:        {path}")
    print(f"Quality:      {report_path}")
    print("\nNext: compare Tier 1 vs Tier 4 (yfinance) before making academic claims.")
    print_data_source_plan()


if __name__ == "__main__":
    main()

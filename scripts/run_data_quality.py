#!/usr/bin/env python3
"""Run data quality checks on processed USD/MXN features."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data_quality import run_data_quality_checks, save_data_quality_report


def main() -> None:
    processed = ROOT / "data" / "processed" / "usdmxn_features_regimes.csv"
    if not processed.exists():
        print("Missing data/processed/usdmxn_features_regimes.csv")
        print("Run: python scripts/run_usdmxn_backtest.py")
        sys.exit(1)

    df = pd.read_csv(processed, parse_dates=["date"])

    # Infer source from dataframe metadata or default to yfinance prototype
    source = "yfinance"
    if "source" in df.columns and df["source"].notna().any():
        source = str(df["source"].dropna().iloc[0])
    elif (ROOT / "data" / "processed" / "USDMXN_X.csv").exists():
        cache = pd.read_csv(ROOT / "data" / "processed" / "USDMXN_X.csv", nrows=5)
        if "source" in cache.columns:
            full = pd.read_csv(ROOT / "data" / "processed" / "USDMXN_X.csv")
            if full["source"].notna().any():
                source = str(full["source"].dropna().iloc[0])

    report = run_data_quality_checks(df, source_name=source, price_col="price", date_col="date")
    out_path = save_data_quality_report(report)

    print("\nBR3N Macro Labs — Data Quality Report")
    print("=" * 50)
    print(f"Source:              {report['source_name']}")
    print(f"Tier:                {report.get('tier_number', '?')} — {report.get('tier_label', report.get('data_tier', 'unknown'))}")
    print(f"Date range:          {report['start_date']} → {report['end_date']}")
    print(f"Observations:        {report['observation_count']}")
    print(f"Missing prices:      {report['missing_price_count']} ({report['missing_price_pct']}%)")
    print(f"Suspicious returns:  {report['suspicious_return_count']} (>|10%| daily)")
    print(f"Quality flag:        {report['data_quality_flag']}")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()

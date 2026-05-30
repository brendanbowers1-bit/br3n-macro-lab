#!/usr/bin/env python3
"""Fetch Tier 2 Bloomberg USD/MXN spot (requires licensed Terminal or B-PIPE)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.bloomberg_loader import (
    BloombergNotAvailableError,
    DEFAULT_USDMXN_TICKER,
    check_bloomberg_available,
    load_or_fetch_bloomberg_usdmxn,
)
from src.data_loader import load_config
from src.data_quality import run_data_quality_checks, save_data_quality_report


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Fetch Tier 2 Bloomberg USD/MXN")
    p.add_argument("--refresh", action="store_true")
    p.add_argument("--ticker", default=None, help="Bloomberg ticker, default USDMXN Curncy")
    p.add_argument("--check", action="store_true", help="Only check Bloomberg availability")
    args = p.parse_args()

    probe = check_bloomberg_available()
    print("\nBloomberg availability check")
    print("=" * 40)
    print(f"Available: {probe['available']}")
    print(f"Method:    {probe['method']}")
    print(probe["message"])

    if args.check:
        sys.exit(0 if probe["available"] else 1)

    if not probe["available"]:
        sys.exit(1)

    cfg = load_config()
    bb_cfg = cfg.get("bloomberg", {})
    ticker = args.ticker or bb_cfg.get("usdmxn_ticker", DEFAULT_USDMXN_TICKER)
    years = int(cfg["data"].get("history_years", 25))

    try:
        df, path = load_or_fetch_bloomberg_usdmxn(
            years=years,
            ticker=ticker,
            force_refresh=args.refresh,
            host=bb_cfg.get("host", "localhost"),
            port=int(bb_cfg.get("port", 8194)),
        )
    except BloombergNotAvailableError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)

    report = run_data_quality_checks(df, source_name="bloomberg", price_col="price")
    report_path = save_data_quality_report(
        report, ROOT / "data" / "outputs" / "data_quality_report_tier2_bloomberg.csv"
    )

    print("\nBR3N Macro Labs — Tier 2 Bloomberg USD/MXN")
    print("=" * 50)
    print(f"Ticker:       {ticker}")
    print(f"Tier:         {report.get('tier_number')} — {report.get('tier_label')}")
    print(f"Observations: {report['observation_count']}")
    print(f"Date range:   {report['start_date']} → {report['end_date']}")
    if "bid" in df.columns and "ask" in df.columns:
        print(f"Avg spread:   {df['spread_bps'].mean():.2f} bps (bid/ask available)")
    print(f"Quality flag: {report['data_quality_flag']}")
    print(f"Saved:        {path}")
    print(f"Quality:      {report_path}")
    print("\nNote: Bloomberg data is licensed — do not redistribute publicly.")


if __name__ == "__main__":
    main()

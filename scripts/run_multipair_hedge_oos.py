#!/usr/bin/env python3
"""Run pre-registered multi-pair hedge governance OOS tests (Level 8)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import load_config
from src.ladder.level8_hedge_oos import (
    hedge_oos_report_md,
    run_multipair_hedge_oos,
    save_hedge_oos_outputs,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-pair hedge governance OOS (Level 8)")
    parser.add_argument("--refresh", action="store_true", help="Force refresh price data")
    parser.add_argument(
        "--pairs",
        nargs="*",
        help="Optional ticker list (default: research_ladder.pairs, min 10)",
    )
    args = parser.parse_args()

    cfg = load_config()
    tickers = args.pairs or None
    scorecard, comparison, summary = run_multipair_hedge_oos(
        cfg, tickers=tickers, force_refresh=args.refresh
    )
    paths = save_hedge_oos_outputs(scorecard, comparison, summary)

    print("\n" + "=" * 60)
    print("BR3N Macro Labs — Multi-Pair Hedge OOS (Level 8)")
    print("=" * 60)
    print(hedge_oos_report_md(scorecard, comparison, summary))

    if not summary.empty:
        s = summary.iloc[0]
        print(f"Pairs tested: {s['pairs_tested']}")
        print(f"H8a pass: {s['h8a_pass']} ({s.get('pct_pairs_h8a')}% pairs)")
        print(f"H8b pass: {s['h8b_pass']} (median turnover red: {s.get('median_turnover_reduction_pct')}%)")

    print("\nOutputs:")
    for name, path in paths.items():
        print(f"  {name}: {path}")
    print("\nReminder: Prototype research only. Not investment advice.")


if __name__ == "__main__":
    main()

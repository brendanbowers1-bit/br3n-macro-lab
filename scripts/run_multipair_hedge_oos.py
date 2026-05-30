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
from src.ladder.level8_hedge_white_rc import (
    hedge_white_rc_report_md,
    run_hedge_policy_white_rc_suite,
    save_hedge_white_rc,
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
    scorecard, comparison, summary, static_cmp = run_multipair_hedge_oos(
        cfg, tickers=tickers, force_refresh=args.refresh
    )
    paths = save_hedge_oos_outputs(scorecard, comparison, summary, static_cmp=static_cmp)

    wrc_df = run_hedge_policy_white_rc_suite(cfg, scorecard=scorecard)
    wrc_path = save_hedge_white_rc(wrc_df)

    print("\n" + "=" * 60)
    print("BR3N Macro Labs — Multi-Pair Hedge OOS (Level 8)")
    print("=" * 60)
    print(hedge_oos_report_md(scorecard, comparison, summary))
    print(hedge_white_rc_report_md(wrc_df))

    if not summary.empty:
        for _, s in summary.iterrows():
            print(
                f"[{s.get('cost_layer')}] H8a={s.get('h8a_pass')} H8b={s.get('h8b_pass')} "
                f"H8d={s.get('h8d_pass')}"
            )

    print("\nOutputs:")
    for name, path in paths.items():
        print(f"  {name}: {path}")
    print(f"  white_rc: {wrc_path}")
    print("\nReminder: Prototype research only. Not investment advice.")


if __name__ == "__main__":
    main()

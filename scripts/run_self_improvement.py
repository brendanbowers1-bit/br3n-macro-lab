#!/usr/bin/env python3
"""
Run the lab self-improvement loop.

Scores current evidence, snapshots outputs, compares to prior runs,
and proposes next research experiments. Research-only — no live trading.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import load_config
from src.self_improve.runner import print_summary, run_self_improvement


def main() -> None:
    p = argparse.ArgumentParser(description="Bowers Frontier Macro Labs self-improvement loop")
    p.add_argument(
        "--rerun",
        action="store_true",
        help="Re-run configured pipelines before scoring (slower)",
    )
    args = p.parse_args()

    cfg = load_config()
    summary = run_self_improvement(cfg, rerun=args.rerun)
    print_summary(summary)


if __name__ == "__main__":
    main()

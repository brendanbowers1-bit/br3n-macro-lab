#!/usr/bin/env python3
"""Run eight-level research ladder."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ladder.runner import run_ladder


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--refresh", action="store_true", help="Re-download all pairs and primary ticker")
    p.add_argument("--pairs-only", action="store_true", help="Refresh ladder pair caches only (skip primary reload)")
    args = p.parse_args()
    path = run_ladder(refresh=args.refresh or args.pairs_only)
    print(f"Research ladder report: {path}")
    print(f"Artifacts: {path.parent}/")


if __name__ == "__main__":
    main()

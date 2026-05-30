#!/usr/bin/env python3
"""
Summarize available computational screening results for MHSI candidates.

Reads mock or real result files from data/results/ if present; otherwise
reports that no computational results are available yet.
"""

from __future__ import annotations

from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"
PLACEHOLDER_MSG = (
    "No computational results yet. Run DFT/phonon workflows after "
    "structures and inputs are prepared."
)


def main() -> None:
    if not RESULTS_DIR.exists():
        print(PLACEHOLDER_MSG)
        return

    result_files = sorted(RESULTS_DIR.glob("*"))
    result_files = [p for p in result_files if p.is_file() and p.name != ".gitkeep"]

    if not result_files:
        print(PLACEHOLDER_MSG)
        return

    print("Computational screening summary")
    print("-" * 40)
    for path in result_files:
        print(f"  {path.name}")


if __name__ == "__main__":
    main()

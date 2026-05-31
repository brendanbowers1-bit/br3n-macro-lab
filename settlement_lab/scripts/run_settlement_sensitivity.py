#!/usr/bin/env python3
"""Run settlement sensitivity analysis."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.models.sensitivity import run_sensitivity_analysis, sensitivity_summary
from src.utils.paths import OUTPUTS_DIR


def main() -> None:
    print("BR3N Settlement Economics Lab — sensitivity")
    results = run_sensitivity_analysis()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUTS_DIR / "sensitivity_results.csv"
    results.to_csv(path, index=False)
    summary = sensitivity_summary(results)
    summary.to_csv(OUTPUTS_DIR / "rank_stability.csv", index=False)
    print(f"Saved: {path} ({len(results)} rows)")
    if not summary.empty:
        print(summary.head(10).to_string(index=False))


if __name__ == "__main__":
    main()

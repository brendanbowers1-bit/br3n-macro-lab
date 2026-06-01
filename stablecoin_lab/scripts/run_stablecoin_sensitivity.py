#!/usr/bin/env python3
"""Run stablecoin sensitivity analysis."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_stablecoin_dataset
from src.models.sensitivity import run_sensitivity_analysis
from src.utils.paths import OUTPUTS_DIR


def main() -> None:
    print("Bowers Frontier Stablecoin Settlement Window Lab — sensitivity")
    ds = build_stablecoin_dataset()
    results = run_sensitivity_analysis(ds)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUTS_DIR / "stablecoin_sensitivity_results.csv", index=False)
    print(f"  {len(results)} rows → {OUTPUTS_DIR / 'stablecoin_sensitivity_results.csv'}")


if __name__ == "__main__":
    main()

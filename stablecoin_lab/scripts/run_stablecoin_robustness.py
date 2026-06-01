#!/usr/bin/env python3
"""Run stablecoin robustness checks."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_stablecoin_dataset
from src.models.robustness import run_robustness_checks
from src.utils.paths import OUTPUTS_DIR, REPORTS_DIR


def main() -> None:
    print("Bowers Frontier Stablecoin Settlement Window Lab — robustness")
    ds = build_stablecoin_dataset()
    results = run_robustness_checks(
        ds.get("stablecoin_finality_quality_outputs"),
        ds.get("stablecoin_value_survival_outputs"),
        ds.get("compliance_settlement_drag_outputs"),
        ds.get("settlement_window_compression_outputs"),
        ds.get("stablecoin_dollarization_outputs"),
    )
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUTS_DIR / "stablecoin_robustness_results.csv", index=False)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "tables").mkdir(parents=True, exist_ok=True)
    print(f"  {len(results)} checks → {OUTPUTS_DIR / 'stablecoin_robustness_results.csv'}")


if __name__ == "__main__":
    main()

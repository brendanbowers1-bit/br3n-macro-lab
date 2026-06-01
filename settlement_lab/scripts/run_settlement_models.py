#!/usr/bin/env python3
"""Run settlement lab models including stress scenarios."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data.build_dataset import build_settlement_dataset
from src.models.empirical_tests import run_empirical_tests
from src.models.stress_scenarios import run_stress_scenarios
from src.utils.paths import OUTPUTS_DIR


def main() -> None:
    print("Bowers Frontier Settlement Economics Lab — run models")
    ds = build_settlement_dataset()
    mock = bool(ds["_mock_data_flag"]["mock_data_flag"].iloc[0])
    stress = run_stress_scenarios(ds["payment_fragility_outputs"])
    emp = run_empirical_tests(ds.get("features", pd.DataFrame()), mock_flag=mock)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    stress.to_csv(OUTPUTS_DIR / "stress_scenario_results.csv", index=False)
    if not emp["tests"].empty:
        emp["tests"].to_csv(OUTPUTS_DIR / "empirical_tests.csv", index=False)
    if emp.get("warning"):
        print(f"  {emp['warning']}")
    print(f"Stress scenarios: {len(stress)} rows → {OUTPUTS_DIR / 'stress_scenario_results.csv'}")


if __name__ == "__main__":
    main()

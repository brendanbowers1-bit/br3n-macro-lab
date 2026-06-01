#!/usr/bin/env python3
"""Run stablecoin lab models and empirical tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_stablecoin_dataset
from src.models.empirical_tests import run_empirical_tests
from src.utils.paths import OUTPUTS_DIR


def main() -> None:
    print("Bowers Frontier Stablecoin Settlement Window Lab — run models")
    ds = build_stablecoin_dataset()
    mock = bool(ds["_mock_data_flag"]["mock_data_flag"].iloc[0])
    emp = run_empirical_tests(ds.get("features"), mock_flag=mock)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if not emp["tests"].empty:
        emp["tests"].to_csv(OUTPUTS_DIR / "empirical_tests.csv", index=False)
    if emp.get("warning"):
        print(f"  {emp['warning']}")
    print(f"Empirical tests: {len(emp['tests'])} rows → {OUTPUTS_DIR / 'empirical_tests.csv'}")


if __name__ == "__main__":
    main()

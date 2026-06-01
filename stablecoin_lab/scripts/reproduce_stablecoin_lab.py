#!/usr/bin/env python3
"""Reproduce full stablecoin lab pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = [
    "fetch_stablecoin_data.py",
    "validate_stablecoin_data.py",
    "build_stablecoin_dataset.py",
    "run_stablecoin_indices.py",
    "run_stablecoin_models.py",
    "run_stablecoin_sensitivity.py",
    "run_stablecoin_robustness.py",
    "make_stablecoin_visuals.py",
]


def main() -> None:
    print("Bowers Frontier Stablecoin Settlement Window Lab — reproduce all")
    failed = []
    for script in STEPS:
        print(f"\n▶ {script}")
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=str(ROOT))
        if r.returncode != 0:
            failed.append(script)
    if failed:
        print(f"\nFailed: {failed}")
        sys.exit(1)
    print("\nReproduction complete.")
    print("Dashboard: streamlit run src/dashboard/app.py")


if __name__ == "__main__":
    main()

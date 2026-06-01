#!/usr/bin/env python3
"""Reproduce full settlement lab pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = [
    "fetch_settlement_data.py",
    "validate_settlement_data.py",
    "build_settlement_dataset.py",
    "run_settlement_indices.py",
    "run_settlement_models.py",
    "run_settlement_sensitivity.py",
    "run_settlement_robustness.py",
    "make_settlement_visuals.py",
]


def main() -> None:
    print("Bowers Frontier Settlement Economics Lab — reproduce all")
    failed = []
    for script in STEPS:
        print(f"\n▶ {script}")
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=str(ROOT))
        if r.returncode != 0:
            failed.append(script)
    if failed:
        print(f"Failed: {failed}")
        sys.exit(1)
    print("\nReproduction complete.")


if __name__ == "__main__":
    main()

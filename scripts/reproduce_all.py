#!/usr/bin/env python3
"""Reproduce full VSI research pipeline end-to-end."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ("build_dataset.py", "Build processed datasets"),
    ("run_vsi.py", "Compute Value Survival Index"),
    ("run_sensitivity.py", "Sensitivity analysis"),
    ("run_robustness.py", "Robustness checks"),
    ("make_visuals.py", "Generate figures"),
]


def main() -> None:
    print("BR3N Value Survival Index — Full Reproduction")
    print("=" * 60)

    failed = []
    for script, desc in STEPS:
        print(f"\n▶ {desc} ({script})")
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script)],
            cwd=str(ROOT),
        )
        if r.returncode != 0:
            failed.append(script)
            print(f"  FAILED: {script}")
        else:
            print(f"  OK: {script}")

    print("\n" + "=" * 60)
    if failed:
        print(f"Reproduction incomplete — failed: {', '.join(failed)}")
        sys.exit(1)
    print("Reproduction complete.")
    print("Dashboard: streamlit run src/dashboard/app.py")
    print("See REPLICATION.md for data acquisition and checksums.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Full data-lake pipeline: ingest → validate → corridor → canonical → validate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def _run(script: str, *args: str) -> None:
    cmd = [PY, str(ROOT / "scripts" / script), *args]
    print(f"\n==> {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> None:
    _run("ingest_fred_policy_rate.py", "--min-date", "2024-01-01")
    _run("ingest_banxico_fx.py", "--min-date", "2024-01-01")
    _run("ingest_banxico_policy_rate.py", "--min-date", "2024-01-01")
    _run("ingest_rpw_remittance_cost.py")
    _run("validate_data_lake.py")
    _run("run_corridor_intelligence.py")
    _run("build_usd_mxn_canonical.py")
    _run("validate_data_lake.py")
    print("\nrun_data_lake_pipeline PASS")


if __name__ == "__main__":
    main()

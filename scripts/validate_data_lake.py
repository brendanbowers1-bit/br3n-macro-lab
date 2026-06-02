#!/usr/bin/env python3
"""Validate data-lake raw and processed assets."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.lake.validate import run_all_validations, write_reports


def main() -> None:
    reports = run_all_validations()
    if not reports:
        print("No data-lake assets found to validate.")
        raise SystemExit(1)

    paths = write_reports(reports)
    failed = [r for r in reports if not r.passed]
    for r in reports:
        status = "PASS" if r.passed else "FAIL"
        print(f"{status}  {r.layer:10}  {r.target}  errors={r.summary.get('errors', 0)} warnings={r.summary.get('warnings', 0)}")

    print(f"\nWrote {len(paths)} report(s) to data-lake/metadata/validation_reports/")
    if failed:
        raise SystemExit(1)
    print("validate_data_lake PASS")


if __name__ == "__main__":
    main()

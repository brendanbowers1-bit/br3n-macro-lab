#!/usr/bin/env python3
"""Sync module outputs to medallion folders and build DuckDB catalog."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_lake.catalog import build_duckdb_catalog, sync_medallion_files


def main() -> int:
    counts = sync_medallion_files()
    print(f"Medallion sync: gold={counts['gold']} silver={counts['silver']} skipped={counts['skipped']}")
    db = build_duckdb_catalog()
    print(f"DuckDB catalog: {db.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

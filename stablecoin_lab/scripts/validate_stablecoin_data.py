#!/usr/bin/env python3
"""Validate stablecoin lab data quality."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_stablecoin_dataset
from src.quality.validation import validate_all_tables


def main() -> None:
    print("BR3N Stablecoin Settlement Window Lab — validate data")
    ds = build_stablecoin_dataset()
    tables = {k: v for k, v in ds.items() if not k.startswith("_")}
    val = validate_all_tables(tables)
    print(val.to_string(index=False))
    sys.exit(0 if val["valid"].all() else 1)


if __name__ == "__main__":
    main()

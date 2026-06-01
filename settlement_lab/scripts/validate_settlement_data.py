#!/usr/bin/env python3
"""Validate settlement lab data quality and metadata."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_settlement_dataset


def main() -> None:
    print("Bowers Frontier Settlement Economics Lab — validate data")
    ds = build_settlement_dataset()
    val = ds["_validation"]
    print(val.to_string(index=False))
    if not val["valid"].all():
        print("\nVALIDATION FAILED")
        sys.exit(1)
    print("\nAll tables passed validation.")


if __name__ == "__main__":
    main()

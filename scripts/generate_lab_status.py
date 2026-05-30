#!/usr/bin/env python3
"""Generate reports/LAB_STATUS.md from latest lab outputs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.lab_status import write_lab_status


def main() -> None:
    path = write_lab_status()
    print(f"Lab status written: {path}")


if __name__ == "__main__":
    main()

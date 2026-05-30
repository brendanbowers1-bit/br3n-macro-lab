#!/usr/bin/env python3
"""Generate model zoo markdown report."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.model_zoo_reporting import generate_model_zoo_report


def main() -> None:
    path = generate_model_zoo_report(ROOT)
    print(f"Report written: {path}")


if __name__ == "__main__":
    main()

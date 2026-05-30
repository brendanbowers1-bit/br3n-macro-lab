#!/usr/bin/env python3
"""Generate multi-corridor roadmap markdown report."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.corridor_reporting import generate_corridor_roadmap_report


def main() -> None:
    path = generate_corridor_roadmap_report(ROOT)
    print(f"Report: {path}")


if __name__ == "__main__":
    main()

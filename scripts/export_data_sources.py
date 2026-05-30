#!/usr/bin/env python3
"""Export data source registry and print upgrade plan."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_sources import export_data_source_registry, print_data_source_plan


def main() -> None:
    path = export_data_source_registry()
    print(f"Exported {path}")
    print()
    print_data_source_plan()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build explicit data-quality manifest for all FX Lab series."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_quality_layer import save_data_quality_layer


def main() -> None:
    paths = save_data_quality_layer()
    print("\nBR3N Macro Labs — Data Quality Layer")
    print("=" * 50)
    for key, path in paths.items():
        print(f"  {key}: {path}")


if __name__ == "__main__":
    main()

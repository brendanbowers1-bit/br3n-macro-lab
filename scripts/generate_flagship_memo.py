#!/usr/bin/env python3
"""Generate USD/MXN flagship memo, working paper outline, and investor one-pager."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.flagship_memo import generate_all_flagship_documents


def main() -> None:
    paths = generate_all_flagship_documents()
    print("\nBowers Frontier Macro Labs — Flagship Documents")
    print("=" * 50)
    for key, path in paths.items():
        print(f"  {key}: {path}")


if __name__ == "__main__":
    main()

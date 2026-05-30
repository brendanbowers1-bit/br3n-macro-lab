#!/usr/bin/env python3
"""Generate publishable research note and one-pager from ladder outputs."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.publication import build_publication


def main() -> None:
    paths = build_publication()
    print("Publication package written:")
    for name, path in paths.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()

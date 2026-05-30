#!/usr/bin/env python3
"""Run full academic research pipeline."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import load_config
from src.research_runner import run_full_research_pipeline


def main() -> None:
    cfg = load_config()
    paths = run_full_research_pipeline(cfg)
    print("\nOutputs:")
    for name, path in paths.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()

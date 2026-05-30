#!/usr/bin/env python3
"""Run multi-corridor remittance FX research roadmap."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.corridor_runner import run_corridor_roadmap
from src.data_loader import load_config


def main() -> None:
    cfg = load_config()
    if not cfg.get("corridors", {}).get("enabled", True):
        print("Corridors disabled in config.yaml")
        sys.exit(0)

    print("\nBR3N Macro Labs — Remittance Corridor Roadmap")
    print("=" * 50)
    paths = run_corridor_roadmap(cfg)
    print("\nOutputs:")
    for name, p in paths.items():
        print(f"  {name}: {p}")
    print("\nNext: python scripts/generate_corridor_report.py")


if __name__ == "__main__":
    main()

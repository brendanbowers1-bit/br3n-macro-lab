#!/usr/bin/env python3
"""
Full lab expansion pipeline:
  macro refresh → ladder (all pairs) → reports → publication site
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    p = argparse.ArgumentParser(description="Run full Bowers Frontier Macro Labs expansion pipeline")
    p.add_argument("--refresh", action="store_true", help="Re-download FX pairs and macro data")
    p.add_argument("--push", action="store_true", help="Git commit and push publication after build")
    args = p.parse_args()

    from src.ladder.runner import run_ladder
    from src.publication import build_publication
    from src.site_builder import build_site

    print("=== Research ladder ===")
    ladder_path = run_ladder(refresh=args.refresh)
    print(f"Ladder: {ladder_path}")

    print("\n=== Publication ===")
    build_publication()

    print("\n=== Site ===")
    site_paths = build_site()
    for k, v in site_paths.items():
        print(f"  {k}: {v}")

    if args.push:
        import subprocess

        subprocess.run(
            ["git", "add", "config.yaml", "reports", "data/processed/macro_panel.csv"],
            cwd=ROOT,
            check=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "Expand dataset: pairs, macro, per-pair economics"],
            cwd=ROOT,
            check=False,
        )
        subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=False)
        print("\nPushed to origin/main — GitHub Pages will rebuild.")


if __name__ == "__main__":
    main()

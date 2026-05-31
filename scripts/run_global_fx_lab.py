#!/usr/bin/env python3
"""Build all flagship indices and save outputs. Research-only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.fetch_public import build_all_public_data
from src.indices.pipeline import run_all_indices, save_index_outputs
from src.research.report_generator import generate_all_reports


def main() -> None:
    print("BR3N Global FX & Remittance Research Lab — Stage 2 pipeline")
    print("=" * 60)
    print("Step 1: Build/fetch public data files…")
    build_all_public_data()
    print("Step 2: Compute flagship indices…")
    indices = run_all_indices()
    paths = save_index_outputs(indices)
    for name, p in paths.items():
        print(f"  index_{name}: {p} ({len(indices[name])} rows)")
    reports = generate_all_reports()
    print(f"\nGenerated {len(reports)} methodology reports")
    print("\nLaunch dashboard: streamlit run src/global_fx_research_lab.py")
    print("Publication: python scripts/build_site.py")


if __name__ == "__main__":
    main()

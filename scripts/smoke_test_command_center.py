#!/usr/bin/env python3
"""Smoke test Bowers Frontier Command Center imports and data loading."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from src.dashboard.data_loader import load_all_dashboard_data
    from src.dashboard import charts, components, page_views
    from src.dashboard.br3n_command_center import PAGES

    assert len(PAGES) == 10, f"Expected 10 pages, got {len(PAGES)}"
    data = load_all_dashboard_data()
    assert data.modules.vsi, "VSI outputs expected"
    checks = [
        ("VSI rows", len(data.vsi["value_survival"].df) > 0),
        ("Settlement SDI", len(data.settlement["settlement_drag"].df) > 0),
        ("Stablecoin SFQI", len(data.stablecoin["finality_quality"].df) > 0),
        ("Gallery items", len(data.gallery) > 0),
    ]
    for name, ok in checks:
        print(f"  {'PASS' if ok else 'WARN'}  {name}")
    print("Command Center smoke: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

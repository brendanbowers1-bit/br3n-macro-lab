#!/usr/bin/env python3
"""Build canonical USD/MXN daily table in data-lake/processed/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.lake.paths import CORRIDOR_DAILY_JSON
from src.lake.usd_mxn_canonical import build_usd_mxn_canonical, canonical_summary


def main() -> None:
    json_src = ROOT / "data" / "outputs" / "us_mx_corridor_daily.json"
    if not json_src.exists():
        json_src = CORRIDOR_DAILY_JSON if CORRIDOR_DAILY_JSON.exists() else None

    df = build_usd_mxn_canonical(corridor_json_src=json_src)
    summary = canonical_summary(df)
    print(json.dumps(summary, indent=2))
    print("build_usd_mxn_canonical PASS")


if __name__ == "__main__":
    main()

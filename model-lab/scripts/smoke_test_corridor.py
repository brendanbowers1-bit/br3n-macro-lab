#!/usr/bin/env python3
"""Smoke test: corridor pipeline produces validated JSON and brief."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.run_corridor_intelligence import run


def main() -> None:
    payload = run()
    assert payload["validation"]["passed"] is True
    assert 0 <= payload["risk_score"]["score"] <= 100
    json_path = ROOT / "data" / "outputs" / "us_mx_corridor_daily.json"
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert len(data["series"]["remittance_usd_millions"]) >= 12
    briefs = list((ROOT / "model-lab" / "outputs" / "briefs").glob("us_mx_corridor_*.md"))
    assert briefs, "Expected generated brief markdown"
    print("model:smoke PASS")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Smoke test: corridor pipeline produces validated JSON, brief, and canonical parquet."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.lake.ingest_fred import ingest_fred_policy_rate
from src.lake.paths import FED_POLICY_CSV, REMITTANCES_CSV, USD_MXN_DAILY_PARQUET
from scripts.run_corridor_intelligence import run


def main() -> None:
    if not FED_POLICY_CSV.exists():
        print("==> Ingesting FRED DFEDTARU...")
        ingest_fred_policy_rate(min_date="2024-01-01")
    if not REMITTANCES_CSV.exists():
        raise FileNotFoundError(f"Missing {REMITTANCES_CSV}")

    payload = run()
    assert payload["validation"]["passed"] is True
    assert 0 <= payload["risk_score"]["score"] <= 100
    json_path = ROOT / "data" / "outputs" / "us_mx_corridor_daily.json"
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert len(data["series"]["remittance_usd_millions"]) >= 12
    briefs = list((ROOT / "model-lab" / "outputs" / "briefs").glob("us_mx_corridor_*.md"))
    assert briefs, "Expected generated brief markdown"
    assert USD_MXN_DAILY_PARQUET.exists(), "Expected canonical parquet in data-lake"
    print("model:smoke PASS")


if __name__ == "__main__":
    main()

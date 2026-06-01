#!/usr/bin/env python3
"""Unit tests for corridor intelligence pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.corridor_intelligence.dataset import load_us_mx_remittances
from src.corridor_intelligence.risk_score import compute_corridor_risk_score
from src.corridor_intelligence.validate import validate_us_mx_dataset


def test_load_and_validate():
    df = load_us_mx_remittances()
    report = validate_us_mx_dataset(df)
    assert report.passed
    assert report.row_count == 23


def test_score_bounds():
    df = load_us_mx_remittances()
    report = validate_us_mx_dataset(df)
    score = compute_corridor_risk_score(df, data_quality_score=report.data_quality_score)
    assert 0 <= score.score <= 100
    assert score.metrics["latest_flow_usd_millions"] > 0


def main() -> None:
    test_load_and_validate()
    test_score_bounds()
    print("model:test PASS (2 tests)")


if __name__ == "__main__":
    main()

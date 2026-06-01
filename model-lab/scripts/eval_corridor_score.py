#!/usr/bin/env python3
"""Evaluate corridor risk score stability on validated dataset."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.corridor_intelligence.dataset import load_us_mx_remittances
from src.corridor_intelligence.risk_score import compute_corridor_risk_score
from src.corridor_intelligence.validate import validate_us_mx_dataset


def main() -> None:
    df = load_us_mx_remittances()
    validation = validate_us_mx_dataset(df)
    score = compute_corridor_risk_score(df, data_quality_score=validation.data_quality_score)

    assert validation.passed
    assert score.band in ("Low", "Moderate", "Elevated")
    assert sum(score.weights.values()) == 1.0

    print(f"Corridor Risk Score: {score.score} ({score.band})")
    for k, v in score.components.items():
        print(f"  {k}: {v}")
    print("model:eval PASS")


if __name__ == "__main__":
    main()

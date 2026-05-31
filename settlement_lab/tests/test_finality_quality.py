"""Tests for Finality Quality Index."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_fqi_bounded():
    from src.data.build_dataset import build_settlement_dataset
    fqi = build_settlement_dataset()["finality_quality_outputs"]
    assert (fqi["finality_quality_index"] >= 0).all()
    assert (fqi["finality_quality_index"] <= 100).all()

"""Tests for settlement lab data quality."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_quality_score_range():
    from src.data.mock_data import create_mock_dataset
    ds = create_mock_dataset()
    for _, df in ds.items():
        assert (df["data_quality_score"] >= 0).all()
        assert (df["data_quality_score"] <= 100).all()


def test_mock_quality_cap():
    from src.data.mock_data import create_mock_dataset
    from src.config.research_settings import MOCK_MAX_QUALITY_SCORE
    ds = create_mock_dataset()
    for _, df in ds.items():
        assert (df["data_quality_score"] <= MOCK_MAX_QUALITY_SCORE).all()

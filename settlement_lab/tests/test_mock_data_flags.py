"""Tests for mock data flags."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_mock_source_id():
    from src.data.mock_data import create_mock_dataset
    from src.config.research_settings import MOCK_SOURCE_ID
    ds = create_mock_dataset()
    for _, df in ds.items():
        assert (df["source_id"] == MOCK_SOURCE_ID).all()


def test_mock_grade():
    from src.data.mock_data import create_mock_dataset
    ds = create_mock_dataset()
    for _, df in ds.items():
        assert (df["data_quality_grade"] == "Demo only").all()

"""Tests for mock data flags."""

from __future__ import annotations


def test_mock_source_id():
    from src.config.research_settings import MOCK_SOURCE_ID
    from src.data.mock_data import create_mock_dataset

    ds = create_mock_dataset()
    for _, df in ds.items():
        assert (df["source_id"] == MOCK_SOURCE_ID).all()


def test_mock_grade():
    from src.data.mock_data import create_mock_dataset

    ds = create_mock_dataset()
    for _, df in ds.items():
        assert (df["data_quality_grade"] == "Demo only").all()


def test_mock_flag_set():
    from src.data.mock_data import create_mock_dataset

    ds = create_mock_dataset()
    for name, df in ds.items():
        assert df["mock_data_flag"].all(), f"{name} not all mock"

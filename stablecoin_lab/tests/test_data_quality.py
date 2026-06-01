"""Tests for stablecoin lab data quality."""

from __future__ import annotations


def test_quality_score_range():
    from src.data.mock_data import create_mock_dataset

    ds = create_mock_dataset()
    for _, df in ds.items():
        assert (df["data_quality_score"] >= 0).all()
        assert (df["data_quality_score"] <= 100).all()


def test_mock_quality_cap():
    from src.config.research_settings import MOCK_MAX_QUALITY_SCORE
    from src.data.mock_data import create_mock_dataset

    ds = create_mock_dataset()
    for _, df in ds.items():
        assert (df["data_quality_score"] <= MOCK_MAX_QUALITY_SCORE).all()


def test_validation_passes():
    from src.data.build_dataset import build_stablecoin_dataset

    val = build_stablecoin_dataset()["_validation"]
    assert val["valid"].all()

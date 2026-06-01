"""Tests for Stablecoin Finality Quality Index."""

from __future__ import annotations


def test_sfqi_bounded():
    from src.data.build_dataset import build_stablecoin_dataset

    sfqi = build_stablecoin_dataset()["stablecoin_finality_quality_outputs"]
    assert (sfqi["stablecoin_finality_quality_index"] >= 0).all()
    assert (sfqi["stablecoin_finality_quality_index"] <= 100).all()


def test_sfqi_not_ledger_only():
    from src.data.build_dataset import build_stablecoin_dataset

    sfqi = build_stablecoin_dataset()["stablecoin_finality_quality_outputs"]
    assert "economic_finality_score" in sfqi.columns
    assert "ledger_finality_score" in sfqi.columns

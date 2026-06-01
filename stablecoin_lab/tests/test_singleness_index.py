"""Tests for Tokenized Money Singleness Index."""

from __future__ import annotations


def test_singleness_index_bounded():
    from src.data.build_dataset import build_stablecoin_dataset

    sing = build_stablecoin_dataset()["tokenized_money_singleness_outputs"]
    assert (sing["singleness_index"] >= 0).all()
    assert (sing["singleness_index"] <= 100).all()


def test_singleness_components_present():
    from src.data.build_dataset import build_stablecoin_dataset

    sing = build_stablecoin_dataset()["tokenized_money_singleness_outputs"]
    assert "price_parity_score" in sing.columns

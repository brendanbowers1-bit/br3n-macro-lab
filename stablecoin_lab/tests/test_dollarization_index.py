"""Tests for Stablecoin Dollarization Index."""

from __future__ import annotations


def test_dollarization_index_bounded():
    from src.data.build_dataset import build_stablecoin_dataset

    sdi = build_stablecoin_dataset()["stablecoin_dollarization_outputs"]
    assert (sdi["stablecoin_dollarization_index"] >= 0).all()
    assert (sdi["stablecoin_dollarization_index"] <= 100).all()

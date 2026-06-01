"""Tests for Settlement Window Compression model."""

from __future__ import annotations


def test_swc_scores_bounded():
    from src.data.build_dataset import build_stablecoin_dataset

    swc = build_stablecoin_dataset()["settlement_window_compression_outputs"]
    assert (swc["swc_extended"] >= 0).all()
    assert (swc["swc_extended"] <= 100).all()


def test_swc_time_reduction_non_negative():
    from src.data.build_dataset import build_stablecoin_dataset

    swc = build_stablecoin_dataset()["settlement_window_compression_outputs"]
    assert (swc["settlement_time_reduction_pct"] >= 0).all()

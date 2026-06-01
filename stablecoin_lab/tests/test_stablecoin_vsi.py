"""Tests for Stablecoin Value Survival Index."""

from __future__ import annotations


def test_stablecoin_vsi_bounded():
    from src.data.build_dataset import build_stablecoin_dataset

    vsi = build_stablecoin_dataset()["stablecoin_value_survival_outputs"]
    assert (vsi["stablecoin_vsi"] >= 0).all()
    assert (vsi["stablecoin_vsi"] <= 100).all()


def test_traditional_vsi_bounded():
    from src.data.build_dataset import build_stablecoin_dataset

    vsi = build_stablecoin_dataset()["stablecoin_value_survival_outputs"]
    assert (vsi["traditional_vsi"] >= 0).all()
    assert (vsi["traditional_vsi"] <= 100).all()

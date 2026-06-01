"""Tests for Stablecoin Liquidity Transformation model."""

from __future__ import annotations


def test_slt_score_bounded():
    from src.data.build_dataset import build_stablecoin_dataset

    slt = build_stablecoin_dataset()["liquidity_transformation_outputs"]
    assert (slt["stablecoin_liquidity_transformation_score"] >= 0).all()
    assert (slt["stablecoin_liquidity_transformation_score"] <= 100).all()


def test_slt_components_present():
    from src.data.build_dataset import build_stablecoin_dataset

    slt = build_stablecoin_dataset()["liquidity_transformation_outputs"]
    for col in ("user_liquidity_benefit_score", "issuer_reserve_burden_score"):
        assert col in slt.columns

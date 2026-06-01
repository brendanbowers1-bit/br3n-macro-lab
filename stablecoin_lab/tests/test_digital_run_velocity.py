"""Tests for Digital Run Velocity model."""

from __future__ import annotations


def test_drv_score_bounded():
    from src.data.build_dataset import build_stablecoin_dataset

    drv = build_stablecoin_dataset()["digital_run_velocity_outputs"]
    assert (drv["digital_run_velocity_score"] >= 0).all()
    assert (drv["digital_run_velocity_score"] <= 100).all()


def test_drv_regime_labels():
    from src.data.build_dataset import build_stablecoin_dataset

    drv = build_stablecoin_dataset()["digital_run_velocity_outputs"]
    assert drv["run_regime"].isin({"low", "elevated", "high", "extreme"}).all()

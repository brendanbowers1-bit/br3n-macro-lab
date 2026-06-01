"""Tests for Compliance Settlement Drag index."""

from __future__ import annotations


def test_compliance_drag_hours_non_negative():
    from src.data.build_dataset import build_stablecoin_dataset

    csd = build_stablecoin_dataset()["compliance_settlement_drag_outputs"]
    assert (csd["compliance_drag_hours"] >= 0).all()


def test_compliance_drag_index_bounded():
    from src.data.build_dataset import build_stablecoin_dataset

    csd = build_stablecoin_dataset()["compliance_settlement_drag_outputs"]
    assert (csd["compliance_drag_index"] >= 0).all()
    assert (csd["compliance_drag_index"] <= 100).all()

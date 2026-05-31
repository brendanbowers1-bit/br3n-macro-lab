"""Tests for Settlement Drag Index."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_sdi_no_negative_lag():
    from src.data.build_dataset import build_settlement_dataset
    flows = build_settlement_dataset()["payment_flow_observations"]
    assert (flows["settlement_lag_days"] >= 0).all()


def test_sdi_bounded():
    from src.data.build_dataset import build_settlement_dataset
    sdi = build_settlement_dataset()["settlement_drag_outputs"]
    assert (sdi["settlement_drag_index"] >= 0).all()
    assert (sdi["settlement_drag_index"] <= 100).all()

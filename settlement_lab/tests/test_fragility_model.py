"""Tests for Payment Network Fragility."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_fragility_bounded():
    from src.data.build_dataset import build_settlement_dataset
    pnf = build_settlement_dataset()["payment_fragility_outputs"]
    assert (pnf["payment_network_fragility_score"] >= 0).all()
    assert (pnf["payment_network_fragility_score"] <= 100).all()


def test_stress_scenarios():
    from src.models.stress_scenarios import run_stress_scenarios
    from src.data.build_dataset import build_settlement_dataset
    stress = run_stress_scenarios(build_settlement_dataset()["payment_fragility_outputs"])
    assert not stress.empty

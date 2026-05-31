"""Tests for operational liquidity burden."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_olb_ratio_non_negative():
    from src.data.build_dataset import build_settlement_dataset
    olb = build_settlement_dataset()["operational_liquidity_outputs"]
    assert (olb["liquidity_burden_ratio"] >= 0).all()


def test_olb_zero_settlement_safe():
    from src.indices.operational_liquidity import calculate_operational_liquidity_row
    import pandas as pd
    r = calculate_operational_liquidity_row(pd.Series({"average_daily_settlement_value_usd": 0}))
    assert r["liquidity_burden_ratio"] == 0

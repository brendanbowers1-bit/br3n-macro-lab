#!/usr/bin/env python3
"""Smoke tests for Settlement Economics Lab."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_mock_flags():
    from src.data.mock_data import create_mock_dataset
    ds = create_mock_dataset()
    for name, df in ds.items():
        assert df["mock_data_flag"].all(), f"{name} not all mock"
        assert (df["data_quality_score"] <= 30).all(), f"{name} mock quality too high"


def test_sdi_bounded():
    from src.data.build_dataset import build_settlement_dataset
    sdi = build_settlement_dataset()["settlement_drag_outputs"]
    assert (sdi["settlement_drag_index"] >= 0).all()
    assert (sdi["settlement_drag_index"] <= 100).all()


def test_fqi_bounded():
    from src.data.build_dataset import build_settlement_dataset
    fqi = build_settlement_dataset()["finality_quality_outputs"]
    assert (fqi["finality_quality_index"] >= 0).all()
    assert (fqi["finality_quality_index"] <= 100).all()


def test_olb_zero_safe():
    from src.indices.operational_liquidity import calculate_operational_liquidity_row
    import pandas as pd
    r = calculate_operational_liquidity_row(pd.Series({"average_daily_settlement_value_usd": 0}))
    assert r["liquidity_burden_ratio"] == 0


def test_metadata_present():
    from src.data.build_dataset import build_settlement_dataset
    flows = build_settlement_dataset()["payment_flow_observations"]
    for col in ("source_id", "methodology_version", "data_quality_score", "data_quality_grade"):
        assert col in flows.columns


def test_validation_passes():
    from src.data.build_dataset import build_settlement_dataset
    val = build_settlement_dataset()["_validation"]
    assert val["valid"].all()


def test_imports():
    import src.dashboard.app  # noqa: F401


def test_curated_not_all_mock():
    from src.data.loaders import parent_lab_has_data, load_all_tables
    if not parent_lab_has_data():
        return
    tables = load_all_tables()
    flows = tables["payment_flow_observations"]
    assert not flows["mock_data_flag"].all(), "expected curated/bridged rows when parent lab has data"


def test_pfi_validation_when_rpw():
    from src.data.build_dataset import build_settlement_dataset
    from src.data.loaders import parent_lab_has_data
    if not parent_lab_has_data():
        return
    ds = build_settlement_dataset()
    pfi_val = ds.get("_pfi_validation", pd.DataFrame())
    if isinstance(pfi_val, pd.DataFrame) and not pfi_val.empty:
        assert "observed_rpw_cost_pct" in pfi_val.columns


def main() -> None:
    tests = [test_mock_flags, test_sdi_bounded, test_fqi_bounded, test_olb_zero_safe,
             test_metadata_present, test_validation_passes, test_imports,
             test_curated_not_all_mock, test_pfi_validation_when_rpw]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
    sys.exit(0 if passed == len(tests) else 1)


if __name__ == "__main__":
    main()

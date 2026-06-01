#!/usr/bin/env python3
"""Smoke tests for BR3N Stablecoin Settlement Window Lab."""

from __future__ import annotations

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


def test_sfqi_bounded():
    from src.data.build_dataset import build_stablecoin_dataset
    sfqi = build_stablecoin_dataset()["stablecoin_finality_quality_outputs"]
    assert (sfqi["stablecoin_finality_quality_index"] >= 0).all()
    assert (sfqi["stablecoin_finality_quality_index"] <= 100).all()


def test_sfqi_not_ledger_only():
    from src.data.build_dataset import build_stablecoin_dataset
    sfqi = build_stablecoin_dataset()["stablecoin_finality_quality_outputs"]
    assert "economic_finality_score" in sfqi.columns
    assert "ledger_finality_score" in sfqi.columns


def test_compliance_drag_non_negative():
    from src.data.build_dataset import build_stablecoin_dataset
    csd = build_stablecoin_dataset()["compliance_settlement_drag_outputs"]
    assert (csd["compliance_drag_hours"] >= 0).all()


def test_stablecoin_vsi_bounded():
    from src.data.build_dataset import build_stablecoin_dataset
    vsi = build_stablecoin_dataset()["stablecoin_value_survival_outputs"]
    assert (vsi["stablecoin_vsi"] >= 0).all()
    assert (vsi["stablecoin_vsi"] <= 100).all()


def test_metadata_present():
    from src.data.build_dataset import build_stablecoin_dataset
    supply = build_stablecoin_dataset()["stablecoin_supply"]
    for col in ("source_id", "data_quality_score", "mock_data_flag"):
        assert col in supply.columns


def test_validation_passes():
    from src.data.build_dataset import build_stablecoin_dataset
    val = build_stablecoin_dataset()["_validation"]
    assert val["valid"].all()


def test_imports():
    import src.dashboard.app  # noqa: F401


def test_sensitivity_outputs():
    from src.data.build_dataset import build_stablecoin_dataset
    from src.models.sensitivity import run_sensitivity_analysis
    ds = build_stablecoin_dataset()
    res = run_sensitivity_analysis(ds)
    assert not res.empty


def main() -> None:
    tests = [
        test_mock_flags, test_sfqi_bounded, test_sfqi_not_ledger_only,
        test_compliance_drag_non_negative, test_stablecoin_vsi_bounded,
        test_metadata_present, test_validation_passes, test_imports,
        test_sensitivity_outputs,
    ]
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

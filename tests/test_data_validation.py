from pathlib import Path

import pandas as pd

from src.quality.validation_rules import validate_vsi_outputs
from src.quality.data_validation import run_data_validation


def test_vsi_bounds_on_fixture():
    df = pd.DataFrame([{
        "value_survival_index": 75.0,
        "total_value_loss_pct": 0.25,
        "real_usable_value_delivered_pct": 0.75,
        "value_loss_usd_per_100": 25.0,
        "fee_pct": 0.02,
        "fx_margin_pct": 0.01,
        "mock_data_flag": False,
        "data_quality_score": 85,
        "source_id": "test",
    }])
    issues = validate_vsi_outputs(df)
    assert not issues


def test_mock_data_quality_score_flagged():
    df = pd.DataFrame([{
        "value_survival_index": 50.0,
        "total_value_loss_pct": 0.5,
        "real_usable_value_delivered_pct": 0.5,
        "value_loss_usd_per_100": 50.0,
        "fee_pct": 0.01,
        "fx_margin_pct": 0.01,
        "mock_data_flag": True,
        "data_quality_score": 50,
        "source_id": "mock",
    }])
    issues = validate_vsi_outputs(df)
    assert any("mock" in i.lower() or "quality" in i.lower() for i in issues)


def test_run_data_validation_smoke():
    root = Path(__file__).resolve().parents[1]
    res = run_data_validation(root)
    assert "summary" in res
    assert "rows" in res

import pandas as pd

from src.indices.value_survival import calculate_vsi_row


def test_vsi_bounded_0_100():
    row = pd.Series({
        "fee_pct": 0.02, "fx_margin_pct": 0.02, "inflation_yoy": 0.03,
        "fx_volatility_30d": 0.1, "payout_method": "bank", "mock_data_flag": False,
    })
    out = calculate_vsi_row(row)
    assert 0 <= out["value_survival_index"] <= 100
    assert 0 <= out["total_value_loss_pct"] <= 100
    assert out["value_loss_usd_per_100"] >= 0


def test_vsi_no_negative_impossible_values():
    row = pd.Series({
        "fee_pct": 0.0, "fx_margin_pct": 0.0, "inflation_yoy": 0.0,
        "fx_volatility_30d": 0.05, "mock_data_flag": False,
    })
    out = calculate_vsi_row(row)
    assert out["explicit_fee_loss_pct"] >= 0
    assert out["fx_spread_loss_pct"] >= 0

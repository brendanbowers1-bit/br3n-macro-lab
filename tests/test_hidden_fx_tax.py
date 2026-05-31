import pandas as pd

from src.indices.hidden_fx_tax import calculate_hidden_fx_tax


def test_hidden_fx_tax_non_negative():
    row = pd.Series({
        "fee_pct": 0.02, "fx_margin_pct": 0.03, "transfer_speed_days": 2,
        "fx_volatility_30d": 0.12, "inflation_yoy": 0.04,
    })
    out = calculate_hidden_fx_tax(row)
    assert out["hidden_fx_tax_pct"] >= 0

import pandas as pd

from src.indices.currency_trust import calculate_currency_trust_score


def test_currency_trust_bounded():
    row = pd.Series({"inflation_yoy": 0.05, "fx_volatility_30d": 0.1, "mock_data_flag": True})
    out = calculate_currency_trust_score(row)
    score = out.get("currency_trust_score", out.get("trust_score"))
    assert 0 <= score <= 100

import pandas as pd

from src.indices.dollar_dependency import calculate_dollar_dependency_row


def test_dollar_dependency_bounded():
    macro = pd.Series({"imports_gdp": 0.3, "remittances_gdp": 0.05, "external_debt_gdp": 0.5})
    market = pd.Series({"dollar_pair_share": 0.7, "liquidity_score": 40})
    out = calculate_dollar_dependency_row(macro, market)
    assert 0 <= out["dollar_dependency_score"] <= 100

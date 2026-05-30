import pandas as pd

from src.data_cleaning import sanitize_fx_prices, validate_series


def test_invert_usdcop_when_feed_is_foreign_per_usd():
    # Simulates Yahoo-style inverted COP (0.00025 USD per COP)
    idx = pd.date_range("2020-01-01", periods=100, freq="B")
    p = pd.Series(0.00025, index=idx)
    df = pd.DataFrame({"price": p})
    clean, meta = sanitize_fx_prices(df, "USDCOP=X")
    assert meta["inverted"] is True
    assert 1500 < clean["price"].median() < 6000
    assert validate_series(clean, "USDCOP=X")


def test_repair_spike_on_mxn():
    idx = pd.date_range("2020-01-01", periods=50, freq="B")
    p = pd.Series(18.0, index=idx)
    p.iloc[25] = 180.0  # bad print
    df = pd.DataFrame({"price": p})
    clean, meta = sanitize_fx_prices(df, "USDMXN=X")
    assert meta["spikes_repaired"] >= 1
    assert clean["price"].pct_change().abs().max() < 0.2

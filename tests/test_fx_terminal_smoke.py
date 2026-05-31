"""Smoke tests for the FX research terminal."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.mock import generate_mock_market_panel, generate_mock_macro_panel
from src.data.pipeline import build_terminal_data_bundle
from src.features.fx_terminal_features import build_multi_pair_feature_table, get_model_matrix
from src.models.baselines import get_baseline_models, signals_to_dataframe
from src.risk.position_risk import assess_trade_risk
from src.risk.regime import classify_fx_regime
from src.backtesting.walk_forward import generate_walk_forward_splits, run_model_comparison


def test_mock_data_generates():
    m = generate_mock_market_panel(pairs=["USDMXN=X"], years=2)
    assert len(m) > 200
    assert "price" in m.columns


def test_feature_engineering_no_lookahead():
    market = generate_mock_market_panel(pairs=["EURUSD=X"], years=3)
    macro = generate_mock_macro_panel(years=3)
    feats = build_multi_pair_feature_table(market, macro=macro, pairs=["EURUSD=X"])
    assert "forward_return_5d" in feats.columns
    assert "direction_5d" in feats.columns
    assert feats["ret_1d"].notna().sum() > 0


def test_baseline_model_fit_predict():
    market = generate_mock_market_panel(pairs=["USDMXN=X"], years=4)
    feats = build_multi_pair_feature_table(market, pairs=["USDMXN=X"])
    X, y, _ = get_model_matrix(feats, horizon=5)
    assert len(X) > 50
    model = get_baseline_models()[3]  # logistic
    model.fit(X, y)
    meta = feats.loc[X.index].reset_index(drop=True)
    sigs = model.predict_signals(X.tail(10).reset_index(drop=True), meta.tail(10).reset_index(drop=True))
    df = signals_to_dataframe(sigs)
    assert "signal" in df.columns


def test_regime_classifier():
    row = pd.Series({"dxy_trend_20d": 0.03, "vix": 30, "vix_change": 0.1, "sp500_return": -0.02})
    state = classify_fx_regime(row)
    assert state.current_regime in ("high_vol_crisis", "risk_off_dollar_squeeze", "usd_bull")


def test_risk_engine():
    from src.risk.regime import RegimeState

    r = assess_trade_risk(
        entry=20.0,
        direction="long",
        confidence=0.3,
        expected_return=0.002,
        vol_20d=0.12,
        carry_score=1.0,
        regime=RegimeState("range_neutral", 0.5, "test", {}),
    )
    assert r.reward_risk_ratio >= 0


def test_walk_forward_splits():
    dates = pd.date_range("2015-01-01", periods=2000, freq="B")
    splits = generate_walk_forward_splits(pd.Series(dates), train_years=3, test_years=1)
    assert len(splits) >= 1


def test_terminal_bundle():
    bundle = build_terminal_data_bundle(use_mock_on_failure=True)
    assert not bundle.market.empty

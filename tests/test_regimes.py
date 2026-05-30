"""Basic tests for regime classifier."""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import load_config
from src.regimes import classify_regimes, ALL_REGIMES


def test_regime_labels_exist():
    cfg = load_config()
    idx = pd.date_range("2020-01-01", periods=300, freq="B")
    df = pd.DataFrame(
        {
            "open": 20.0,
            "high": 20.1,
            "low": 19.9,
            "close": 20.0 + pd.Series(range(300)).values * 0.01,
            "volume": 0,
            "ret": 0.001,
            "ma20": 20.0,
            "ma60": 19.5,
            "ma_spread_pct": 0.02,
            "trend_flag": 1,
            "high_vol_flag": False,
            "low_vol_flag": True,
            "realized_vol_20d": 0.1,
            "realized_vol_pct": 0.4,
        },
        index=idx,
    )
    out = classify_regimes(df, cfg)
    assert out["regime"].isin(ALL_REGIMES).all()

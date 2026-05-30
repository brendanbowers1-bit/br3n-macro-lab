"""
Experimental research models — NOT live-trading models.

Tests conditional forecastability using scikit-learn direction classifiers
and simple rule-based regime models.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from .regimes import R1, R2

ROOT = Path(__file__).resolve().parents[1]

FEATURE_COLS = [
    "ma_spread_pct",
    "realized_vol_20d",
    "realized_vol_percentile",
    "trend_flag",
    "high_vol_flag",
    "ret_lag_1",
    "ret_lag_5",
    "ret_lag_20",
]


def baseline_random_walk(df: pd.DataFrame) -> pd.Series:
    """Next return forecast = 0; next price forecast = current price."""
    return pd.Series(0.0, index=df.index)


def regime_conditioned_trend_forecast(df: pd.DataFrame) -> pd.Series:
    """
    Rule model: forecast non-zero return only in R2 when MA trend is clear.
    Otherwise forecast zero (random-walk return).
    """
    pred = pd.Series(0.0, index=df.index)
    in_r2 = df["regime"] == R2
    pred.loc[in_r2 & (df["ma20"] > df["ma60"])] = df.loc[in_r2, "daily_return"].expanding().mean()
    pred.loc[in_r2 & (df["ma20"] < df["ma60"])] = -df.loc[in_r2, "daily_return"].expanding().mean().abs()
    return pred.fillna(0)


def r1_risk_warning(df: pd.DataFrame) -> pd.Series:
    """Risk label: 1 = unstable trend (R1), 0 otherwise. Not a trading signal."""
    return (df["regime"] == R1).astype(int)


def prepare_model_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add lags and 5-day direction target."""
    out = df.copy()
    out["ret_lag_1"] = out["daily_return"].shift(1)
    out["ret_lag_5"] = out["daily_return"].shift(5)
    out["ret_lag_20"] = out["daily_return"].shift(20)
    out["target_return_5d"] = out["price"].pct_change(5).shift(-5)
    out["target_direction_5d"] = (out["target_return_5d"] > 0).astype(int)
    return out.dropna(subset=FEATURE_COLS + ["target_direction_5d", "target_return_5d"])


def train_test_split_time_series(df: pd.DataFrame, train_ratio: float = 0.7) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Chronological split — no shuffle."""
    n = len(df)
    cut = int(n * train_ratio)
    return df.iloc[:cut].copy(), df.iloc[cut:].copy()


def _eval_classifier(name: str, model, X_test, y_test, n_train: int) -> dict:
    pred = model.predict(X_test)
    acc = accuracy_score(y_test, pred)
    warning = ""
    if n_train < 200:
        warning = "Small training sample — treat metrics as illustrative only."
    return {
        "model_name": name,
        "accuracy": round(float(acc), 4),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, pred, zero_division=0)), 4),
        "directional_accuracy": round(float(acc) * 100, 2),
        "observations": len(y_test),
        "warning": warning,
    }


def run_direction_models(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Train logistic, random forest, gradient boosting on 5-day direction."""
    prepared = prepare_model_features(df)
    train_ratio = float(config.get("research", {}).get("train_ratio", 0.7))
    min_train = int(config.get("research", {}).get("min_train_rows", 200))
    train, test = train_test_split_time_series(prepared, train_ratio)

    if len(train) < min_train:
        return pd.DataFrame(
            [{
                "model_name": "ALL",
                "warning": f"Insufficient data: {len(train)} train rows (need {min_train}).",
                "observations": len(test),
            }]
        )

    X_train = train[FEATURE_COLS]
    y_train = train["target_direction_5d"]
    X_test = test[FEATURE_COLS]
    y_test = test["target_direction_5d"]

    models = [
        ("logistic_direction_model", LogisticRegression(max_iter=1000, random_state=42)),
        ("random_forest_direction_model", RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)),
        ("gradient_boosting_direction_model", GradientBoostingClassifier(random_state=42, max_depth=3)),
    ]
    rows = []
    for name, model in models:
        model.fit(X_train, y_train)
        rows.append(_eval_classifier(name, model, X_test, y_test, len(train)))

    # Baseline: always predict majority class
    majority = int(y_train.mode().iloc[0]) if not y_train.empty else 0
    base_pred = np.full(len(y_test), majority)
    rows.append({
        "model_name": "majority_class_baseline",
        "accuracy": round(float((base_pred == y_test).mean()), 4),
        "precision": None,
        "recall": None,
        "f1": None,
        "directional_accuracy": round(float((base_pred == y_test).mean()) * 100, 2),
        "observations": len(y_test),
        "warning": "Naive baseline — not random walk but useful comparator.",
    })
    return pd.DataFrame(rows)


def save_ml_scorecard(df: pd.DataFrame, path: Path | None = None) -> Path:
    path = path or ROOT / "data" / "outputs" / "ml_direction_model_scorecard.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path

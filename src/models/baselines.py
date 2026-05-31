"""
Baseline FX prediction models for the research terminal.

Research-only — outputs signals for benchmarking, not live trading.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.preprocessing import StandardScaler

try:
    import xgboost as xgb

    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    import lightgbm as lgb

    HAS_LGB = True
except ImportError:
    HAS_LGB = False


@dataclass
class ModelSignal:
    pair: str
    date: pd.Timestamp
    signal: str  # long, short, neutral
    probability_up: float
    expected_return: float
    confidence: float
    model_name: str
    feature_importance: dict[str, float] | None = None


class BaseFXModel(ABC):
    name: str = "base"

    @abstractmethod
    def fit(self, X: pd.DataFrame, y_dir: pd.Series, y_ret: pd.Series | None = None) -> "BaseFXModel":
        ...

    @abstractmethod
    def predict_signals(
        self,
        X: pd.DataFrame,
        meta: pd.DataFrame,
        horizon: int = 5,
    ) -> list[ModelSignal]:
        ...


def _signal_from_prob(prob_up: float, threshold: float = 0.55) -> str:
    if prob_up >= threshold:
        return "long"
    if prob_up <= 1 - threshold:
        return "short"
    return "neutral"


class RandomWalkBaseline(BaseFXModel):
    name = "random_walk"

    def fit(self, X, y_dir, y_ret=None):
        self._base_rate = float(y_dir.mean()) if len(y_dir) else 0.5
        return self

    def predict_signals(self, X, meta, horizon=5):
        signals = []
        for i in range(len(X)):
            p = self._base_rate
            signals.append(
                ModelSignal(
                    pair=str(meta.iloc[i]["pair"]),
                    date=pd.Timestamp(meta.iloc[i]["date"]),
                    signal="neutral",
                    probability_up=p,
                    expected_return=0.0,
                    confidence=0.0,
                    model_name=self.name,
                )
            )
        return signals


class MomentumBaseline(BaseFXModel):
    name = "momentum"

    def fit(self, X, y_dir, y_ret=None):
        return self

    def predict_signals(self, X, meta, horizon=5):
        signals = []
        mom = X.get("ret_20d", pd.Series(0, index=X.index)).fillna(0)
        for i in range(len(X)):
            m = float(mom.iloc[i])
            prob = 0.5 + np.clip(m * 5, -0.25, 0.25)
            signals.append(
                ModelSignal(
                    pair=str(meta.iloc[i]["pair"]),
                    date=pd.Timestamp(meta.iloc[i]["date"]),
                    signal=_signal_from_prob(prob),
                    probability_up=prob,
                    expected_return=m,
                    confidence=abs(prob - 0.5) * 2,
                    model_name=self.name,
                    feature_importance={"ret_20d": 1.0},
                )
            )
        return signals


class CarryBaseline(BaseFXModel):
    name = "carry"

    def fit(self, X, y_dir, y_ret=None):
        return self

    def predict_signals(self, X, meta, horizon=5):
        signals = []
        carry = X.get("carry_score", pd.Series(0, index=X.index)).fillna(0)
        for i in range(len(X)):
            c = float(carry.iloc[i])
            prob = 0.5 + np.clip(c / 20, -0.2, 0.2)
            signals.append(
                ModelSignal(
                    pair=str(meta.iloc[i]["pair"]),
                    date=pd.Timestamp(meta.iloc[i]["date"]),
                    signal=_signal_from_prob(prob),
                    probability_up=prob,
                    expected_return=c / 10000,
                    confidence=abs(prob - 0.5) * 2,
                    model_name=self.name,
                    feature_importance={"carry_score": 1.0},
                )
            )
        return signals


class SklearnClassifierModel(BaseFXModel):
    def __init__(self, name: str, estimator: Any):
        self.name = name
        self.estimator = estimator
        self.scaler = StandardScaler()
        self._importance: dict[str, float] | None = None

    def fit(self, X, y_dir, y_ret=None):
        Xs = self.scaler.fit_transform(X)
        self.estimator.fit(Xs, y_dir)
        if hasattr(self.estimator, "feature_importances_"):
            self._importance = dict(zip(X.columns, self.estimator.feature_importances_))
        elif hasattr(self.estimator, "coef_"):
            self._importance = dict(zip(X.columns, np.abs(self.estimator.coef_.ravel())))
        return self

    def predict_signals(self, X, meta, horizon=5):
        Xs = self.scaler.transform(X)
        if hasattr(self.estimator, "predict_proba"):
            probs = self.estimator.predict_proba(Xs)[:, 1]
        else:
            preds = self.estimator.predict(Xs)
            probs = preds.astype(float)
        signals = []
        for i, prob in enumerate(probs):
            prob = float(np.clip(prob, 0, 1))
            exp_ret = float(meta.iloc[i].get(f"forward_return_{horizon}d", 0) or 0)
            signals.append(
                ModelSignal(
                    pair=str(meta.iloc[i]["pair"]),
                    date=pd.Timestamp(meta.iloc[i]["date"]),
                    signal=_signal_from_prob(prob),
                    probability_up=prob,
                    expected_return=exp_ret,
                    confidence=abs(prob - 0.5) * 2,
                    model_name=self.name,
                    feature_importance=self._importance,
                )
            )
        return signals


class RidgeReturnModel(BaseFXModel):
    name = "ridge_fair_value"

    def fit(self, X, y_dir, y_ret=None):
        self.scaler = StandardScaler()
        self.model = Ridge(alpha=1.0)
        if y_ret is None:
            raise ValueError("RidgeReturnModel requires y_ret")
        Xs = self.scaler.fit_transform(X)
        self.model.fit(Xs, y_ret)
        self._importance = dict(zip(X.columns, np.abs(self.model.coef_)))
        return self

    def predict_signals(self, X, meta, horizon=5):
        Xs = self.scaler.transform(X)
        preds = self.model.predict(Xs)
        signals = []
        for i, er in enumerate(preds):
            prob = float(1 / (1 + np.exp(-er * 50)))
            signals.append(
                ModelSignal(
                    pair=str(meta.iloc[i]["pair"]),
                    date=pd.Timestamp(meta.iloc[i]["date"]),
                    signal=_signal_from_prob(prob),
                    probability_up=prob,
                    expected_return=float(er),
                    confidence=min(abs(er) * 100, 1.0),
                    model_name=self.name,
                    feature_importance=self._importance,
                )
            )
        return signals


def clone_baseline_model(model: BaseFXModel) -> BaseFXModel:
    """Fresh model instance for walk-forward folds."""
    if isinstance(model, SklearnClassifierModel):
        return SklearnClassifierModel(model.name, type(model.estimator)())
    if isinstance(model, RidgeReturnModel):
        return RidgeReturnModel()
    return type(model)()


def get_baseline_models() -> list[BaseFXModel]:
    """Return all available baseline models."""
    models: list[BaseFXModel] = [
        RandomWalkBaseline(),
        MomentumBaseline(),
        CarryBaseline(),
        SklearnClassifierModel("logistic_regression", LogisticRegression(max_iter=1000)),
        SklearnClassifierModel("random_forest", RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)),
    ]
    if HAS_XGB:
        models.append(
            SklearnClassifierModel(
                "xgboost",
                xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=4,
                    learning_rate=0.05,
                    eval_metric="logloss",
                    random_state=42,
                ),
            )
        )
    if HAS_LGB:
        models.append(
            SklearnClassifierModel(
                "lightgbm",
                lgb.LGBMClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42, verbose=-1),
            )
        )
    return models


def signals_to_dataframe(signals: list[ModelSignal]) -> pd.DataFrame:
    rows = []
    for s in signals:
        rows.append(
            {
                "pair": s.pair,
                "date": s.date,
                "signal": s.signal,
                "probability_up": s.probability_up,
                "expected_return": s.expected_return,
                "confidence": s.confidence,
                "model_name": s.model_name,
            }
        )
    return pd.DataFrame(rows)

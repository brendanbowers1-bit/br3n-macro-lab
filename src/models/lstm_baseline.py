"""
EUR/USD LSTM baseline adapter — research placeholder.

TODO: Wrap open-source LSTM baseline with Bowers Frontier feature pipeline and walk-forward splits.
Research-only. Not a trading system.
"""


def train_lstm_baseline(config: dict | None = None) -> dict:
    """Train or load LSTM baseline. Not implemented."""
    raise NotImplementedError("LSTM baseline wrapper pending Phase 2 implementation.")


def predict_lstm_baseline(features, model=None) -> dict:
    """Return direction/return forecasts from LSTM baseline. Not implemented."""
    raise NotImplementedError("LSTM baseline wrapper pending Phase 2 implementation.")

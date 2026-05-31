"""
Central registry of open-source FX AI models and frameworks for BR3N benchmarking.

Research-only — not trading systems. Every entry requires OOS validation with costs.
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd

MODEL_REGISTRY: dict[str, dict[str, Any]] = {
    "eurusd_lstm_baseline": {
        "category": "baseline_forecasting",
        "type": "LSTM",
        "title": "EUR/USD LSTM Model",
        "source": "open-source baseline",
        "task": "EUR/USD forecasting",
        "status": "baseline candidate",
        "description": "Classic LSTM time-series model for EUR/USD short-horizon forecasting.",
        "use_case": "Traditional neural-network benchmark under BR3N walk-forward splits.",
        "br3n_improvement": [
            "add carry features",
            "add macro features",
            "add news sentiment",
            "use transaction-cost-aware labels",
            "walk-forward validation",
        ],
    },
    "eurusd_transformer_baseline": {
        "category": "baseline_forecasting",
        "type": "Transformer",
        "title": "EUR/USD TimeSeriesTransformer",
        "source": "open-source baseline",
        "task": "EUR/USD forecasting",
        "status": "baseline candidate",
        "description": "Transformer-based ML model for EUR/USD short-term forecasting.",
        "use_case": "Modern deep-learning benchmark vs BR3N regime models.",
        "br3n_improvement": [
            "add macro features, rate differentials, carry",
            "add news sentiment and volatility regimes",
            "transaction-cost-aware labels",
            "compare against LSTM under same splits",
        ],
    },
    "rogendo_forex_lstm": {
        "category": "baseline_forecasting",
        "type": "LSTM collection",
        "title": "Rogendo Forex LSTM Models",
        "source": "Hugging Face — pair/timeframe-specific LSTMs",
        "task": "Multi-pair forex forecasting",
        "status": "baseline candidate",
        "description": "Collection of pair-specific LSTM forex models on Hugging Face.",
        "use_case": "Test whether pair-specific models beat generalized FX models.",
        "br3n_improvement": [
            "evaluate across major pairs",
            "retrain with BR3N cleaner feature set",
            "same cost and walk-forward standard",
        ],
    },
    "finrl": {
        "category": "reinforcement_learning",
        "type": "RL framework",
        "title": "FinRL / FinRL-X",
        "source": "AI4Finance",
        "task": "trading decision layer (PPO, A2C, DDPG, SAC, TD3)",
        "status": "future trading-layer candidate",
        "description": "Open-source financial RL framework for portfolio and trading decisions.",
        "use_case": "Decision layer after forecast models — long/short/flat/sized positions.",
        "br3n_improvement": [
            "feed forecast confidence, volatility, carry, spread",
            "include drawdown and macro regime in state",
            "optimize risk-adjusted return not raw PnL",
        ],
    },
    "tensortrade": {
        "category": "reinforcement_learning",
        "type": "RL trading framework",
        "title": "TensorTrade",
        "source": "open-source",
        "task": "custom FX trading environments",
        "status": "future environment candidate",
        "description": "Flexible RL framework for custom actions, rewards, and data feeds.",
        "use_case": "FX environments with spreads, slippage, and position sizing.",
        "br3n_improvement": [
            "build custom FX environment",
            "add realistic costs",
            "custom BR3N reward function (Sharpe, drawdown control)",
        ],
    },
    "timesfm": {
        "category": "foundation_models",
        "type": "time-series foundation model",
        "title": "Google TimesFM",
        "source": "Google Research",
        "task": "zero-shot or fine-tuned FX forecasting",
        "status": "experiment candidate",
        "description": "General-purpose open-source time-series foundation model.",
        "use_case": "Zero-shot / fine-tuned benchmark on major FX pairs.",
        "br3n_improvement": [
            "fine-tune on FX + macro + carry",
            "compare against LSTM and Transformer baselines",
        ],
    },
    "lag_llama": {
        "category": "foundation_models",
        "type": "probabilistic foundation model",
        "title": "Lag-Llama",
        "source": "open-source foundation model",
        "task": "probabilistic FX forecasting",
        "status": "experiment candidate",
        "description": "Probabilistic time-series foundation model with uncertainty estimates.",
        "use_case": "Confidence intervals and volatility-aware position sizing.",
        "br3n_improvement": [
            "use uncertainty for position sizing",
            "reduce trades when confidence is low",
        ],
    },
    "chronos": {
        "category": "foundation_models",
        "type": "Transformer foundation model",
        "title": "Chronos / TS Transformer Foundations",
        "source": "open-source / Amazon Chronos family",
        "task": "pretrained time-series forecasting adapted to FX",
        "status": "experiment candidate",
        "description": "Foundation-model approaches for time-series that may adapt to currency markets.",
        "use_case": "Benchmark large pretrained TS models vs smaller FX-specific models.",
        "br3n_improvement": [
            "fine-tune on FX OHLC, rates, macro, news-derived features",
            "walk-forward OOS with cost drag",
        ],
    },
}

CATEGORY_LABELS = {
    "baseline_forecasting": "Baseline FX Forecasting",
    "reinforcement_learning": "Reinforcement Learning Frameworks",
    "foundation_models": "Time-Series Foundation Models",
}


def get_model(model_id: str) -> dict[str, Any]:
    if model_id not in MODEL_REGISTRY:
        raise KeyError(f"Unknown model: {model_id}")
    return {"model_id": model_id, **MODEL_REGISTRY[model_id]}


def list_models(category: Optional[str] = None) -> list[dict[str, Any]]:
    items = [get_model(mid) for mid in MODEL_REGISTRY]
    if category:
        items = [m for m in items if m["category"] == category]
    return items


def models_dataframe() -> pd.DataFrame:
    rows = []
    for mid, meta in MODEL_REGISTRY.items():
        rows.append(
            {
                "model_id": mid,
                "category": meta["category"],
                "title": meta["title"],
                "type": meta["type"],
                "source": meta["source"],
                "status": meta["status"],
                "task": meta["task"],
                "br3n_improvement": "; ".join(meta["br3n_improvement"]),
            }
        )
    return pd.DataFrame(rows)


def registry_summary_markdown() -> str:
    lines = ["# Open Source Model Registry", ""]
    for cat_key, cat_label in CATEGORY_LABELS.items():
        lines.append(f"## {cat_label}")
        lines.append("")
        for m in list_models(cat_key):
            lines.append(f"### {m['title']} (`{m['model_id']}`)")
            lines.append(f"- **Type:** {m['type']}")
            lines.append(f"- **Status:** {m['status']}")
            lines.append(f"- **Use case:** {m['use_case']}")
            lines.append("")
    return "\n".join(lines)

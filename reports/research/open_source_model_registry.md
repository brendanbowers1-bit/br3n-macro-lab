# Open Source FX AI Model Lab

**Borrow. Benchmark. Improve. Explain.**

> Research-only. Not investment advice. No live trading.

Registry implementation: `src/models/model_registry.py`

## Warning

These models are not trading systems by themselves. They are research baselines. Every model must be tested out-of-sample with realistic transaction costs, drawdown controls, and no look-ahead bias before any trading use.

## Core Thesis

Most open-source FX AI models are weak because they only predict the next candle from historical OHLC data. Bowers Frontier FX Lab should improve on them by adding carry, macro, volatility regimes, news sentiment, better labels, transaction costs, and proper walk-forward backtesting.

**Conclusion:** The edge is not copying an open-source FX model. The edge is building a disciplined research pipeline that proves when a model works, when it fails, and why.

See also: `reports/OPEN_SOURCE_FX_AI_MODEL_LAB.md` for full documentation.

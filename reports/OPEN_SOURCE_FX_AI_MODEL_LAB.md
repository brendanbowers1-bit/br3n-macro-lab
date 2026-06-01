# Bowers Frontier Model Lab

**Borrow. Benchmark. Improve. Explain.**

A model-agnostic AI research environment for testing local and hosted models against FX, treasury, settlement, and corridor-risk tasks.

> Research-only. Not investment advice. No live trading.

---

## Core Thesis

Most open-source FX AI models are weak because they only predict the next candle from historical OHLC data. Bowers Frontier FX Lab should improve on them by adding carry, macro, volatility regimes, news sentiment, better labels, transaction costs, and proper walk-forward backtesting.

> **Warning:** These models are not trading systems by themselves. They are research baselines. Every model must be tested out-of-sample with realistic transaction costs, drawdown controls, and no look-ahead bias before any trading use.

> **Conclusion:** The edge is not copying an open-source FX model. The edge is building a disciplined research pipeline that proves when a model works, when it fails, and why.

---

## 1. Baseline FX Forecasting Models

### A. EUR/USD TimeSeriesTransformer

**Description:** A transformer-based machine learning model for EUR/USD short-term forecasting, useful as a modern deep-learning benchmark.

**Use case:** Benchmark Bowers Frontier's own FX models against a direct transformer baseline.

**Improvement idea:** Add macro features, rate differentials, carry, news sentiment, volatility regimes, and transaction-cost-aware labels.

### B. EUR/USD LSTM Model

**Description:** A classic deep-learning time-series model for EUR/USD forecasting using LSTM architecture.

**Use case:** Use as a traditional neural-network benchmark.

**Improvement idea:** Compare LSTM vs Transformer vs foundation models under the same train/test split and trading-cost assumptions.

### C. Rogendo Forex LSTM Models

**Description:** A Hugging Face collection of multiple pair/timeframe-specific LSTM forex models.

**Use case:** Test whether pair-specific models outperform generalized FX models.

**Improvement idea:** Evaluate model quality across major pairs, then retrain using Bowers Frontier's cleaner feature set.

---

## 2. Reinforcement Learning Trading Frameworks

### A. FinRL / FinRL-X

**Description:** An open-source financial reinforcement-learning framework using algorithms such as PPO, A2C, DDPG, SAC, and TD3.

**Use case:** Use after forecasting models are built, as a decision layer that chooses long, short, flat, or reduced-size positions.

**Improvement idea:** Do not let the RL agent blindly trade price candles. Feed it forecast confidence, volatility, carry, spread, drawdown, and macro regime.

### B. TensorTrade

**Description:** A flexible open-source reinforcement-learning framework for custom trading environments, actions, rewards, and data feeds.

**Use case:** Build custom FX trading environments with realistic spreads, slippage, and position sizing.

**Improvement idea:** Create Bowers Frontier-specific reward functions based on risk-adjusted return, drawdown control, Sharpe ratio, and capital preservation.

---

## 3. Time-Series Foundation Models

### A. Google TimesFM

**Description:** A general-purpose open-source time-series foundation model that can be tested on FX forecasting tasks.

**Use case:** Zero-shot or fine-tuned FX forecasting benchmark.

**Improvement idea:** Compare TimesFM against LSTM and Transformer baselines on major FX pairs.

### B. Lag-Llama

**Description:** An open-source probabilistic time-series foundation model for forecasting with uncertainty estimates.

**Use case:** Generate probabilistic forecasts, confidence intervals, and volatility-aware trading signals.

**Improvement idea:** Use forecast uncertainty to reduce position size when model confidence is low.

### C. Chronos / Time-Series Transformer Foundation Models

**Description:** General foundation-model approaches for time-series forecasting that may be adapted to currency markets.

**Use case:** Benchmark whether large pretrained time-series models beat smaller FX-specific models.

**Improvement idea:** Fine-tune on FX OHLC, rates, macro, and news-derived features.

---

## 4. Bowers Frontier Improvement Layer

What Bowers Frontier FX Lab adds beyond open-source models:

### A. Carry Features

- interest-rate differentials
- forward points
- central bank policy rates
- yield spreads
- positive or negative carry

### B. Macro Features

- inflation
- unemployment
- GDP
- PMI
- trade balance
- fiscal stress
- central bank policy expectations

### C. Market Regime Features

- VIX
- DXY
- US 10-year yield
- oil
- gold
- equity risk sentiment
- realized volatility
- trend regime
- mean-reversion regime
- crisis regime

### D. News and Sentiment Features

- central bank speeches
- FOMC / ECB / BOJ tone
- geopolitical risk
- inflation surprise language
- rate-cut / rate-hike expectations
- crisis headlines
- country-specific political risk

### E. Better Labels

Instead of predicting next close, label trades using:

- next 1-hour return
- next 4-hour return
- next 1-day return
- risk-adjusted return
- return after spread and slippage
- direction only when move exceeds cost threshold
- no-trade label when edge is too small

### F. Better Backtesting

- walk-forward validation
- out-of-sample testing
- no look-ahead bias
- realistic spreads
- slippage
- max drawdown
- Sharpe ratio
- Sortino ratio
- win rate
- average win/loss
- profit factor
- regime-specific performance
- pair-specific performance

---

## 5. Architecture — Bowers Frontier FX Lab v1

```
Bowers Frontier FX Lab v1
├── Baselines
│   ├── EUR/USD LSTM
│   ├── EUR/USD TimeSeriesTransformer
│   ├── TimesFM
│   ├── Lag-Llama
│   └── FinRL / TensorTrade
│
├── Data Layer
│   ├── OHLCV
│   ├── interest-rate differentials
│   ├── forward points / carry
│   ├── DXY / VIX / yields
│   ├── macro indicators
│   └── news sentiment
│
├── Signal Engine
│   ├── direction probability
│   ├── expected return
│   ├── volatility forecast
│   ├── carry score
│   └── confidence score
│
├── Trading Layer
│   ├── long / short / flat
│   ├── position sizing
│   ├── stop-loss logic
│   ├── drawdown controls
│   └── transaction costs
│
└── Research Dashboard
    ├── accuracy
    ├── Sharpe
    ├── Sortino
    ├── max drawdown
    ├── win rate
    ├── average win/loss
    ├── profit factor
    └── regime performance
```

---

## 6. Research Questions

- Do time-series foundation models outperform traditional LSTM and Transformer models in FX?
- Does adding interest-rate carry improve directional accuracy?
- Does news sentiment improve short-term FX prediction after central bank events?
- Are models better at predicting trend continuation or mean reversion?
- Which pairs are most predictable: EUR/USD, USD/JPY, GBP/USD, AUD/USD, USD/MXN, or USD/INR?
- Does the model still work after transaction costs?
- Can a model know when not to trade?
- Can Bowers Frontier FX Lab explain why a trade works instead of only predicting direction?

---

## 7. Benchmarking Standard

Every model must be judged by:

- same currency pair
- same timeframe
- same train/test split
- same transaction cost assumptions
- same evaluation dates
- same risk limits
- same walk-forward testing method

**Metrics:** directional accuracy, precision on trade signals, recall on trade signals, Sharpe ratio, Sortino ratio, max drawdown, average win, average loss, win rate, profit factor, turnover, transaction cost drag, performance by regime.

---

## 8. Practical Build Roadmap

| Phase | Deliverable |
|-------|-------------|
| **Phase 1** | Add model registry and documentation page |
| **Phase 2** | Implement baseline LSTM and Transformer model wrappers |
| **Phase 3** | Add TimesFM and Lag-Llama experiment notebooks or placeholder adapters |
| **Phase 4** | Add macro/carry/news feature pipeline |
| **Phase 5** | Build walk-forward backtesting engine |
| **Phase 6** | Add model comparison dashboard |
| **Phase 7** | Add trade explanation engine |
| **Phase 8** | Publish Bowers Frontier FX Lab research notes |

---

## 9. Project Folder Structure

```
src/
  data/                    (via data/ at repo root)
    raw/
    processed/
    macro/
    news/
  features/
    carry_features.py      → src/carry_features.py (existing)
    macro_features.py
    volatility_features.py → src/features.py (regime/vol)
    news_sentiment_features.py → src/news_features.py (existing)
  models/
    model_registry.py
    lstm_baseline.py
    transformer_baseline.py
    timesfm_adapter.py
    lag_llama_adapter.py
    finrl_agent.py
    tensortrade_env.py
  backtesting/
    walk_forward.py
    transaction_costs.py
    risk_metrics.py
    regime_analysis.py
  dashboard/
    model_comparison.py
    trade_explainer.py
  research/                → reports/research/
    open_source_model_registry.md
    benchmark_standard.md
    research_questions_os_models.md
```

Registry: `src/models/model_registry.py`

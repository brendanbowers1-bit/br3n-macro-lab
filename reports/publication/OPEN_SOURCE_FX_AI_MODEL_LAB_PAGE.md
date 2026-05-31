# Open Source FX AI Model Lab

## Borrow. Benchmark. Improve. Explain.

> Research-only. Not investment advice. No live trading.

---

## Core Thesis

Most open-source FX AI models are weak because they only predict the next candle from historical OHLC data. BR3N FX Lab improves on them by adding **carry**, **macro**, **volatility regimes**, **news sentiment**, **better labels**, **transaction costs**, and **proper walk-forward backtesting**.

> **Warning:** These models are not trading systems by themselves. They are research baselines. Every model must be tested out-of-sample with realistic transaction costs, drawdown controls, and no look-ahead bias before any trading use.

> **Conclusion:** The edge is not copying an open-source FX model. The edge is building a disciplined research pipeline that proves when a model works, when it fails, and why.

---

## 1. Baseline FX Forecasting Models

### EUR/USD TimeSeriesTransformer
Transformer-based ML for EUR/USD short-term forecasting. **Use:** modern deep-learning benchmark vs BR3N models. **Improve:** macro, carry, news, regimes, cost-aware labels.

### EUR/USD LSTM Model
Classic LSTM for EUR/USD. **Use:** traditional neural benchmark. **Improve:** compare LSTM vs Transformer vs foundation models on same splits and costs.

### Rogendo Forex LSTM Models
Hugging Face collection of pair/timeframe LSTMs. **Use:** test pair-specific vs generalized models. **Improve:** evaluate major pairs; retrain on BR3N feature set.

---

## 2. Reinforcement Learning Frameworks

### FinRL / FinRL-X
Financial RL (PPO, A2C, DDPG, SAC, TD3). **Use:** decision layer after forecasts. **Improve:** feed confidence, vol, carry, spread, drawdown — not raw candles alone.

### TensorTrade
Custom trading environments, actions, rewards. **Use:** FX envs with spreads and slippage. **Improve:** BR3N reward = risk-adjusted return, drawdown control, Sharpe.

---

## 3. Time-Series Foundation Models

### Google TimesFM
General-purpose TS foundation model. **Use:** zero-shot / fine-tuned FX benchmark. **Improve:** fine-tune on FX + macro + carry; compare to LSTM/Transformer.

### Lag-Llama
Probabilistic foundation model with uncertainty. **Use:** confidence intervals and vol-aware signals. **Improve:** size down when confidence is low.

### Chronos / TS Transformer Foundations
Pretrained time-series models adaptable to FX. **Use:** benchmark large pretrained vs small FX-specific models. **Improve:** fine-tune on OHLC, rates, macro, news.

---

## 4. BR3N Improvement Layer

| Layer | Features |
|-------|----------|
| **Carry** | rate differentials, forward points, policy rates, yield spreads |
| **Macro** | inflation, unemployment, GDP, PMI, trade balance, fiscal stress |
| **Regime** | VIX, DXY, yields, oil, gold, equity risk, realized vol, trend/range/crisis |
| **News** | central bank tone, geopolitical risk, inflation language, political risk |
| **Labels** | multi-horizon returns, cost-adjusted returns, no-trade when edge < cost |
| **Backtest** | walk-forward, OOS, no look-ahead, spreads, slippage, regime metrics |

---

## 5. Architecture — BR3N FX Lab v1

```
BR3N FX Lab v1
├── Baselines
│   ├── EUR/USD LSTM
│   ├── EUR/USD TimeSeriesTransformer
│   ├── TimesFM
│   ├── Lag-Llama
│   └── FinRL / TensorTrade
├── Data Layer
│   ├── OHLCV
│   ├── interest-rate differentials
│   ├── forward points / carry
│   ├── DXY / VIX / yields
│   ├── macro indicators
│   └── news sentiment
├── Signal Engine
│   ├── direction probability
│   ├── expected return
│   ├── volatility forecast
│   ├── carry score
│   └── confidence score
├── Trading Layer
│   ├── long / short / flat
│   ├── position sizing
│   ├── stop-loss logic
│   ├── drawdown controls
│   └── transaction costs
└── Research Dashboard
    ├── accuracy · Sharpe · Sortino · max drawdown
    ├── win rate · avg win/loss · profit factor
    └── regime performance
```

---

## 6. Research Questions

- Do foundation models beat LSTM and Transformer in FX?
- Does carry improve directional accuracy?
- Does news help after central bank events?
- Trend continuation vs mean reversion — which is more predictable?
- Most predictable pair: EUR/USD, USD/JPY, GBP/USD, AUD/USD, USD/MXN, USD/INR?
- Does edge survive transaction costs?
- Can a model know when **not** to trade?
- Can BR3N explain **why** a trade works?

---

## 7. Benchmarking Standard

Same pair · timeframe · train/test split · costs · dates · risk limits · walk-forward method.

Metrics: directional accuracy, precision/recall on signals, Sharpe, Sortino, max drawdown, win rate, profit factor, turnover, cost drag, performance by regime.

---

## 8. Build Roadmap

| Phase | Deliverable |
|-------|-------------|
| 1 | Model registry + documentation (this page) |
| 2 | LSTM + Transformer wrappers |
| 3 | TimesFM + Lag-Llama adapters |
| 4 | Macro / carry / news feature pipeline |
| 5 | Walk-forward backtesting engine |
| 6 | Model comparison dashboard |
| 7 | Trade explanation engine |
| 8 | Published research notes |

---

## 9. Project Structure

```
src/models/          — registry, baselines, adapters, RL stubs
src/backtesting/     — walk-forward, costs, risk metrics, regimes
src/carry_features.py
src/news_features.py
src/features.py      — volatility / regime features
reports/research/    — benchmark standard, research questions
```

See `src/models/model_registry.py` for the live registry.

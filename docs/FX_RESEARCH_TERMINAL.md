# FX Research Terminal

Institutional-grade local-first FX research system for BR3N Macro Labs.

**Research and education only. Not investment advice. No live trading.**

---

## What it does

| Layer | Purpose |
|-------|---------|
| **Data** | Spot FX, macro, rates/carry, sentiment placeholders |
| **Features** | Price, carry, vol, macro — no look-ahead bias |
| **Models** | Random walk, momentum, carry, logistic, RF, XGB/LGBM |
| **Backtest** | Walk-forward OOS comparison |
| **Regime** | Rule-based USD/carry/crisis classifier |
| **Risk** | Stops, sizing, reward/risk gates |
| **LLM** | Ollama memos, news/CB classification, sanity checks |
| **Dashboard** | Overview, pair detail, corridors, model lab, news lab |

## Core pairs

EUR/USD, GBP/USD, USD/JPY, USD/CAD, USD/MXN, USD/BRL, USD/INR, USD/PHP, USD/COP (+ DXY via macro panel)

## Corridors

US→Mexico, India, Philippines, Colombia, Brazil, Guatemala, El Salvador, Dominican Republic, Europe→Africa, Gulf→South Asia

---

## Folder structure

```
data/
  raw/           # Vendor CSV drops
  processed/     # Cached spot series
  features/      # Terminal feature tables
  outputs/       # Model comparison CSVs

src/
  data/          # Terminal data layer (wraps data_loader)
  features/      # fx_terminal_features.py
  models/        # baselines.py + open-source registry
  backtesting/   # walk_forward.py, risk_metrics.py
  risk/          # regime.py, position_risk.py
  llm/           # Ollama client, prompts, memos
  dashboard/     # model_comparison stubs
  utils/         # paths, config

notebooks/
  fx_research_starter.ipynb

reports/
  trade_memos/   # LLM-generated memos

scripts/
  run_fx_research_terminal.py
```

Note: `src/backtest.py` (legacy) is kept separate from `src/backtesting/` to avoid import conflicts.

---

## Quick start

```bash
cd ~/fx_regime_lab
source .venv/bin/activate
pip install -r requirements.txt

# Run pipeline (data → features → walk-forward comparison)
python scripts/run_fx_research_terminal.py

# Launch terminal dashboard
streamlit run src/fx_research_terminal.py

# Smoke tests
pytest tests/test_fx_terminal_smoke.py -q
```

## LLM setup

See [LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md).

---

## Placeholder / mock data

| Component | Status |
|-----------|--------|
| Spot FX | Uses cached `data/processed/*.csv` or yfinance; mock on failure |
| Macro (DXY, VIX, yields) | FRED/Yahoo via `macro_loader`; mock fallback |
| Per-pair policy rates | **Mock** — wire FRED/OECD in Phase 2 |
| CFTC positioning | **Placeholder** zeros |
| News / CB tone scores | **Placeholder** zeros; LLM classifies pasted text |
| USDCAD, USDGTQ | May use mock if Yahoo unavailable |

---

## Next steps for real API integration

1. Wire FRED series for US 2Y/10Y and foreign policy rates per pair
2. Add CFTC COT CSV ingest for USD positioning
3. Connect GDELT / RSS to `news_sentiment_features.py`
4. Add forward points from broker CSV for carry economics
5. Unify walk-forward with `src/research_ladder` splits
6. Optional: Hidden Markov Model regime layer (`hmmlearn`)

---

## Disclaimer

This system is for research and education only. It does not provide financial advice. FX trading involves substantial risk. Backtests are not guarantees of future results. Models may be wrong, overfit, stale, or affected by missing data. Always validate signals against real market data, transaction costs, liquidity, and risk limits.

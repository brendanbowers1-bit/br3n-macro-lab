# BR3N Macro Labs — FX Lab

**Testing When Currency Markets Become Less Random**

FX Lab is the flagship research program of BR3N Macro Labs — an independent AI-assisted research lab studying **when currency markets become conditionally forecastable** by regime.

**Not investment advice.** No live trading. No broker API.

FX Lab research is for education, analysis, and risk-framing only.

BR3N Macro Labs is an independent research project. It is not affiliated with, endorsed by, or sponsored by any employer, university, financial institution, payment company, data vendor, or research institution unless explicitly stated.

---

## FX Lab

Research-only system to study **when FX pairs are more forecastable** by market regime.

**Not investment advice.** No live trading. No broker API.

FX Lab research is for education, analysis, and risk-framing only.

## Install

```bash
cd ~/fx_regime_lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python scripts/run_usdmxn_backtest.py
python scripts/run_research_models.py      # academic research layer
python scripts/run_hedge_policy_tests.py   # hedge policies only
python scripts/run_under_tested_research.py  # hedge governance, flow proxies, RW validity
python scripts/run_corridor_roadmap.py       # multi-corridor remittance roadmap
python scripts/run_fx_desk_framework.py      # FX desk decision scorecards and memos
python scripts/generate_corridor_report.py   # corridor roadmap markdown report
python scripts/export_data_sources.py       # data source registry
python scripts/run_data_quality.py          # data quality report
python scripts/fetch_tier1_official.py      # Tier 1 USD/MXN via FRED H.10
python scripts/generate_report.py
python scripts/run_research_ladder.py   # eight-level evidence ladder
python scripts/build_publication.py     # markdown memo + one-pager
python scripts/build_site.py --open     # styled HTML site (best for sharing)
python scripts/serve_publication.py     # local URL http://127.0.0.1:8765
streamlit run src/dashboard.py          # live dashboard + Research Note page
streamlit run src/luxury_dashboard.py     # high-end institutional research terminal
```

## High-End Dashboard

Run:

```bash
streamlit run src/luxury_dashboard.py
```

The dashboard includes:

- Executive Overview
- Random-Walk Lab
- Regime Intelligence
- Corridor Roadmap
- Hedge Governance
- Flow Pressure
- Academic Tests
- Data Quality
- FX Desk Command Center
- Publication Memo

Design purpose:
The dashboard is built for research review, investor/pilot conversations, academic framing, and treasury risk discussions.

**Disclaimer:** This dashboard is for research and risk-framing only. It is not investment advice and does not place trades.

## Research ladder (Levels 1–6)

| Level | Module | Question |
|-------|--------|----------|
| 1 | `src/ladder/level1_descriptive.py` | Do returns differ by regime? |
| 2 | `src/ladder/level2_oos.py` | Beat random walk OOS on fixed splits? |
| 3 | `src/ladder/level3_multipair.py` | Works on other FX pairs? |
| 4 | `src/ladder/level4_forecast.py` | Better forecast errors (MAE, RMSE, DM)? |
| 5 | `src/ladder/level5_economic.py` | Economic value after frictions? |
| 6 | `src/ladder/level6_snooping.py` | Data-snooping control / holdout |

Outputs: `reports/research_ladder/RESEARCH_LADDER.md` + CSVs per level.

Additional artifacts:
- `level3_multipair_oos.csv` — fixed-split OOS per pair
- `level3_oos_by_pair.csv` / `level3_oos_summary.csv`
- `level6_white_reality_check.csv` — White (2000) bootstrap reality check

## Publish

After running the ladder, generate a plain-English research note:

```bash
python scripts/build_publication.py
```

Outputs:
- `reports/publication/FX_REGIME_RESEARCH_NOTE.md` — full memo (~5 min read)
- `reports/publication/ONE_PAGER.md` — executive summary

Copy either file to Substack, LinkedIn, GitHub, or a PDF exporter. Includes disclaimer and reproducibility block.

### Styled HTML site (recommended)

```bash
python scripts/build_site.py --open
```

Opens `reports/publication/index.html` — dark-themed, mobile-friendly, three pages (one-pager, full memo, ladder).

Keep it running locally for easy access:

```bash
python scripts/serve_publication.py
# → http://127.0.0.1:8765
```

### Streamlit (live data + research tab)

```bash
streamlit run src/dashboard.py
```

Use sidebar **Research Note** page for the publication; main page for live charts.

### Share publicly (optional)

Full guide: **[docs/SHARING.md](docs/SHARING.md)**

| Option | URL | Effort |
|--------|-----|--------|
| **GitHub Pages** | `https://you.github.io/br3n-macro-lab/` | Push repo + enable Pages (Actions) |
| **Netlify Drop** | random `*.netlify.app` | Drag `reports/publication/` folder |
| **Streamlit Cloud** | `*.streamlit.app` | Push repo + connect at share.streamlit.io |
| **ngrok** | temporary HTTPS | `ngrok http 8765` while local server runs |

Quick GitHub Pages path:

```bash
python scripts/build_site.py
git add . && git commit -m "Publish BR3N Macro Lab"
git push origin main
# Settings → Pages → Source: GitHub Actions
```

Re-download all pairs (run in Terminal.app, not sandboxed agent):

```bash
python scripts/run_research_ladder.py --refresh
```

**OOS splits (pre-registered in config):**
- Train 2010–2018 → test 2019–2021
- Train 2010–2021 → test 2022–2024  
- Train 2010–2024 → test 2025–2026

## Academic Research Layer

BR3N Macro Labs tests five high-level questions (see `reports/research_questions.md`):

1. When does random walk fail in FX?
2. What creates conditional forecastability?
3. Can payment-flow proxies predict currency pressure?
4. Can regime-based hedging beat static hedge policy?
5. Is FX partly a balance-sheet-constrained market?

The lab **separates**:
- **Forecasting accuracy** (`src/forecast_tests.py`, `src/academic_tests.py`)
- **Trading P&L** (`src/backtest.py`)
- **Hedging usefulness** (`src/hedge_backtest.py`)

A model may fail to beat random walk on RMSE but still help hedge governance by reducing turnover or avoiding over-adjustment in noisy regimes.

| Module | Output |
|--------|--------|
| `src/research_runner.py` | Master pipeline |
| `src/research_models.py` | ML direction models |
| `src/hedge_backtest.py` | Hedge policy scorecard |
| `scripts/run_research_models.py` | Run all research tests |
| `scripts/run_hedge_policy_tests.py` | Hedge tests only |

Outputs in `data/outputs/`:
- `forecast_scorecard.csv`
- `academic_test_results.csv`
- `ml_direction_model_scorecard.csv`
- `hedge_policy_scorecard.csv`
- `hedge_policy_detail.csv`

### Core Academic References

- **Meese & Rogoff (1983)** — *Journal of International Economics*. Establishes the random-walk benchmark problem in FX forecasting.
- **Diebold & Mariano (1995)** — *Journal of Business & Economic Statistics*. Formal test for comparing forecast accuracy.
- **Clark & West (2007)** — *Journal of Econometrics*. Tests for nested forecast models vs benchmarks.
- **Sullivan, Timmermann & White (1999)** — *Journal of Finance*. Data-snooping / bootstrap warning when testing many rules.

## Under-Tested Research Layer

BR3N Macro Labs is testing an applied question that is less saturated than pure FX forecasting:

**Can regime classification improve hedge governance even when exchange-rate forecasts fail to beat random walk?**

The lab tests:
- when not to hedge
- no-change-in-range policy
- regime-based hedge ratios
- public payment-flow proxies
- random-walk validity by regime
- forecast failure versus hedge usefulness

A model may fail as a forecasting model but still be useful as a hedge-governance tool if it reduces unnecessary hedge turnover, avoids over-adjustment in noisy regimes, or improves cost-adjusted risk reduction.

| Module | Output |
|--------|--------|
| `src/flow_proxies.py` | Calendar flow-pressure features |
| `src/flow_pressure_tests.py` | Flow window vs normal-day tests |
| `src/hedge_governance.py` | Hedge governance policies + scorecard |
| `src/random_walk_validity.py` | Regime-specific RW validity map |
| `scripts/run_under_tested_research.py` | Run all under-tested research |

Additional outputs in `data/outputs/`:
- `hedge_governance_scorecard.csv`
- `hedge_governance_detail.csv`
- `flow_pressure_test_results.csv`
- `random_walk_validity_map.csv`
- `data/processed/usdmxn_features_regimes_flow.csv`

## Remittance Corridor Roadmap

BR3N Macro Labs is expanding from USD/MXN into major remittance and payment corridors.

Initial priority corridors:

- U.S. → Mexico / USD/MXN
- U.S. → India / USD/INR
- U.S. → Philippines / USD/PHP
- U.S. → Colombia / USD/COP
- U.S. → Brazil / USD/BRL
- U.S. → Guatemala / USD/GTQ, if data quality allows
- Gulf → India / USD/INR proxy, because AED and SAR are USD-pegged

Research question:
Do major remittance corridors show regime-specific FX behavior around public payment-flow windows?

Important limitation:
Public calendar proxies are not actual payment-flow data. They are exploratory proxies used until official remittance data or legally usable proprietary flow data becomes available.

## Corridor Research Outputs

The corridor roadmap creates:

- `corridor_master_scorecard.csv`
- `corridor_download_log.csv`
- `corridor_random_walk_validity.csv`
- `corridor_flow_pressure_summary.csv`
- `corridor_hedge_governance_summary.csv`
- `corridor_roadmap_report.md`

## Cross-Border Payments FX Desk Decision Framework

BR3N Macro Labs is an independent research lab studying FX regime intelligence, conditional forecastability, payment-corridor risk, and treasury hedge governance.

The framework translates regime research into the core decisions faced by global payments and multi-currency treasury FX desks:

1. What is the true real-time exposure?
2. Should the desk hedge now, later, partially, or not at all?
3. What customer FX spread or pricing posture is appropriate?
4. Can the local currency actually be sourced at the quoted rate?
5. How much local currency should be prefunded?
6. Which bank or liquidity provider should receive the trade?
7. Are there value-date, settlement, weekend, or holiday mismatches?
8. Are forward points and carry costs worth the hedge protection?
9. What happens during a shock?
10. Is the action a real hedge or unauthorized speculation?

```bash
python scripts/run_fx_desk_framework.py
streamlit run src/luxury_dashboard.py
```

Outputs:

- `data/outputs/fx_desk_scorecard.csv`
- `reports/fx_desk_memos/{corridor_id}_fx_desk_memo.md`
- `reports/FX_DESK_DECISION_FRAMEWORK.md`

The deepest lab question is:
How do we turn millions of small customer transfers into a real-time map of global currency pressure, without over-hedging noise or taking unauthorized directional risk?

## Best Data Upgrade Path

For publication-grade corridor research, upgrade from yfinance to:

1. Federal Reserve H.10 / FRED where available.
2. BIS effective exchange rates.
3. World Bank remittance data.
4. Central bank spot/remittance data.
5. Bloomberg/LSEG/FactSet for forwards, swaps, bid/ask, and professional FX data.
6. Legally usable proprietary payment-flow data only with proper authorization.

## Data Strategy

BR3N Macro Labs uses a **four-tier data stack** (Tier 1 = highest quality):

| Tier | Label | Examples |
|------|-------|----------|
| **1** | Official / academic-grade | FRED, Federal Reserve H.10, BIS, IMF, World Bank, central banks |
| **2** | Professional market data | Bloomberg, LSEG/Refinitiv, FactSet, CME, Cboe FX, EBS, 360T, FXall |
| **3** | Proprietary data | Payment flows, order flow, settlement timing, hedge execution data |
| **4** | Prototype data | Yahoo/yfinance, Stooq, free web sources |

**Principle:** Every model should record the data source, **tier number**, and tier label used in the test.

**Warning:** Results on Tier 4 prototype data are not publication-grade until rerun on Tier 1 official sources. Trading/hedging claims require Tier 2 professional data (bid/ask, forwards, execution costs).

```bash
python scripts/export_data_sources.py    # registry + tier plan
python scripts/run_data_quality.py       # quality check (current default: Tier 4)
python scripts/fetch_tier1_official.py     # free Tier 1 USD/MXN via FRED H.10
python scripts/run_self_improvement.py     # score evidence + propose next experiments
python scripts/fetch_bloomberg_spot.py --check  # Bloomberg availability (requires license)
python scripts/fetch_bloomberg_spot.py     # Tier 2 USD/MXN via Bloomberg Terminal
```

See `reports/DATA_STRATEGY.md` and `src/data_sources.py`.

| Module | Output |
|--------|--------|
| `src/data_sources.py` | Source registry and tier metadata |
| `src/data_quality.py` | Price series quality checks |
| `scripts/export_data_sources.py` | Export registry CSV |
| `scripts/run_data_quality.py` | Quality report for processed data |

Outputs:
- `data/outputs/data_source_registry.csv`
- `data/outputs/data_quality_report.csv`

## Self-improvement loop

The lab reviews its own evidence over time — without auto-trading or holdout tuning.

```bash
python scripts/run_self_improvement.py          # fast: score + snapshot
python scripts/run_self_improvement.py --rerun  # re-run pipelines first
```

Each run snapshots scorecards to `data/runs/{run_id}/`, compares to the prior run, and proposes next experiments. See `reports/SELF_IMPROVEMENT.md`.

## What it does

1. Loads `USDMXN=X` (yfinance)
2. Builds features (MA20/60, vol percentile, returns)
3. Labels regimes R1–R4
4. Backtests: buy_and_hold, legacy, flat_range, r2_only, random_walk (flat)
5. Applies **transaction costs** on turnover (config `transaction_cost_bps`)
6. **Walk-forward** when history allows (5y train / 1y test)
7. Hedge-ratio guidance for treasury framing
8. Markdown report + Streamlit dashboard

## Strategy rules

| Strategy | Rule |
|----------|------|
| legacy | Long if MA20>MA60, short if MA20<MA60, 1-day lag |
| flat_range | Trade R1/R2 only; flat in R3/R4 |
| r2_only | Trade R2 only |
| buy_and_hold | Always long |
| random_walk | Always flat (sanity benchmark) |

## Outputs

- `data/outputs/usdmxn_backtest_detail.csv` — full column set
- `data/outputs/strategy_scorecard.csv`
- `reports/usdmxn_regime_report.md`
- `reports/charts/equity_curves.png`

## Limitations

- In-sample bias; walk-forward needs long history
- No forward curve / carry in v1
- Trading P&L ≠ hedge effectiveness

## Config

Edit `config.yaml` for thresholds, costs, walk-forward windows.

## Next edits

- `src/backtest.py` — carry, spread model
- `config.yaml` — `history_years`, `trend_threshold`

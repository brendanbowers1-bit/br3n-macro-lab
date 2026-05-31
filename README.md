# BR3N Macro Labs — FX Lab

**Testing When Currency Markets Become Less Random**

---

## BR3N Value Survival Index: Measuring How Much Value Survives When Money Crosses Borders

**Core thesis:** Foreign exchange is the daily auction of global trust. The Value Survival Index measures how much economic value survives when it crosses from one monetary trust system into another.

**Main formula:**

```
VSI = 100 × Real Usable Value Delivered / Original Value Sent
```

**Cross-border value loss** = explicit fees + FX spread + timing loss + volatility loss + inflation erosion + payout friction + dollar dependency drag + trust discount

Research-only. **Not investment advice.** Not a trading signal. Not a price forecast.

### Quick start

```bash
cd ~/fx_regime_lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/smoke_test.py       # production readiness checks
python scripts/build_dataset.py  # processed tables → data/processed/
python scripts/run_vsi.py          # VSI outputs → data/outputs/
python scripts/make_visuals.py     # charts → reports/figures/
streamlit run src/dashboard/app.py
```

### Data modes

| Mode | Meaning |
|------|---------|
| `real` | Public RPW/KNOMAD/IMF/WB files loaded; formula placeholders remain |
| `mixed` | Some demo + some real tables |
| `demo` | All synthetic seed data — dashboard shows red banner |

Drop official files in `data/raw/` — see [DATA_SOURCES.md](DATA_SOURCES.md).

### Documentation

- [VALUE_SURVIVAL_INDEX.md](VALUE_SURVIVAL_INDEX.md) — index definition
- [METHODOLOGY.md](METHODOLOGY.md) — formulas and limitations
- [Live publication page](https://brendanbowers1-bit.github.io/br3n-macro-lab/value-survival-index.html)

---

## BR3N Settlement Economics Lab

**Core thesis:** Modern economies run on settlement — not just money.

Measures **settlement drag (SDI)**, **operational liquidity burden (OLB)**, **finality quality (FQI)**, **payment-network fragility (PNF)**, and **friction incidence (PFI)**.

Research-only. Not financial advice. Not operational payment guidance.

### Quick start

```bash
cd ~/fx_regime_lab/settlement_lab
source ../.venv/bin/activate
export PYTHONPATH=.
python scripts/smoke_test_settlement_lab.py
python scripts/reproduce_settlement_lab.py
streamlit run src/dashboard/app.py
```

- [README_SETTLEMENT_LAB.md](settlement_lab/README_SETTLEMENT_LAB.md)
- [Live publication page](https://brendanbowers1-bit.github.io/br3n-macro-lab/settlement-economics-lab.html)

---

## Research Quality, Testing, and Audit Trail

Project-wide quality infrastructure covers **both** the Value Survival Index and Settlement Economics Lab.

### Run all quality checks

```bash
python scripts/run_all_quality_checks.py
```

Reports land in `audit/test_reports/`, `audit/data_quality_reports/`, and `audit/model_validation_reports/`.

### Version Control and Backup Workflow

Recommended workflow:

1. `python scripts/create_snapshot.py --reason "before change"`
2. Make edits
3. `python scripts/run_all_quality_checks.py`
4. `python scripts/git_checkpoint.py --message "describe change"`

Snapshots: `_snapshots/YYYYMMDD_HHMMSS_project_snapshot.zip`  
Log: `audit/change_logs/snapshot_log.csv`

```bash
python scripts/create_snapshot.py --reason "before major validation upgrade"
python scripts/list_snapshots.py
python scripts/restore_snapshot.py --snapshot _snapshots/<file>.zip --target restored_project
```

### Time Tracking

```bash
python scripts/time_tracker.py start --task "Value Survival Index validation"
python scripts/time_tracker.py status
python scripts/time_tracker.py stop
python scripts/time_tracker.py report
python scripts/estimate_time_from_git.py   # git-based estimate (labeled)
```

Historical time before the tracker was installed cannot be measured exactly; git-based estimates are labeled as such in `audit/project_metrics/time_report.md`.

### Other quality commands

```bash
python scripts/project_metrics.py          # line counts → audit/project_metrics/
python scripts/validate_all_data.py
python scripts/validate_models.py
python scripts/reproduce_all.py            # full replication + audit/reproducibility_report.md
python scripts/update_change_log.py --type "model validation" --reason "added checks"
make quality                               # Makefile wrapper
```

Dashboard **Quality Command Center** page: `streamlit run src/dashboard/app.py`

---

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
python scripts/run_flagship_research_lane.py  # flagship OOS hedge lane + R1/R2 quality
python scripts/run_corridor_roadmap.py       # multi-corridor remittance roadmap
python scripts/run_fx_desk_framework.py      # FX desk decision scorecards and memos
python scripts/generate_corridor_report.py   # corridor roadmap markdown report
python scripts/export_data_sources.py       # data source registry
python scripts/run_data_quality.py          # data quality report
python scripts/fetch_tier1_official.py      # Tier 1 USD/MXN via FRED H.10
python scripts/generate_report.py
python scripts/run_research_ladder.py   # eight-level evidence ladder
python scripts/run_multipair_hedge_oos.py  # Level 8 multi-pair hedge OOS (pre-registered)
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
- Model Zoo
- Corridor Roadmap
- Hedge Governance
- Flow Pressure
- News & Macro Stress
- Carry & UIP Lab
- Unanswered FX Questions
- FX History
- Academic Tests
- Data Quality
- FX Desk Command Center
- Publication Memo

Design purpose:
The dashboard is built for research review, investor/pilot conversations, academic framing, and treasury risk discussions.

**Disclaimer:** This dashboard is for research and risk-framing only. It is not investment advice and does not place trades.

## Major Unanswered FX Questions

FX Lab is organized around unresolved questions in international finance and FX risk:

1. Why do exchange rates disconnect from fundamentals?
2. Why does uncovered interest parity fail?
3. Is carry a risk premium, anomaly, or liquidity premium?
4. When does random walk fail?
5. Can public flow proxies approximate payment-flow pressure?
6. Can a model fail as a forecast but still help hedging?
7. Why do no-arbitrage relationships break?
8. When does central-bank intervention work?
9. Are high-volatility trends information or forced liquidation?
10. What is the right objective function for corporate FX hedging?
11. Can AI improve FX decisions without improving FX forecasts?

**Core thesis:** The question is not only whether FX can be predicted. The question is whether FX decisions can be improved when prediction fails.

Full document: `reports/UNANSWERED_FX_QUESTIONS.md`  
Registry: `src/research_questions.py`  
Roadmap: `reports/FX_RESEARCH_ROADMAP.md` (generate via `src/research_roadmap_reporting.py`)

```bash
python -c "from src.research_questions import research_questions_dataframe; print(research_questions_dataframe())"
python -c "from pathlib import Path; from src.research_roadmap_reporting import generate_research_roadmap_report; print(generate_research_roadmap_report(Path('.')))"
```

## FX History & Academic Foundations

FX Lab is built on the major milestones in exchange-rate research:

- Hume and specie-flow adjustment
- gold standard
- Purchasing Power Parity
- Bretton Woods
- Mundell-Fleming
- Dornbusch overshooting
- Meese-Rogoff random-walk puzzle
- UIP and carry puzzle
- market microstructure and order flow
- funding stress and CIP breakdown
- machine learning and FX forecasting

The lab’s thesis builds after this history:

Forecasting exchange rates remains extremely difficult, but FX decisions may still improve when regime information is used for hedge governance, risk escalation, and decision discipline.

Full document: `reports/FX_HISTORY_AND_ACADEMIC_FOUNDATIONS.md`  
Public page: `reports/publication/history.html` (build via `python scripts/build_site.py`)

## FX Research Terminal

Local-first institutional FX research dashboard: statistical models, regime analysis, risk engine, and Ollama LLM layer for memos and news classification.

```bash
python scripts/run_fx_research_terminal.py
streamlit run src/fx_research_terminal.py
pytest tests/test_fx_terminal_smoke.py -q
```

Full docs: [docs/FX_RESEARCH_TERMINAL.md](docs/FX_RESEARCH_TERMINAL.md) · LLM setup: [LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md)

## Global FX & Remittance Research Lab

**Who bears the cost when value crosses borders?**

Six flagship indices: Hidden FX Tax, Remittance Welfare Loss, Currency Credibility, Dollar Dependency, Labor Conversion, Currency Stress.

```bash
python scripts/run_global_fx_lab.py
streamlit run src/global_fx_research_lab.py
pytest tests/test_global_fx_lab_smoke.py -q
```

Data guide: [DATA_SOURCES.md](DATA_SOURCES.md)

## Open Source FX AI Model Lab

**Borrow. Benchmark. Improve. Explain.**

Catalog of open-source FX forecasting baselines, RL frameworks, and time-series foundation models for disciplined benchmarking against BR3N models. Not trading systems — research baselines only.

- Registry: `src/models/model_registry.py`
- Full doc: `reports/OPEN_SOURCE_FX_AI_MODEL_LAB.md`
- Public page: `reports/publication/open-source-ai.html`
- Research notes: `reports/research/benchmark_standard.md`, `reports/research/research_questions_os_models.md`

```bash
python -c "from src.models.model_registry import models_dataframe; print(models_dataframe())"
python scripts/build_site.py
```

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

## News and Macro Stress Layer

FX Lab can optionally include news and uncertainty features.

The purpose is **not** to predict FX from headlines. The purpose is to test whether policy uncertainty, geopolitical risk, central-bank news, inflation news, commodity news, and country-specific news intensity help explain when regimes become more dangerous, more structured, or more random-walk-like.

Initial sources:
- FRED Economic Policy Uncertainty (`USEPUINDXD`)
- Geopolitical Risk Index (planned)
- GDELT optional (`news.use_gdelt: true`)
- professional news analytics later if licensed

News is treated as a **regime/risk feature** — not a direct trading signal. All news features require out-of-sample testing.

```bash
python scripts/run_news_layer.py    # FRED uncertainty + optional GDELT
python scripts/run_model_zoo.py     # includes news-aware models when news CSV exists
```

| Module | Output |
|--------|--------|
| `src/news_features.py` | News/uncertainty feature engineering |
| `src/gdelt_news_loader.py` | Optional GDELT open-news loader |
| `src/news_tests.py` | High-news vs normal-day tests |
| `reports/NEWS_DATA_STRATEGY.md` | Architecture and tier rules |

Outputs:
- `data/processed/usdmxn_features_regimes_news.csv`
- `data/outputs/news_feature_test_results.csv`

## Carry & UIP Lab

FX Lab includes a carry research layer.

Interest-rate carry is the return earned or paid from holding one currency against another because of interest-rate differences.

The lab tests whether carry is:
- a return source in stable regimes,
- compensation for crash risk,
- a warning sign when crowded,
- useful for hedge governance,
- or a regime-dependent failure of uncovered interest parity.

**Core question:** Is the failure of uncovered interest parity constant, or is it regime-dependent compensation for liquidity, crash, and balance-sheet risk?

**Important limitation:** Policy-rate differentials are only a proxy. Real hedge economics require forward points, FX swaps, bid/ask spreads, and execution cost data.

```bash
python scripts/run_carry_layer.py    # FRED policy rates + carry features
python scripts/run_model_zoo.py     # includes carry-aware models when carry CSV exists
```

| Module | Output |
|--------|--------|
| `src/carry_features.py` | Carry feature engineering |
| `src/forward_points.py` | Forward point placeholders |
| `src/carry_tests.py` | Carry regime tests |
| `src/carry_models.py` | Carry-aware model zoo |
| `src/carry_hedge_governance.py` | Carry-adjusted hedge policies |
| `reports/CARRY_RESEARCH_FRAMEWORK.md` | Research framework |

Outputs:
- `data/processed/usdmxn_features_regimes_carry.csv`
- `data/outputs/carry_regime_test_results.csv`
- `data/outputs/carry_hedge_governance_scorecard.csv`

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

# Full nightly pipeline (data → news → carry → model zoo → score → LAB_STATUS.md)
bash scripts/run_full_lab_pipeline.sh
python scripts/run_self_improvement.py   # score + snapshot after pipeline
bash scripts/auto_improve_daily.sh       # scheduled daily (install LaunchAgent first)
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

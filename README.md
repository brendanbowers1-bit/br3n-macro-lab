# BR3N Macro Lab

Research-only system to study **when FX pairs are more forecastable** by market regime.

**Not investment advice.** No live trading. No broker API.

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
python scripts/generate_report.py
python scripts/run_research_ladder.py   # six-level evidence ladder
python scripts/build_publication.py     # markdown memo + one-pager
python scripts/build_site.py --open     # styled HTML site (best for sharing)
python scripts/serve_publication.py     # local URL http://127.0.0.1:8765
streamlit run src/dashboard.py          # live dashboard + Research Note page
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

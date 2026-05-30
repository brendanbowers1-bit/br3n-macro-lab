# FX Lab Status

_Generated: 2026-05-30 22:52 UTC_

**Overall health:** `needs_work`

> Research-only. Not investment advice. No live trading.

## Dimension scores

| Dimension | Verdict | Detail |
|-----------|---------|--------|
| data_quality | strong | Tier 1, flag OK, source fred_h10 |
| data_provenance | strong | source=fred_h10, tier=official, provenance_cols=True |
| forecast_vs_random_walk | weak | RMSE beats RW: False; MAE beats RW: False; DM p-value: 0.4834 |
| model_zoo_forecast | strong | 1/19 models beat RW by RMSE; scorecard source=fred_h10 |
| ml_direction | weak | Best directional accuracy: 50.22% (threshold 53%) |
| trading_oos | weak | flat_range positive Sharpe OOS folds: 9/20 |
| hedge_governance | strong | Best policy: fully_hedged (11.365); no_change_in_range turnover win vs regime_based: True |
| news_layer | strong | high-news vol=15.0658%, normal=10.1613% (stress discriminates: True) |
| carry_layer | insufficient_data | Carry placeholders only — add FRED rate series |
| carry_hedge_governance | weak | carry_adjusted=-64.377 vs regime_only=-59.152 |
| data_snooping_control | weak | White Reality Check p-value: 0.5980 (need < 0.05 to reject data mining) |

## Data layer

- **Spot source:** fred_h10 (Official / academic-grade)
- **Quality flag:** OK
- **Observations:** 6183
- **Range:** 2001-09-14 → 2026-05-15
- **FRED vs yfinance correlation:** 0.482037 (agree closely: False)

## News layer (regime/risk feature)

- News-enhanced features: **available**
- High-news vol: 15.0658% vs normal 10.1613%

## Carry layer (regime/risk feature)

- Carry-enhanced features: **available**
- Latest carry proxy: **5.100**
- High carry: False
- Carry fragility: False
- Carry-adjusted regime: `R2_low_carry`
- Forward points: _proxy only (policy rates)_
- High-carry vol: 13.4121% vs low-carry 9.3822%

## Model zoo

- Models beating random walk (RMSE): **1** / 19
- Scorecard data source: `fred_h10`
- Best trading Sharpe (net): `dollar_stress_model` (0.312)

## Hedge governance

- Best policy (US entity long MXN): `fully_hedged` (cost-adj risk reduction: 11.365)
- Best carry-aware hedge policy: `static_50` (-44.633)

## Provenance (USD/MXN scorecard)

- source: `fred_h10`
- data_tier: `official`
- sample_start: `2001-05-22`
- sample_end: `2026-05-22`
- observations: `6267`
- run_timestamp: `2026-05-30T22:46:35+00:00`

## Proposed next experiments

1. **carry_hedge_governance** — Test carry_adjusted_regime under forward_full costs on multi-pair OOS.
   - `python scripts/run_carry_layer.py`
2. **forecast_vs_random_walk** — Test conditional forecastability by regime (Level 4 ladder); do not claim FX prediction.
   - `python scripts/run_research_ladder.py`
3. **trading_oos** — Review transaction costs and flat_range rule; run level5 economic friction tests.
   - `python scripts/run_research_ladder.py`
4. **carry_layer** — Add forward points CSV; compare policy-rate proxy vs executable carry.
   - `python scripts/run_carry_layer.py`
5. **data_snooping_control** — Pre-register next experiment before testing; avoid tuning on holdout 2025–2026.
   - `python scripts/run_research_ladder.py`

## What still limits publication claims

- Forward points and executable bid/ask not in default pipeline
- Forecast models do not reliably beat random walk
- News/carry layers need out-of-sample validation on holdout window
- Level 8 institutional bar not fully cleared under forward_full costs

## Commands

```bash
bash scripts/run_full_lab_pipeline.sh    # full nightly run
python scripts/run_self_improvement.py --rerun
bash scripts/auto_improve_daily.sh       # scheduled daily
```

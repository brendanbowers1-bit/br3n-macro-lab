# Pre-Registration Log

BR3N Macro Labs — FX Lab. Register hypotheses **before** tuning parameters or reading holdout results.

---

## Test Name

R2-Only Vol-Scaled USD/MXN Test

## Date Registered

2026-05-30

## Hypothesis

An R2-only trend model with volatility-scaled position sizing improves drawdown-adjusted trading performance versus the unscaled R2-only model, but may still fail to beat random walk on forecast accuracy.

## Dataset

USD/MXN daily features + regimes (`data/processed/usdmxn_features_regimes_flow.csv` preferred).

## Training Window

Walk-forward train windows per `config.yaml` (`train_years: 5`); fixed MA/regime rules — no parameter search on test.

## Test Window

Walk-forward test windows (`test_years: 1`); fixed OOS ladder splits in `research_ladder.level2_splits`.

## Holdout Window

2025-01-01 → 2026-12-31 (per `research_ladder.holdout`) — **do not tune on this window**.

## Model Rules

- Trade only in `R2_trend_low_vol`
- Direction: +1 if MA20 > MA60, −1 if MA20 < MA60, else 0
- Position size: `target_vol / realized_vol_20d`, clipped to `[0, max_position]`
- Final position: `signal × position_size`
- Flat outside R2

## Parameters Fixed Before Test

- `model_zoo.r2_vol_scaled_target_vol: 0.10`
- `model_zoo.r2_vol_scaled_max_position: 1.0`
- `backtest.transaction_cost_bps: 2.0`
- `backtest.execution_lag_days: 1`

## Primary Metric

Out-of-sample Sharpe net of transaction costs (walk-forward aggregate).

## Secondary Metrics

Max drawdown net, total transaction cost, percent time in market, RMSE vs random walk, MAE vs random walk.

## What Would Count as Support?

- Vol-scaled R2-only beats unscaled `r2_only_model` on OOS Sharpe net **and** max drawdown net
- Improvement survives walk-forward (not only full sample)
- Forecast-error tests still reported honestly even if trading improves

## What Would Count as Failure?

- No improvement vs unscaled R2-only on OOS Sharpe or drawdown
- Higher turnover/costs without risk benefit
- Any claim of forecast superiority without RMSE/MAE beating random walk

## Notes

**Claim discipline:** Even if trading metrics improve, this does **not** prove FX forecastability unless forecast-error tests also improve versus random walk.

---

## Test Name

Multi-Pair Hedge Governance OOS Test

## Date Registered

2026-05-30

## Hypothesis

`no_change_in_range` improves hedge discipline versus `regime_based` on a multi-pair panel: lower turnover and equal or better cost-adjusted risk reduction, **out of sample**, net of realistic hedge costs including forward roll where available.

## Dataset

Daily spot + regime labels for ≥ 10 FX pairs from Tier-1 sources (FRED H.10 or licensed feeds). Pairs: start with `research_ladder.multipair` list; minimum 10 with ≥ 15 years history.

## Training Window

Walk-forward train per pair: `train_years: 5` from `config.yaml`. Regime rules fixed — no parameter search on test windows.

## Test Window

Walk-forward test: `test_years: 1`, rolled across sample. Fixed ladder splits (2019–2021, 2022–2024, 2025–2026) reported separately.

## Holdout Window

2025-01-01 → 2026-12-31 (per `research_ladder.holdout`) — **do not tune on this window**.

## Model Rules

**Policies compared (fixed set):**

- `half_hedged` (static 50%)
- `mostly_hedged` (static 75%)
- `regime_based`
- `no_change_in_range`
- `volatility_triggered`

**Exposure types (minimum 3):**

- `us_entity_long_mxn` (or pair-equivalent receiver exposure)
- `receiver_currency_exposure`
- `usd_liability_exposure` / pair-equivalent USD-liability stress

## Parameters Fixed Before Test

- Regime classification: existing R1–R4 rules from `config.yaml` (no retuning)
- `backtest.transaction_cost_bps: 2.0`
- Hedge turnover cost: existing bps model; forward roll added when data available
- `MAX_DAILY_HEDGE_STEP: 0.10` (from `hedge_governance.py`)

## Primary Metric

Median **cost-adjusted risk reduction** of `no_change_in_range` vs `regime_based` across pairs, **OOS walk-forward aggregate**.

## Secondary Metrics

- Median turnover reduction (`no_change_in_range` vs `regime_based`)
- Max drawdown hedged (OOS)
- Volatility reduction net of costs
- % of pairs where `no_change_in_range` beats static 50% on cost-adjusted risk reduction
- Regret proxy

## What Would Count as Support?

- H8a: `no_change_in_range` beats `regime_based` on cost-adjusted risk reduction OOS on **≥ 50%** of pairs
- H8b: Median turnover reduction **≥ 40%** without worse max drawdown hedged
- H8c: Results hold on **Tier-1 spot only** (no prototype fallback in published scorecards)
- H8d: Forward-point-adjusted costs do **not** reverse ranking vs static 50% / 75%
- H8e: Best policy survives **White Reality Check** on pre-registered policy set (p < 0.05)
- H8f: **≥ 3 exposure types** show consistent turnover discipline

## What Would Count as Failure?

- OOS cost-adjusted risk reduction does not favor `no_change_in_range` on a majority of pairs
- Turnover savings disappear after forward roll / realistic execution costs
- Results driven by one pair or one exposure type only
- White RC fails to reject data-mining on the policy set
- Any upgrade of claim language before all nine Level 8 requirements are **Met**

## Notes

**Claim discipline:** This test is for **hedge governance**, not FX forecastability. Forecast-error tests (Level 4) must still be reported honestly even if hedge discipline improves.

**Level 8 gate:** Partial pass on any requirement keeps claims at **prototype** tier only.

---

## Template (copy for next test)

### Test Name

### Date Registered

### Hypothesis

### Dataset

### Training Window

### Test Window

### Holdout Window

### Model Rules

### Parameters Fixed Before Test

### Primary Metric

### Secondary Metrics

### What Would Count as Support?

### What Would Count as Failure?

### Notes

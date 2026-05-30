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

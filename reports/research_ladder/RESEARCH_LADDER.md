# BR3N Macro Labs — Research Ladder

**Generated:** 2026-05-30 12:46  
**Primary pair:** USDMXN=X  
**Period:** 2004-03-19 → 2026-05-22 (5773 bars)  
**Primary strategy:** flat_range

> Research only. Not investment advice.

---

## Ladder status

| Level | Question | Status |
|-------|----------|--------|
| 1 | Do returns differ by regime? | done |
| 2 | Beat random walk OOS? | done |
| 3 | Works on other pairs? | done |
| 4 | Better forecast errors? | done |
| 5 | Economic value after costs? | partial |
| 6 | Data-snooping control? | done |

---

## Level 1 — Descriptive evidence

**Question:** Do returns differ by regime?

### Spot returns by regime
| regime | pct_time | days | avg_bps_day_spot | sharpe_spot | max_dd_pct_spot |
| --- | --- | --- | --- | --- | --- |
| R1_trend_high_vol | 36.81 | 2125 | 3.28 | 0.501 | -20.09 |
| R2_trend_low_vol | 49.14 | 2837 | -0.6 | -0.169 | -23.06 |
| R3_range_high_vol | 2.67 | 154 | 9.14 | 1.728 | -6.34 |
| R4_range_low_vol | 11.38 | 657 | -0.57 | -0.179 | -13.87 |


### Strategy (flat_range) by regime
| regime | avg_bps_day_flat_range | sharpe_flat_range | max_dd_pct_flat_range |
| --- | --- | --- | --- |
| R1_trend_high_vol | 0.17 | 0.026 | -37.23 |
| R2_trend_low_vol | 1.17 | 0.334 | -21.94 |
| R3_range_high_vol | -0.51 | -9.214 | -0.76 |
| R4_range_low_vol | -0.2 | -5.345 | -1.33 |


---

## Level 2 — Out-of-sample (fixed splits)

**Question:** Does the model beat random walk on unseen data?

Splits: train 2010–2018 → test 2019–2021; roll → test 2022–2024; test 2025–2026.

| split | sample | train_bars | test_bars | test_period | strategy | total_return_pct | sharpe | max_drawdown_pct | beats_random_walk_sharpe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| split_1 | test | 2347 | 783 | 2019-01-01..2021-12-31 | legacy | -1.86 | 0.024 | -18.42 | None |
| split_1 | test | 2347 | 783 | 2019-01-01..2021-12-31 | flat_range | 0.42 | 0.075 | -15.98 | True |
| split_1 | test | 2347 | 783 | 2019-01-01..2021-12-31 | r2_only | 1.67 | 0.112 | -9.54 | None |
| split_1 | test | 2347 | 783 | 2019-01-01..2021-12-31 | random_walk | 0.0 | 0.0 | 0.0 | None |
| split_2 | test | 3130 | 782 | 2022-01-01..2024-12-31 | legacy | 22.34 | 0.625 | -11.62 | None |
| split_2 | test | 3130 | 782 | 2022-01-01..2024-12-31 | flat_range | 10.92 | 0.363 | -13.3 | True |
| split_2 | test | 3130 | 782 | 2022-01-01..2024-12-31 | r2_only | 19.86 | 1.014 | -4.03 | None |
| split_2 | test | 3130 | 782 | 2022-01-01..2024-12-31 | random_walk | 0.0 | 0.0 | 0.0 | None |
| split_3 | test | 3912 | 358 | 2025-01-01..2026-12-31 | legacy | 8.35 | 0.604 | -7.01 | None |
| split_3 | test | 3912 | 358 | 2025-01-01..2026-12-31 | flat_range | 3.82 | 0.317 | -7.07 | True |
| split_3 | test | 3912 | 358 | 2025-01-01..2026-12-31 | r2_only | 8.64 | 1.13 | -3.39 | None |
| split_3 | test | 3912 | 358 | 2025-01-01..2026-12-31 | random_walk | 0.0 | 0.0 | 0.0 | None |


---

## Level 3 — Multi-pair

**Question:** Does this work outside USD/MXN?

| strategy | total_return_pct | ann_return_pct | ann_vol_pct | sharpe | max_drawdown_pct | win_rate_pct | trades | pct_flat | total_cost_pct | ticker | bars | start | end | primary_beats_rw |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flat_range | 20.99 | 0.84 | 11.68 | 0.13 | -32.61 | 42.5 | 213 | 15.9 | 4.26 | USDMXN=X | 5773 | 2004-03-19 | 2026-05-22 | True |
| flat_range | 100.32 | 3.34 | 17.88 | 0.272 | -41.34 | 45.1 | 201 | 11.5 | 4.02 | USDBRL=X | 5335 | 2004-03-19 | 2026-05-25 | True |
| flat_range | 14.22 | 0.58 | 17.65 | 0.121 | -41.89 | 43.7 | 213 | 10.9 | 4.26 | USDCOP=X | 5757 | 2004-03-23 | 2026-05-22 | True |
| flat_range | 44.22 | 1.45 | 9.67 | 0.197 | -24.47 | 42.5 | 235 | 15.5 | 4.7 | USDJPY=X | 6406 | 2001-09-18 | 2026-05-25 | True |
| flat_range | 21.2 | 0.85 | 9.04 | 0.138 | -26.51 | 41.9 | 218 | 16.1 | 4.38 | EURUSD=X | 5752 | 2004-03-19 | 2026-05-22 | True |
| flat_range | 31.61 | 1.21 | 6.76 | 0.212 | -24.2 | 36.9 | 211 | 25.4 | 4.22 | USDINR=X | 5749 | 2004-03-19 | 2026-05-22 | True |
| flat_range | 16.3 | 0.66 | 7.35 | 0.127 | -35.86 | 37.6 | 203 | 22.1 | 4.06 | USDPHP=X | 5745 | 2004-03-22 | 2026-05-22 | True |
| flat_range | -40.17 | -2.22 | 16.92 | -0.048 | -52.07 | 43.6 | 245 | 10.7 | 4.9 | USDZAR=X | 5767 | 2004-03-19 | 2026-05-25 | False |
| flat_range | 1029.49 | 11.79 | 15.79 | 0.785 | -36.72 | 49.8 | 158 | 10.1 | 3.18 | USDTRY=X | 5481 | 2005-04-22 | 2026-05-22 | True |
| flat_range | -8.82 | -0.4 | 16.49 | 0.058 | -42.72 | 41.9 | 231 | 13.8 | 4.62 | USDCLP=X | 5746 | 2004-03-22 | 2026-05-22 | True |
| flat_range | 76.36 | 2.52 | 13.06 | 0.256 | -36.33 | 44.8 | 199 | 11.2 | 3.98 | USDPLN=X | 5751 | 2004-03-19 | 2026-05-22 | True |
| flat_range | -7.31 | -0.33 | 12.86 | 0.038 | -35.71 | 42.0 | 216 | 16.9 | 4.36 | USDKRW=X | 5750 | 2004-03-19 | 2026-05-22 | True |
| flat_range | 75.25 | 2.49 | 9.4 | 0.309 | -18.77 | 42.7 | 193 | 16.8 | 3.86 | USDTHB=X | 5751 | 2004-03-19 | 2026-05-22 | True |
| flat_range | 29.59 | 1.14 | 8.24 | 0.179 | -23.22 | 38.4 | 182 | 24.6 | 3.64 | USDMYR=X | 5772 | 2004-03-19 | 2026-05-22 | True |
| flat_range | 7.35 | 0.29 | 11.91 | 0.084 | -40.26 | 40.9 | 213 | 19.3 | 4.26 | USDIDR=X | 6206 | 2001-10-23 | 2026-05-22 | True |
| flat_range | -57.07 | -3.26 | 16.4 | -0.12 | -62.17 | 36.5 | 251 | 24.9 | 5.02 | USDPEN=X | 6427 | 2001-09-19 | 2026-05-22 | False |
| flat_range | 2.89 | 0.12 | 8.49 | 0.057 | -29.33 | 42.8 | 227 | 14.8 | 4.54 | GBPUSD=X | 5764 | 2004-03-19 | 2026-05-22 | True |
| flat_range | -24.92 | -1.4 | 11.86 | -0.059 | -39.12 | 43.0 | 201 | 13.0 | 4.02 | AUDUSD=X | 5129 | 2006-09-04 | 2026-05-25 | False |
| flat_range | -30.05 | -1.54 | 9.48 | -0.116 | -51.87 | 41.5 | 241 | 17.1 | 4.82 | USDCHF=X | 5819 | 2004-01-06 | 2026-05-25 | False |


### Per-pair OOS (`flat_range` vs random walk)
| split | primary_sharpe | primary_return_pct | rw_sharpe | beats_rw | ticker |
| --- | --- | --- | --- | --- | --- |
| split_1 | 0.075 | 0.42 | 0.0 | True | USDMXN=X |
| split_2 | 0.363 | 10.92 | 0.0 | True | USDMXN=X |
| split_3 | 0.317 | 3.82 | 0.0 | True | USDMXN=X |
| split_1 | -0.201 | -14.38 | 0.0 | False | USDBRL=X |
| split_2 | 0.048 | -0.78 | 0.0 | True | USDBRL=X |
| split_3 | -0.709 | -12.34 | 0.0 | False | USDBRL=X |
| split_1 | -0.318 | -16.49 | 0.0 | False | USDCOP=X |
| split_2 | 0.041 | -1.65 | 0.0 | True | USDCOP=X |
| split_3 | -0.367 | -8.53 | 0.0 | False | USDCOP=X |
| split_1 | -0.367 | -6.65 | 0.0 | False | USDJPY=X |
| split_2 | 0.776 | 25.54 | 0.0 | True | USDJPY=X |
| split_3 | -0.08 | -1.55 | 0.0 | False | USDJPY=X |
| split_1 | -0.004 | -0.49 | 0.0 | False | EURUSD=X |
| split_2 | 0.067 | 0.7 | 0.0 | True | EURUSD=X |
| split_3 | 0.487 | 4.71 | 0.0 | True | EURUSD=X |
| split_1 | -1.045 | -19.17 | 0.0 | False | USDINR=X |
| split_2 | 0.042 | 0.25 | 0.0 | True | USDINR=X |
| split_3 | 0.838 | 6.79 | 0.0 | True | USDINR=X |
| split_1 | -0.455 | -8.61 | 0.0 | False | USDPHP=X |
| split_2 | 0.49 | 9.92 | 0.0 | True | USDPHP=X |
| split_3 | 0.316 | 3.69 | 0.0 | True | USDPHP=X |
| split_1 | 0.156 | 3.84 | 0.0 | True | USDZAR=X |
| split_2 | -0.203 | -10.49 | 0.0 | False | USDZAR=X |
| split_3 | -0.088 | -8.23 | 0.0 | False | USDZAR=X |
| split_1 | 1.097 | 101.52 | 0.0 | True | USDTRY=X |
| split_2 | 3.212 | 154.86 | 0.0 | True | USDTRY=X |
| split_3 | 5.127 | 29.2 | 0.0 | True | USDTRY=X |
| split_1 | 0.214 | 6.38 | 0.0 | True | USDCLP=X |
| split_2 | 0.105 | 0.65 | 0.0 | True | USDCLP=X |
| split_3 | -0.373 | -8.28 | 0.0 | False | USDCLP=X |
| split_1 | -0.027 | -1.92 | 0.0 | False | USDPLN=X |
| split_2 | -0.233 | -9.36 | 0.0 | False | USDPLN=X |
| split_3 | 0.07 | 0.33 | 0.0 | True | USDPLN=X |
| split_1 | 0.544 | 11.06 | 0.0 | True | USDKRW=X |
| split_2 | 0.256 | 6.36 | 0.0 | True | USDKRW=X |
| split_3 | -0.152 | -2.71 | 0.0 | False | USDKRW=X |
| split_1 | 0.817 | 12.28 | 0.0 | True | USDTHB=X |
| split_2 | 0.362 | 8.14 | 0.0 | True | USDTHB=X |
| split_3 | -0.894 | -9.47 | 0.0 | False | USDTHB=X |
| split_1 | 0.197 | 2.03 | 0.0 | True | USDMYR=X |
| split_2 | 0.613 | 10.3 | 0.0 | True | USDMYR=X |
| split_3 | -0.036 | -0.45 | 0.0 | False | USDMYR=X |
| split_1 | 0.118 | 2.19 | 0.0 | True | USDIDR=X |
| split_2 | 0.222 | 4.87 | 0.0 | True | USDIDR=X |
| split_3 | 0.48 | 6.47 | 0.0 | True | USDIDR=X |
| split_1 | -0.216 | -13.73 | 0.0 | False | USDPEN=X |
| split_2 | -0.414 | -26.44 | 0.0 | False | USDPEN=X |
| split_3 | -0.032 | -4.15 | 0.0 | False | USDPEN=X |
| split_1 | 0.441 | 10.73 | 0.0 | True | GBPUSD=X |
| split_2 | 0.391 | 9.85 | 0.0 | True | GBPUSD=X |
| split_3 | 0.03 | -0.05 | 0.0 | True | GBPUSD=X |
| split_1 | -0.049 | -2.63 | 0.0 | False | AUDUSD=X |
| split_2 | -0.433 | -14.16 | 0.0 | False | AUDUSD=X |
| split_3 | -1.095 | -12.83 | 0.0 | False | AUDUSD=X |
| split_1 | -0.631 | -10.91 | 0.0 | False | USDCHF=X |
| split_2 | 0.352 | 7.59 | 0.0 | True | USDCHF=X |
| split_3 | 0.501 | 5.52 | 0.0 | True | USDCHF=X |


### OOS summary by pair
| ticker | splits_beating_rw | splits_total | all_splits_beat_rw |
| --- | --- | --- | --- |
| AUDUSD=X | 0 | 3 | False |
| EURUSD=X | 2 | 3 | False |
| GBPUSD=X | 3 | 3 | True |
| USDBRL=X | 1 | 3 | False |
| USDCHF=X | 2 | 3 | False |
| USDCLP=X | 2 | 3 | False |
| USDCOP=X | 1 | 3 | False |
| USDIDR=X | 3 | 3 | True |
| USDINR=X | 2 | 3 | False |
| USDJPY=X | 1 | 3 | False |
| USDKRW=X | 2 | 3 | False |
| USDMXN=X | 3 | 3 | True |
| USDMYR=X | 2 | 3 | False |
| USDPEN=X | 0 | 3 | False |
| USDPHP=X | 2 | 3 | False |
| USDPLN=X | 1 | 3 | False |
| USDTHB=X | 2 | 3 | False |
| USDTRY=X | 3 | 3 | True |
| USDZAR=X | 1 | 3 | False |


### OOS aggregate
| cells | beats_rw_cells | pct_beats_rw | pairs_tested |
| --- | --- | --- | --- |
| 57.0 | 33.0 | 57.9 | 19.0 |


---

## Level 4 — Forecast errors

**Question:** Better forecasts than random walk (zero)?

| split | test_period | strategy | mae_model | rmse_model | dir_acc_model_pct | mae_rw | rmse_rw | dir_acc_rw_pct | dm_stat | dm_pvalue | model_beats_rw_mae | clark_west_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| split_1 | 2019-01-01..2021-12-31 | flat_range | 0.005939102761101291 | 0.008647659921353528 | 39.59131545338442 | 0.005938415226997784 | 0.008647735214997272 | 0.0 | -0.0012933186736936038 | 0.9989680812857389 | False | CW not run — use when nested OLS forecas |
| split_2 | 2022-01-01..2024-12-31 | flat_range | 0.0052463370621143 | 0.007216597405093337 | 46.67519181585678 | 0.0052454287107691 | 0.007216001927182372 | 0.0 | 0.008531476531811844 | 0.9931929491709532 | False | CW not run — use when nested OLS forecas |
| split_3 | 2025-01-01..2026-12-31 | flat_range | 0.004477809349403005 | 0.006424743002585592 | 46.089385474860336 | 0.004475033861764117 | 0.00642495899872646 | 0.0 | -0.0027506823051637857 | 0.9978052758246763 | False | CW not run — use when nested OLS forecas |


---

## Level 5 — Economic value

**Question:** Money/risk after spreads, roll, carry?

| strategy | total_return_pct | ann_return_pct | ann_vol_pct | sharpe | max_drawdown_pct | win_rate_pct | cost_layer | ticker | total_cost_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flat_range | 20.99 | 0.84 | 11.68 | 0.13 | -32.61 | 42.5 | base_costs_only | USDMXN=X | 4.26 |
| flat_range | -6.77 | -0.31 | 11.68 | 0.032 | -41.0 | 42.0 | full_economic | USDMXN=X | 24.337 |


---

## Level 6 — Data-snooping control

### Pre-registered hypotheses
- H1: Average spot return differs across R1–R4 regimes (Level 1).
- H2: flat_range OOS Sharpe exceeds random_walk on fixed splits (Level 2).
- H3: Effect appears in >=50% of EM FX pairs tested (Level 3).
- H4: Model 1-step forecast RMSE < random walk on OOS splits (Level 4).
- H5: Net return remains positive after full economic frictions (Level 5).
- H6: Holdout period not used for any parameter tuning (Level 6).
- H7: Best-of-strategy Sharpe survives White Reality Check (p < 0.05).

### Holdout evaluation (do not tune on this window)
| strategy | total_return_pct | ann_return_pct | ann_vol_pct | sharpe | max_drawdown_pct | win_rate_pct | sample | period |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flat_range | 3.82 | 2.67 | 9.87 | 0.317 | -7.07 | 45.8 | holdout | 2025-01-01..2026-12-31 |
| legacy | 8.35 | 5.81 | 10.2 | 0.604 | -7.01 | 53.9 | holdout | 2025-01-01..2026-12-31 |
| random_walk | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | holdout | 2025-01-01..2026-12-31 |


### Bootstrap Sharpe check (flat_range, full sample)
- observed_sharpe: 0.13
- boot_pvalue_approx: 0.268

### White Reality Check (legacy / flat_range / r2_only)
| strategy | observed_sharpe | is_best | bars | best_strategy | observed_max_sharpe | white_rc_pvalue | n_boot | block_len | rejects_data_mining_5pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flat_range | 0.1296 | False | 5773.0 | nan | nan | nan | nan | nan | nan |
| legacy | 0.1121 | False | 5773.0 | nan | nan | nan | nan | nan | nan |
| r2_only | 0.1503 | True | 5773.0 | nan | nan | nan | nan | nan | nan |
| _SUMMARY | nan | nan | nan | r2_only | 0.1503 | 0.6355 | 2000.0 | 10.0 | False |

- best_strategy: r2_only
- white_rc_pvalue: 0.6355
- rejects_data_mining_5pct: False

### Holdout discipline
- Do not change `config.yaml` after reading holdout results
- Document all trials in a research log

---

## Next actions

1. Refresh all pairs: `python scripts/run_research_ladder.py --refresh` (Terminal.app)
2. USDCOP and other EM feeds are auto-sanitized (`src/data_cleaning.py`)
3. Do not change `config.yaml` thresholds after reading holdout results.

---

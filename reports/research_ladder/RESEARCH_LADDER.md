# BR3N Macro Lab — Research Ladder

**Generated:** 2026-05-30 11:28  
**Primary pair:** USDMXN=X  
**Period:** 2006-09-15 → 2026-05-22 (5125 bars)  
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
| R1_trend_high_vol | 36.18 | 1854 | 3.06 | 0.446 | -20.09 |
| R2_trend_low_vol | 51.14 | 2621 | -0.42 | -0.116 | -22.69 |
| R3_range_high_vol | 2.26 | 116 | 17.27 | 2.958 | -4.92 |
| R4_range_low_vol | 10.42 | 534 | -0.69 | -0.205 | -13.87 |


### Strategy (flat_range) by regime
| regime | avg_bps_day_flat_range | sharpe_flat_range | max_dd_pct_flat_range |
| --- | --- | --- | --- |
| R1_trend_high_vol | 0.03 | 0.005 | -37.23 |
| R2_trend_low_vol | 1.59 | 0.443 | -19.54 |
| R3_range_high_vol | -0.57 | -9.966 | -0.66 |
| R4_range_low_vol | -0.22 | -5.643 | -1.19 |


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
| flat_range | 28.9 | 1.26 | 12.17 | 0.163 | -32.61 | 43.5 | 187 | 14.5 | 3.74 | USDMXN=X | 5125 | 2006-09-15 | 2026-05-22 | True |
| flat_range | 62.95 | 2.44 | 17.23 | 0.226 | -41.34 | 45.0 | 191 | 11.5 | 3.82 | USDBRL=X | 5097 | 2006-09-18 | 2026-05-25 | True |
| flat_range | 22.63 | 1.01 | 17.99 | 0.146 | -41.89 | 44.2 | 189 | 10.2 | 3.78 | USDCOP=X | 5113 | 2006-09-15 | 2026-05-22 | True |
| flat_range | 59.0 | 2.32 | 10.02 | 0.279 | -21.68 | 42.3 | 181 | 15.5 | 3.62 | USDJPY=X | 5104 | 2006-09-18 | 2026-05-25 | True |
| flat_range | 21.83 | 0.98 | 9.13 | 0.153 | -24.12 | 42.0 | 188 | 16.2 | 3.78 | EURUSD=X | 5104 | 2006-09-15 | 2026-05-22 | True |
| flat_range | 17.62 | 0.8 | 7.01 | 0.149 | -24.2 | 36.9 | 197 | 25.1 | 3.94 | USDINR=X | 5102 | 2006-09-15 | 2026-05-22 | True |
| flat_range | 3.16 | 0.15 | 7.63 | 0.059 | -35.86 | 39.1 | 185 | 20.5 | 3.7 | USDPHP=X | 5100 | 2006-09-15 | 2026-05-22 | True |
| flat_range | -19.3 | -1.05 | 17.02 | 0.023 | -40.4 | 43.5 | 215 | 11.2 | 4.3 | USDZAR=X | 5118 | 2006-09-18 | 2026-05-25 | True |
| flat_range | 1107.91 | 13.05 | 16.0 | 0.847 | -36.72 | 50.6 | 142 | 9.7 | 2.86 | USDTRY=X | 5118 | 2006-09-15 | 2026-05-22 | True |


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


### OOS summary by pair
| ticker | splits_beating_rw | splits_total | all_splits_beat_rw |
| --- | --- | --- | --- |
| EURUSD=X | 2 | 3 | False |
| USDBRL=X | 1 | 3 | False |
| USDCOP=X | 1 | 3 | False |
| USDINR=X | 2 | 3 | False |
| USDJPY=X | 1 | 3 | False |
| USDMXN=X | 3 | 3 | True |
| USDPHP=X | 2 | 3 | False |
| USDTRY=X | 3 | 3 | True |
| USDZAR=X | 1 | 3 | False |


### OOS aggregate
| cells | beats_rw_cells | pct_beats_rw | pairs_tested |
| --- | --- | --- | --- |
| 27.0 | 16.0 | 59.3 | 9.0 |


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

| strategy | total_return_pct | ann_return_pct | ann_vol_pct | sharpe | max_drawdown_pct | win_rate_pct | cost_layer | total_cost_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flat_range | 28.9 | 1.26 | 12.17 | 0.163 | -32.61 | 43.5 | base_costs_only | 3.74 |
| flat_range | 2.43 | 0.12 | 12.18 | 0.071 | -41.0 | 43.0 | full_economic | 21.649 |


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
- observed_sharpe: 0.163
- boot_pvalue_approx: 0.22

### White Reality Check (legacy / flat_range / r2_only)
| strategy | observed_sharpe | is_best | bars | best_strategy | observed_max_sharpe | white_rc_pvalue | n_boot | block_len | rejects_data_mining_5pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flat_range | 0.1634 | False | 5125.0 | nan | nan | nan | nan | nan | nan |
| legacy | 0.1346 | False | 5125.0 | nan | nan | nan | nan | nan | nan |
| r2_only | 0.2306 | True | 5125.0 | nan | nan | nan | nan | nan | nan |
| _SUMMARY | nan | nan | nan | r2_only | 0.2306 | 0.628 | 2000.0 | 10.0 | False |

- best_strategy: r2_only
- white_rc_pvalue: 0.628
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

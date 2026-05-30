# BR3N Macro Labs — Research Ladder

**Generated:** 2026-05-30 15:59  
**Primary pair:** USDMXN=X  
**Period:** 2001-09-14 → 2026-05-15 (6183 bars)  
**Primary strategy:** flat_range

> Research and education only. Not investment advice. No guaranteed returns. No live trading.

---

## Main conclusion

> **Main conclusion:** The current regime model does **not** provide robust evidence of exchange-rate forecast superiority over random walk. However, regime labels appear descriptively meaningful and may be more useful for **hedge-governance discipline** than outright price prediction.

---

## What passed / what failed

### Passed

- long-sample USD/MXN research setup
- regime labels produce different return and risk profiles
- fixed OOS strategy tests generated testable evidence
- multi-pair framework works
- White Reality Check and forecast-error tests are now included

### Failed or not yet supported

- forecast errors do not beat random walk
- full economic costs weaken or eliminate strategy value
- White Reality Check does not reject data-mining risk
- cross-pair evidence is mixed

---

## Ladder status

| Level | Question | Evidence status |
|-------|----------|-----------------|
| 1 — Descriptive regime evidence | Do returns differ by regime? | Supported descriptively |
| 2 — Out-of-sample strategy benchmark | Does the strategy beat random walk OOS? | Supported for USD/MXN, modest evidence |
| 3 — Multi-pair robustness | Does this work outside USD/MXN? | Mixed evidence |
| 4 — Forecast errors vs random walk | Better forecast errors than RW? | Not supported |
| 5 — Economic value after full frictions | Money/risk after spreads, roll, carry? | Not robust yet |
| 6 — Data-snooping control | Data-snooping / holdout discipline? | Not supported yet |
| 7 — Hedge-governance usefulness | Can regime rules improve hedge governance when forecasts fail? | See Level 7 below |
| 8 — Institutional proof | External validity for hedge-governance claims? | Not met — 1 met, 6 partial, 2 failed |

---

## Claim discipline

BR3N Macro Labs does **not** claim that the current model predicts FX or disproves random walk. The current evidence suggests that regime labels may be useful for organizing risk, identifying noisy versus structured environments, and testing hedge-governance policies.

---

## Level 1 — Descriptive evidence

**Question:** Do returns differ by regime?

### Spot returns by regime
| regime | pct_time | days | avg_bps_day_spot | sharpe_spot | max_dd_pct_spot |
| --- | --- | --- | --- | --- | --- |
| R1_trend_high_vol | 36.99 | 2287 | 4.1 | 0.6780 | -18.87 |
| R2_trend_low_vol | 50.27 | 3108 | -0.7400 | -0.2270 | -37.25 |
| R3_range_high_vol | 2.35 | 145 | 9.43 | 1.83 | -8.24 |
| R4_range_low_vol | 10.4 | 643 | -1.2 | -0.4140 | -16.17 |


### Strategy (flat_range) by regime
| regime | avg_bps_day_flat_range | sharpe_flat_range | max_dd_pct_flat_range |
| --- | --- | --- | --- |
| R1_trend_high_vol | 0.0300 | 0.0050 | -44.91 |
| R2_trend_low_vol | 1.11 | 0.3440 | -30.75 |
| R3_range_high_vol | -0.5900 | -10.271 | -0.8400 |
| R4_range_low_vol | -0.2200 | -5.633 | -1.43 |


---

## Level 2 — Out-of-sample (fixed splits)

**Question:** Does the model beat random walk on unseen data?

Splits: train 2010–2018 → test 2019–2021; roll → test 2022–2024; test 2025–2026.

| split | sample | train_bars | test_bars | test_period | strategy | total_return_pct | sharpe | max_drawdown_pct | beats_random_walk_sharpe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| split_1 | test | 2253 | 748 | 2019-01-01..2021-12-31 | legacy | -7.15 | -0.1120 | -18.2 | — |
| split_1 | test | 2253 | 748 | 2019-01-01..2021-12-31 | flat_range | -2.58 | -0.0020 | -14.95 | False |
| split_1 | test | 2253 | 748 | 2019-01-01..2021-12-31 | r2_only | -3.82 | -0.1640 | -9.08 | — |
| split_1 | test | 2253 | 748 | 2019-01-01..2021-12-31 | random_walk | 0.0000 | 0.0000 | 0.0000 | — |
| split_2 | test | 3001 | 750 | 2022-01-01..2024-12-31 | legacy | 15.29 | 0.4700 | -16.36 | — |
| split_2 | test | 3001 | 750 | 2022-01-01..2024-12-31 | flat_range | 8.91 | 0.3160 | -18.32 | True |
| split_2 | test | 3001 | 750 | 2022-01-01..2024-12-31 | r2_only | 24.12 | 1.284 | -3.92 | — |
| split_2 | test | 3001 | 750 | 2022-01-01..2024-12-31 | random_walk | 0.0000 | 0.0000 | 0.0000 | — |
| split_3 | test | 3751 | 344 | 2025-01-01..2026-12-31 | legacy | 8.2 | 0.6570 | -7.79 | — |
| split_3 | test | 3751 | 344 | 2025-01-01..2026-12-31 | flat_range | 6.01 | 0.5220 | -6.52 | True |
| split_3 | test | 3751 | 344 | 2025-01-01..2026-12-31 | r2_only | 10.17 | 1.27 | -3.18 | — |
| split_3 | test | 3751 | 344 | 2025-01-01..2026-12-31 | random_walk | 0.0000 | 0.0000 | 0.0000 | — |


---

## Level 3 — Multi-pair

**Question:** Does this work outside USD/MXN?

| strategy | total_return_pct | ann_return_pct | ann_vol_pct | sharpe | max_drawdown_pct | win_rate_pct | trades | pct_flat | total_cost_pct | ticker | bars | start | end | primary_beats_rw |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flat_range | 20.36 | 0.7600 | 10.87 | 0.1240 | -44.27 | 43.7 | 231 | 14.7 | 4.62 | USDMXN=X | 6183 | 2001-09-14 | 2026-05-15 | True |
| flat_range | 103.28 | 3.41 | 17.69 | 0.2780 | -41.34 | 45.1 | 201 | 11.5 | 4.02 | USDBRL=X | 5335 | 2004-03-19 | 2026-05-25 | True |
| flat_range | 14.22 | 0.5800 | 17.65 | 0.1210 | -41.89 | 43.7 | 213 | 10.9 | 4.26 | USDCOP=X | 5757 | 2004-03-23 | 2026-05-22 | True |
| flat_range | 44.22 | 1.45 | 9.67 | 0.1970 | -24.47 | 42.5 | 235 | 15.5 | 4.7 | USDJPY=X | 6406 | 2001-09-18 | 2026-05-25 | True |
| flat_range | 21.2 | 0.8500 | 9.04 | 0.1380 | -26.51 | 41.9 | 218 | 16.1 | 4.38 | EURUSD=X | 5752 | 2004-03-19 | 2026-05-22 | True |
| flat_range | 31.61 | 1.21 | 6.76 | 0.2120 | -24.2 | 36.9 | 211 | 25.4 | 4.22 | USDINR=X | 5749 | 2004-03-19 | 2026-05-22 | True |
| flat_range | 16.3 | 0.6600 | 7.35 | 0.1270 | -35.86 | 37.6 | 203 | 22.1 | 4.06 | USDPHP=X | 5745 | 2004-03-22 | 2026-05-22 | True |
| flat_range | -40.17 | -2.22 | 16.92 | -0.0480 | -52.07 | 43.6 | 245 | 10.7 | 4.9 | USDZAR=X | 5767 | 2004-03-19 | 2026-05-25 | False |
| flat_range | 1,029.49 | 11.79 | 15.79 | 0.7850 | -36.72 | 49.8 | 158 | 10.1 | 3.18 | USDTRY=X | 5481 | 2005-04-22 | 2026-05-22 | True |
| flat_range | -8.82 | -0.4000 | 16.49 | 0.0580 | -42.72 | 41.9 | 231 | 13.8 | 4.62 | USDCLP=X | 5746 | 2004-03-22 | 2026-05-22 | True |
| flat_range | 76.36 | 2.52 | 13.06 | 0.2560 | -36.33 | 44.8 | 199 | 11.2 | 3.98 | USDPLN=X | 5751 | 2004-03-19 | 2026-05-22 | True |
| flat_range | -7.31 | -0.3300 | 12.86 | 0.0380 | -35.71 | 42 | 216 | 16.9 | 4.36 | USDKRW=X | 5750 | 2004-03-19 | 2026-05-22 | True |
| flat_range | 75.25 | 2.49 | 9.4 | 0.3090 | -18.77 | 42.7 | 193 | 16.8 | 3.86 | USDTHB=X | 5751 | 2004-03-19 | 2026-05-22 | True |
| flat_range | 29.59 | 1.14 | 8.24 | 0.1790 | -23.22 | 38.4 | 182 | 24.6 | 3.64 | USDMYR=X | 5772 | 2004-03-19 | 2026-05-22 | True |
| flat_range | 7.35 | 0.2900 | 11.91 | 0.0840 | -40.26 | 40.9 | 213 | 19.3 | 4.26 | USDIDR=X | 6206 | 2001-10-23 | 2026-05-22 | True |
| flat_range | -57.07 | -3.26 | 16.4 | -0.1200 | -62.17 | 36.5 | 251 | 24.9 | 5.02 | USDPEN=X | 6427 | 2001-09-19 | 2026-05-22 | False |
| flat_range | 2.89 | 0.1200 | 8.49 | 0.0570 | -29.33 | 42.8 | 227 | 14.8 | 4.54 | GBPUSD=X | 5764 | 2004-03-19 | 2026-05-22 | True |
| flat_range | -24.92 | -1.4 | 11.86 | -0.0590 | -39.12 | 43 | 201 | 13 | 4.02 | AUDUSD=X | 5129 | 2006-09-04 | 2026-05-25 | False |
| flat_range | -30.05 | -1.54 | 9.48 | -0.1160 | -51.87 | 41.5 | 241 | 17.1 | 4.82 | USDCHF=X | 5819 | 2004-01-06 | 2026-05-25 | False |


### Per-pair OOS (`flat_range` vs random walk)
| split | primary_sharpe | primary_return_pct | rw_sharpe | beats_rw | ticker |
| --- | --- | --- | --- | --- | --- |
| split_1 | -0.0020 | -2.58 | 0.0000 | False | USDMXN=X |
| split_2 | 0.3160 | 8.91 | 0.0000 | True | USDMXN=X |
| split_3 | 0.5220 | 6.01 | 0.0000 | True | USDMXN=X |
| split_1 | -0.2010 | -14.38 | 0.0000 | False | USDBRL=X |
| split_2 | 0.0480 | -0.7800 | 0.0000 | True | USDBRL=X |
| split_3 | -0.7090 | -12.34 | 0.0000 | False | USDBRL=X |
| split_1 | -0.3180 | -16.49 | 0.0000 | False | USDCOP=X |
| split_2 | 0.0410 | -1.65 | 0.0000 | True | USDCOP=X |
| split_3 | -0.3670 | -8.53 | 0.0000 | False | USDCOP=X |
| split_1 | -0.3670 | -6.65 | 0.0000 | False | USDJPY=X |
| split_2 | 0.7760 | 25.54 | 0.0000 | True | USDJPY=X |
| split_3 | -0.0800 | -1.55 | 0.0000 | False | USDJPY=X |
| split_1 | -0.0040 | -0.4900 | 0.0000 | False | EURUSD=X |
| split_2 | 0.0670 | 0.7000 | 0.0000 | True | EURUSD=X |
| split_3 | 0.4870 | 4.71 | 0.0000 | True | EURUSD=X |
| split_1 | -1.045 | -19.17 | 0.0000 | False | USDINR=X |
| split_2 | 0.0420 | 0.2500 | 0.0000 | True | USDINR=X |
| split_3 | 0.8380 | 6.79 | 0.0000 | True | USDINR=X |
| split_1 | -0.4550 | -8.61 | 0.0000 | False | USDPHP=X |
| split_2 | 0.4900 | 9.92 | 0.0000 | True | USDPHP=X |
| split_3 | 0.3160 | 3.69 | 0.0000 | True | USDPHP=X |
| split_1 | 0.1560 | 3.84 | 0.0000 | True | USDZAR=X |
| split_2 | -0.2030 | -10.49 | 0.0000 | False | USDZAR=X |
| split_3 | -0.0880 | -8.23 | 0.0000 | False | USDZAR=X |
| split_1 | 1.097 | 101.52 | 0.0000 | True | USDTRY=X |
| split_2 | 3.212 | 154.86 | 0.0000 | True | USDTRY=X |
| split_3 | 5.127 | 29.2 | 0.0000 | True | USDTRY=X |
| split_1 | 0.2140 | 6.38 | 0.0000 | True | USDCLP=X |
| split_2 | 0.1050 | 0.6500 | 0.0000 | True | USDCLP=X |
| split_3 | -0.3730 | -8.28 | 0.0000 | False | USDCLP=X |
| split_1 | -0.0270 | -1.92 | 0.0000 | False | USDPLN=X |
| split_2 | -0.2330 | -9.36 | 0.0000 | False | USDPLN=X |
| split_3 | 0.0700 | 0.3300 | 0.0000 | True | USDPLN=X |
| split_1 | 0.5440 | 11.06 | 0.0000 | True | USDKRW=X |
| split_2 | 0.2560 | 6.36 | 0.0000 | True | USDKRW=X |
| split_3 | -0.1520 | -2.71 | 0.0000 | False | USDKRW=X |
| split_1 | 0.8170 | 12.28 | 0.0000 | True | USDTHB=X |
| split_2 | 0.3620 | 8.14 | 0.0000 | True | USDTHB=X |
| split_3 | -0.8940 | -9.47 | 0.0000 | False | USDTHB=X |
| split_1 | 0.1970 | 2.03 | 0.0000 | True | USDMYR=X |
| split_2 | 0.6130 | 10.3 | 0.0000 | True | USDMYR=X |
| split_3 | -0.0360 | -0.4500 | 0.0000 | False | USDMYR=X |
| split_1 | 0.1180 | 2.19 | 0.0000 | True | USDIDR=X |
| split_2 | 0.2220 | 4.87 | 0.0000 | True | USDIDR=X |
| split_3 | 0.4800 | 6.47 | 0.0000 | True | USDIDR=X |
| split_1 | -0.2160 | -13.73 | 0.0000 | False | USDPEN=X |
| split_2 | -0.4140 | -26.44 | 0.0000 | False | USDPEN=X |
| split_3 | -0.0320 | -4.15 | 0.0000 | False | USDPEN=X |
| split_1 | 0.4410 | 10.73 | 0.0000 | True | GBPUSD=X |
| split_2 | 0.3910 | 9.85 | 0.0000 | True | GBPUSD=X |
| split_3 | 0.0300 | -0.0500 | 0.0000 | True | GBPUSD=X |
| split_1 | -0.0490 | -2.63 | 0.0000 | False | AUDUSD=X |
| split_2 | -0.4330 | -14.16 | 0.0000 | False | AUDUSD=X |
| split_3 | -1.095 | -12.83 | 0.0000 | False | AUDUSD=X |
| split_1 | -0.6310 | -10.91 | 0.0000 | False | USDCHF=X |
| split_2 | 0.3520 | 7.59 | 0.0000 | True | USDCHF=X |
| split_3 | 0.5010 | 5.52 | 0.0000 | True | USDCHF=X |


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
| USDMXN=X | 2 | 3 | False |
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
| 57 | 32 | 56.1 | 19 |


---

## Level 4 — Forecast errors

**Question:** Better forecasts than random walk (zero)?

| split | test_period | strategy | mae_model | rmse_model | dir_acc_model_pct | mae_rw | rmse_rw | dir_acc_rw_pct | dm_stat | dm_pvalue | model_beats_rw_mae | clark_west_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| split_1 | 2019-01-01..2021-12-31 | flat_range | 0.0059 | 0.0087 | 40.3485 | 0.0059 | 0.0087 | 0.0000 | -0.0368 | 0.9706 | True | CW not run — use when nested OLS forecast; ru… |
| split_2 | 2022-01-01..2024-12-31 | flat_range | 0.0055 | 0.0073 | 40.988 | 0.0055 | 0.0073 | 0.0000 | 0.0115 | 0.9908 | False | CW not run — use when nested OLS forecast; ru… |
| split_3 | 2025-01-01..2026-12-31 | flat_range | 0.0043 | 0.0060 | 45.6395 | 0.0043 | 0.0060 | 0.0000 | 0.0371 | 0.9704 | True | CW not run — use when nested OLS forecast; ru… |


---

## Level 5 — Economic value

**Question:** Money/risk after spreads, roll, carry?

| strategy | total_return_pct | ann_return_pct | ann_vol_pct | sharpe | max_drawdown_pct | win_rate_pct | cost_layer | ticker | total_cost_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flat_range | 20.36 | 0.7600 | 10.87 | 0.1240 | -44.27 | 43.7 | base_costs_only | USDMXN=X | 4.62 |
| flat_range | -6.47 | -0.2700 | 10.87 | 0.0290 | -51.35 | 43.6 | full_economic | USDMXN=X | 26.42 |


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
| flat_range | 6.01 | 4.36 | 8.95 | 0.5220 | -6.52 | 45.3 | holdout | 2025-01-01..2026-12-31 |
| legacy | 8.2 | 5.94 | 9.47 | 0.6570 | -7.79 | 51.7 | holdout | 2025-01-01..2026-12-31 |
| random_walk | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | holdout | 2025-01-01..2026-12-31 |


### Bootstrap Sharpe check (flat_range, full sample)
- observed_sharpe: 0.124
- boot_pvalue_approx: 0.242

### White Reality Check (legacy / flat_range / r2_only)
| strategy | observed_sharpe | is_best | bars | best_strategy | observed_max_sharpe | white_rc_pvalue | n_boot | block_len | rejects_data_mining_5pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flat_range | 0.1238 | False | 6,183.00 | — | — | — | — | — | — |
| legacy | 0.1616 | False | 6,183.00 | — | — | — | — | — | — |
| r2_only | 0.2676 | True | 6,183.00 | — | — | — | — | — | — |
| _SUMMARY | — | — | — | r2_only | 0.2676 | 0.6075 | 2,000.00 | 10 | False |

- best_strategy: r2_only
- white_rc_pvalue: 0.6075
- rejects_data_mining_5pct: False

### Holdout discipline
- Do not change `config.yaml` after reading holdout results
- Document all trials in a research log

---

## Level 7 — Hedge-governance usefulness

**Question:** Can regime rules improve hedge governance even when they fail as FX forecasts?

**Metrics:** hedge turnover, hedge cost, volatility reduction, max drawdown of hedged exposure, regret proxy, cost-adjusted risk reduction, and comparison of `no_change_in_range` vs static hedge ratios.

### Hedge governance scorecard (US entity long MXN)

| policy_name | hedge_turnover | total_hedge_cost | volatility_reduction | max_drawdown_hedged | regret_proxy | cost_adjusted_risk_reduction | average_hedge_ratio | number_of_hedge_changes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| never_hedged | 0.0000 | 0.0000 | 0.0000 | -71.451 | 7.88 | 0.0000 | 0.0000 | 0 |
| half_hedged | 0.5000 | 0.0100 | 5.695 | -45.019 | 3.94 | 5.685 | 0.5000 | 1 |
| mostly_hedged | 0.7500 | 0.0150 | 8.542 | -25.322 | 1.97 | 8.527 | 0.7500 | 1 |
| fully_hedged | 1 | 0.0200 | 11.385 | 0.0000 | 0.0000 | 11.365 | 1 | 1 |
| regime_based | 98.4 | 1.968 | 7.221 | -33.106 | 2.967 | 5.253 | 0.6010 | 501 |
| r2_active_policy | 118.9 | 2.378 | 5.273 | -53.14 | 3.788 | 2.895 | 0.5510 | 395 |
| no_change_in_range | 26.9 | 0.5380 | 7.163 | -37.488 | 2.781 | 6.625 | 0.6600 | 264 |
| volatility_triggered | 83.2 | 1.664 | 6.649 | -30.134 | 3.473 | 4.985 | 0.5180 | 277 |


**Interpretation:** Compare `no_change_in_range` and `regime_based` policies against static ratios (`half_hedged`, `fully_hedged`) on turnover and cost-adjusted risk reduction — not on forecast accuracy.


---

## Level 8 — Institutional proof requirements

**Question:** What must be demonstrated before hedge-governance claims are treated as institutionally valid?

Do **not** upgrade hedge-governance claims from prototype to institutional until **all nine** Level 8 requirements are **Met** (not Partial). Partial results may inform the research agenda only.

### Pass / fail matrix

| requirement | pass_threshold | evidence_status | current_state | design_notes |
| --- | --- | --- | --- | --- |
| Many currency pairs | >= 10 pairs with hedge scorecards published | Partial | 19 pairs with hedge OOS scorecards (target 10) | Trading ladder covers ~19 pairs; hedge govern… |
| Multiple decades | >= 20 years per pair without survivorship gaps | Partial | 25y configured; multi-pair decades not validated | USD/MXN ~20–25y; not validated across full pa… |
| Official data | Tier-1 spot (FRED H.10 or licensed feed) for … | Partial | Tier-1 preferred; not enforced across full he… | FRED H.10 for USD/MXN when available; Yahoo f… |
| Real or realistic forward costs | Forward points + roll in static vs dynamic he… | Not met | No forward curve or bid/ask history in hedge … | Turnover bps + spread/slippage/roll/carry ass… |
| Static vs dynamic hedge policies | Static benchmarks vs dynamic policies on same… | Partial | Static vs dynamic tested OOS on 19 pairs | Tested on USD/MXN: never/half/mostly/fully vs… |
| Transaction costs | All hedge and trading metrics net of explicit… | Partial | Costs included but simplified (bps on hedge t… | 2 bps turnover + Level 5 frictions for tradin… |
| Out-of-sample tests | Walk-forward OOS for hedge policies, not only… | Met | Hedge OOS on 19 pairs; H8a pass (100.0%) | Trading OOS (3 splits) exists; hedge headline… |
| Data-snooping controls | Pre-registered hypotheses; White RC / SPA on … | Not met | White RC p = 0.6075 — does not reject data-mi… | White RC p ≈ 0.61 on trading strategies — doe… |
| Multiple corporate exposure types | >= 3 exposure types with published scorecards | Partial | 3 exposure types in hedge OOS panel (19 pairs) | Code supports receiver / US-long-MXN / USD-li… |


### Pre-registered hypotheses (Level 8 upgrade path)
- H8a: `no_change_in_range` beats `regime_based` on cost-adjusted risk reduction OOS on >= 50% of pairs tested.
- H8b: Turnover reduction (no_change vs regime_based) >= 40% median across pairs without worse max drawdown hedged.
- H8c: Results replicate on Tier-1 spot only (no prototype fallback in published scorecards).
- H8d: Forward-point-adjusted hedge costs do not reverse the ranking of no_change vs static 50% / 75%.
- H8e: Best hedge policy survives White Reality Check on the pre-registered policy set (p < 0.05).
- H8f: At least three exposure types show consistent turnover discipline vs reactive regime hedging.

### First planned test

Multi-pair walk-forward OOS hedge policy comparison — see `reports/research_log/PRE_REGISTRATION_LOG.md` (Multi-Pair Hedge OOS).

Run: `python scripts/run_multipair_hedge_oos.py`

### Multi-pair hedge OOS summary (pre-registered)

- Pairs tested: **19** (target ≥ 10)
- Exposure types: **3**
- Comparison cells (no_change vs regime_based): **829**
- H8a — pairs where no_change wins majority of cells: **19** (100.0% of pairs) → **PASS**
- H8b — median turnover reduction: **74.07%** → **PASS**

**Note:** H8a/H8b use simplified hedge turnover costs (no forward curve). Passing these hypotheses does **not** clear the full Level 8 gate — all nine institutional requirements must be **Met**.

### Per-pair OOS (no_change vs regime_based)

| ticker | cells | win_rate | median_turnover_red_% |
| --- | --- | --- | --- |
| AUDUSD=X | 36 | 77.8 | 74.5 |
| EURUSD=X | 42 | 81.0 | 75.0 |
| GBPUSD=X | 42 | 85.7 | 73.9 |
| USDBRL=X | 42 | 57.1 | 75.0 |
| USDCHF=X | 42 | 85.7 | 71.1 |
| USDCLP=X | 42 | 61.9 | 77.2 |
| USDCOP=X | 42 | 71.4 | 72.7 |
| USDIDR=X | 46 | 56.5 | 72.0 |
| USDINR=X | 42 | 76.2 | 83.0 |
| USDJPY=X | 46 | 73.9 | 78.1 |
| USDKRW=X | 42 | 85.7 | 67.5 |
| USDMXN=X | 69 | 69.6 | 77.4 |
| USDMYR=X | 42 | 78.6 | 75.0 |
| USDPEN=X | 46 | 95.7 | 69.6 |
| USDPHP=X | 42 | 85.7 | 75.0 |
| USDPLN=X | 42 | 66.7 | 73.2 |
| USDTHB=X | 42 | 76.2 | 70.3 |
| USDTRY=X | 40 | 50.0 | 68.0 |
| USDZAR=X | 42 | 66.7 | 70.0 |


**Claim discipline:** Level 7 prototype results (USD/MXN, one exposure type, full sample) do **not** satisfy Level 8. They justify continued research, not desk adoption.


---

## Next actions

1. Refresh all pairs: `python scripts/run_research_ladder.py --refresh` (Terminal.app)
2. Pre-register and run multi-pair hedge OOS: see `reports/research_log/PRE_REGISTRATION_LOG.md`
3. USDCOP and other EM feeds are auto-sanitized (`src/data_cleaning.py`)
4. Do not change `config.yaml` thresholds after reading holdout results.

---

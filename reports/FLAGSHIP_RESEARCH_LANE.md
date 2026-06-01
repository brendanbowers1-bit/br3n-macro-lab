# Flagship Research Lane — Forecast Failure and Hedge Usefulness

*Generated: 2026-06-01 06:41*

## Thesis

Bowers Frontier Macro Labs does not need to prove that FX is predictable to create research value. The flagship lane tests whether regime intelligence improves hedge-governance decisions when price prediction fails.

## Forecast Scorecard (separate object)

- Models evaluated: **19**
- Beat random walk (RMSE): **1** (5.3%)

Interpretation: Most models still fail the forecast-accuracy benchmark. Hedge usefulness must be evaluated independently.

## Data Context

- Carry layer ready: **True** (policy-rate proxy; forward points required for true economics)
- Forward points CSV loaded: **True**

## OOS Hedge Governance — base costs

### split_1 (2019-01-01..2021-12-31)

- **fully_hedged** [static]: cost-adj 13.84, turnover 0.0, efficiency 13.84
- **no_change_in_range_carry_aware** [carry_aware]: cost-adj 10.892, turnover 6.831, efficiency 1.594
- **mostly_hedged** [static]: cost-adj 10.38, turnover 0.0, efficiency 10.38
- **carry_adjusted_regime** [carry_aware]: cost-adj 9.801, turnover 10.3, efficiency 0.952
- **no_change_in_range** [dynamic]: cost-adj 8.682, turnover 1.6, efficiency 5.426
- **regime_based** [dynamic]: cost-adj 8.451, turnover 11.8, efficiency 0.716
- **regime_only** [carry_aware]: cost-adj 8.451, turnover 11.8, efficiency 0.716
- **volatility_triggered** [dynamic]: cost-adj 8.006, turnover 4.8, efficiency 1.668
- **half_hedged** [static]: cost-adj 6.92, turnover 0.0, efficiency 6.92
- **static_50** [static]: cost-adj 6.92, turnover 0.0, efficiency 6.92
- **r2_active_policy** [dynamic]: cost-adj 6.102, turnover 12.0, efficiency 0.509

### split_2 (2022-01-01..2024-12-31)

- **fully_hedged** [static]: cost-adj 11.62, turnover 0.0, efficiency 11.62
- **no_change_in_range_carry_aware** [carry_aware]: cost-adj 9.19, turnover 7.875, efficiency 1.167
- **mostly_hedged** [static]: cost-adj 8.715, turnover 0.0, efficiency 8.715
- **carry_adjusted_regime** [carry_aware]: cost-adj 7.62, turnover 10.9, efficiency 0.699
- **no_change_in_range** [dynamic]: cost-adj 7.211, turnover 5.0, efficiency 1.442
- **regime_based** [dynamic]: cost-adj 7.084, turnover 13.4, efficiency 0.529
- **regime_only** [carry_aware]: cost-adj 7.084, turnover 13.4, efficiency 0.529
- **volatility_triggered** [dynamic]: cost-adj 6.547, turnover 15.6, efficiency 0.42
- **half_hedged** [static]: cost-adj 5.81, turnover 0.0, efficiency 5.81
- **static_50** [static]: cost-adj 5.81, turnover 0.0, efficiency 5.81
- **r2_active_policy** [dynamic]: cost-adj 5.024, turnover 17.4, efficiency 0.289

### split_3 (2025-01-01..2026-12-31)

- **fully_hedged** [static]: cost-adj 9.488, turnover 0.0, efficiency 9.488
- **no_change_in_range_carry_aware** [carry_aware]: cost-adj 7.366, turnover 2.625, efficiency 2.806
- **mostly_hedged** [static]: cost-adj 7.116, turnover 0.0, efficiency 7.116
- **carry_adjusted_regime** [carry_aware]: cost-adj 6.65, turnover 3.3, efficiency 2.015
- **no_change_in_range** [dynamic]: cost-adj 6.092, turnover 0.6, efficiency 10.153
- **regime_based** [dynamic]: cost-adj 5.774, turnover 4.2, efficiency 1.375
- **regime_only** [carry_aware]: cost-adj 5.774, turnover 4.2, efficiency 1.375
- **volatility_triggered** [dynamic]: cost-adj 5.037, turnover 1.8, efficiency 2.798
- **half_hedged** [static]: cost-adj 4.744, turnover 0.0, efficiency 4.744
- **static_50** [static]: cost-adj 4.744, turnover 0.0, efficiency 4.744
- **r2_active_policy** [dynamic]: cost-adj 4.654, turnover 4.2, efficiency 1.108

**Best dynamic/carry policy (base):** `no_change_in_range_carry_aware`

## OOS Hedge Governance — forward_full costs

### split_1 (2019-01-01..2021-12-31)

- **volatility_triggered** [dynamic]: cost-adj 1.884, turnover 4.8, efficiency 0.393
- **fully_hedged** [static]: cost-adj 1.67, turnover 0.0, efficiency 1.67
- **no_change_in_range_carry_aware** [carry_aware]: cost-adj 1.55, turnover 6.831, efficiency 0.227
- **carry_adjusted_regime** [carry_aware]: cost-adj 1.273, turnover 10.3, efficiency 0.124
- **mostly_hedged** [static]: cost-adj 1.252, turnover 0.0, efficiency 1.252
- **regime_based** [dynamic]: cost-adj 0.972, turnover 11.8, efficiency 0.082
- **regime_only** [carry_aware]: cost-adj 0.972, turnover 11.8, efficiency 0.082
- **half_hedged** [static]: cost-adj 0.835, turnover 0.0, efficiency 0.835
- **static_50** [static]: cost-adj 0.835, turnover 0.0, efficiency 0.835
- **no_change_in_range** [dynamic]: cost-adj 0.446, turnover 1.6, efficiency 0.279
- **r2_active_policy** [dynamic]: cost-adj -1.252, turnover 12.0, efficiency -0.104

### split_2 (2022-01-01..2024-12-31)

- **half_hedged** [static]: cost-adj -0.291, turnover 0.0, efficiency -0.291
- **static_50** [static]: cost-adj -0.291, turnover 0.0, efficiency -0.291
- **mostly_hedged** [static]: cost-adj -0.436, turnover 0.0, efficiency -0.436
- **fully_hedged** [static]: cost-adj -0.582, turnover 0.0, efficiency -0.582
- **volatility_triggered** [dynamic]: cost-adj -0.778, turnover 15.6, efficiency -0.05
- **no_change_in_range** [dynamic]: cost-adj -0.922, turnover 5.0, efficiency -0.184
- **regime_based** [dynamic]: cost-adj -0.998, turnover 13.4, efficiency -0.074
- **regime_only** [carry_aware]: cost-adj -0.998, turnover 13.4, efficiency -0.074
- **no_change_in_range_carry_aware** [carry_aware]: cost-adj -1.017, turnover 7.875, efficiency -0.129
- **carry_adjusted_regime** [carry_aware]: cost-adj -1.18, turnover 10.9, efficiency -0.108
- **r2_active_policy** [dynamic]: cost-adj -2.137, turnover 17.4, efficiency -0.123

### split_3 (2025-01-01..2026-12-31)

- **fully_hedged** [static]: cost-adj 3.891, turnover 0.0, efficiency 3.891
- **no_change_in_range_carry_aware** [carry_aware]: cost-adj 2.974, turnover 2.625, efficiency 1.133
- **mostly_hedged** [static]: cost-adj 2.918, turnover 0.0, efficiency 2.918
- **carry_adjusted_regime** [carry_aware]: cost-adj 2.703, turnover 3.3, efficiency 0.819
- **no_change_in_range** [dynamic]: cost-adj 2.327, turnover 0.6, efficiency 3.878
- **regime_based** [dynamic]: cost-adj 2.225, turnover 4.2, efficiency 0.53
- **regime_only** [carry_aware]: cost-adj 2.225, turnover 4.2, efficiency 0.53
- **volatility_triggered** [dynamic]: cost-adj 2.191, turnover 1.8, efficiency 1.217
- **half_hedged** [static]: cost-adj 1.946, turnover 0.0, efficiency 1.946
- **static_50** [static]: cost-adj 1.946, turnover 0.0, efficiency 1.946
- **r2_active_policy** [dynamic]: cost-adj 1.236, turnover 4.2, efficiency 0.294

**Best dynamic/carry policy (forward_full):** `no_change_in_range_carry_aware`

## Turnover-Adjusted Comparison (forward_full)

### split_1 (2019-01-01..2021-12-31)
- Best static: `fully_hedged` — cost-adj 1.67, turnover 0.0, efficiency 1.67
- Best dynamic (efficiency): `volatility_triggered` — cost-adj 1.884, turnover 4.8, efficiency 0.393
- Dynamic beats static on cost-adj: **True** | on turnover efficiency: **False**

### split_2 (2022-01-01..2024-12-31)
- Best static: `half_hedged` — cost-adj -0.291, turnover 0.0, efficiency -0.291
- Best dynamic (efficiency): `volatility_triggered` — cost-adj -0.778, turnover 15.6, efficiency -0.05
- Dynamic beats static on cost-adj: **False** | on turnover efficiency: **True**

### split_3 (2025-01-01..2026-12-31)
- Best static: `fully_hedged` — cost-adj 3.891, turnover 0.0, efficiency 3.891
- Best dynamic (efficiency): `no_change_in_range` — cost-adj 2.327, turnover 0.6, efficiency 3.878
- Dynamic beats static on cost-adj: **False** | on turnover efficiency: **False**

## R1 vs R2 Trend Quality (full sample)

### R1_trend_high_vol (full)
- Continuation probability: 0.5068
- Annualized vol: 15.221%
- Max drawdown: -18.873%
- Carry fragility rate: 0.3021
- Interpretation: High-volatility trend — often stress, liquidation, or unstable momentum; use caution rather than trend-following.

### R2_trend_low_vol (full)
- Continuation probability: 0.5248
- Annualized vol: 8.275%
- Max drawdown: -37.246%
- Carry fragility rate: 0.176
- Interpretation: Low-volatility trend — candidate information-diffusion regime; worth testing for structured hedge adjustment (OOS required).

## R1 vs R2 Trend Quality (OOS test windows only)

### split_1
  ### R1_trend_high_vol (oos_test)
  - Continuation probability: 0.5392
  - Annualized vol: 21.603%
  - Max drawdown: -14.322%
  - Carry fragility rate: 0.6471
  - Interpretation: High-volatility trend — often stress, liquidation, or unstable momentum; use caution rather than trend-following.

  ### R2_trend_low_vol (oos_test)
  - Continuation probability: 0.5182
  - Annualized vol: 9.275%
  - Max drawdown: -11.565%
  - Carry fragility rate: 0.1363
  - Interpretation: Low-volatility trend — candidate information-diffusion regime; worth testing for structured hedge adjustment (OOS required).

  - R2 minus R1 continuation: **-0.0210**

### split_2
  ### R1_trend_high_vol (oos_test)
  - Continuation probability: 0.5029
  - Annualized vol: 13.774%
  - Max drawdown: -11.61%
  - Carry fragility rate: 0.3161
  - Interpretation: High-volatility trend — often stress, liquidation, or unstable momentum; use caution rather than trend-following.

  ### R2_trend_low_vol (oos_test)
  - Continuation probability: 0.5802
  - Annualized vol: 9.072%
  - Max drawdown: -16.784%
  - Carry fragility rate: 0.287
  - Interpretation: Low-volatility trend — candidate information-diffusion regime; worth testing for structured hedge adjustment (OOS required).

  - R2 minus R1 continuation: **0.0773**

### split_3
  ### R1_trend_high_vol (oos_test)
  - Continuation probability: 0.5238
  - Annualized vol: 12.453%
  - Max drawdown: -7.624%
  - Carry fragility rate: 0.4667
  - Interpretation: High-volatility trend — often stress, liquidation, or unstable momentum; use caution rather than trend-following.

  ### R2_trend_low_vol (oos_test)
  - Continuation probability: 0.5072
  - Annualized vol: 7.798%
  - Max drawdown: -12.672%
  - Carry fragility rate: 0.2222
  - Interpretation: Low-volatility trend — candidate information-diffusion regime; worth testing for structured hedge adjustment (OOS required).

  - R2 minus R1 continuation: **-0.0166**

## Claim Discipline

Results depend on data quality and cost assumptions. Static full hedge may dominate raw vol reduction; the research question is whether dynamic policies improve turnover-adjusted discipline when forecasts fail. This report does not claim trading readiness, FX predictability, or guaranteed hedge savings.

# BR3N Macro Labs — Model Zoo Report

**Generated:** 2026-05-30 15:15

> Research and education only. Not investment advice. No guaranteed returns. No live trading.

The model zoo is designed to prevent overreliance on a single rule. The objective is **not** to find one perfect FX predictor, but to test whether different model families provide value under different regimes and decision contexts.

This tests **conditional forecastability** — not proof that FX is predictable.

---

## 1. Purpose

Compare simple, explainable models against random walk, buy-and-hold, and always-flat benchmarks under transaction costs, walk-forward splits, and separate forecast / trading / hedge-governance lenses.

---

## 2. Models tested

- **Attempted:** 15
- **Successful:** 15
- **Skipped:** 0

- random_walk_model
- buy_and_hold_model
- always_flat_model
- ma_crossover_model
- regime_trend_model
- r2_only_model
- r1_risk_off_model
- volatility_breakout_model
- mean_reversion_range_model
- carry_proxy_model
- dollar_stress_model
- flow_pressure_model
- ensemble_vote_model
- conservative_hedge_model
- no_change_in_range_model

### Run log

| model_name | status | reason | required_columns_missing |
| --- | --- | --- | --- |
| random_walk_model | success | nan | nan |
| buy_and_hold_model | success | nan | nan |
| always_flat_model | success | nan | nan |
| ma_crossover_model | success | nan | nan |
| regime_trend_model | success | nan | nan |
| r2_only_model | success | nan | nan |
| r1_risk_off_model | success | nan | nan |
| volatility_breakout_model | success | nan | nan |
| mean_reversion_range_model | success | nan | nan |
| carry_proxy_model | success | nan | nan |
| dollar_stress_model | success | nan | nan |
| flow_pressure_model | success | nan | nan |
| ensemble_vote_model | success | nan | nan |
| conservative_hedge_model | success | nan | nan |
| no_change_in_range_model | success | nan | nan |

---

## 3. Forecast accuracy results

| model_name | rmse_model | rmse_random_walk | mae_model | mae_random_walk | model_beats_rw_rmse | model_beats_rw_mae | directional_accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| random_walk_model | 0.007175 | 0.007175 | 0.004964 | 0.004964 | False | False | 0.0 |
| buy_and_hold_model | 0.007175 | 0.007175 | 0.004964 | 0.004964 | False | False | 0.0 |
| always_flat_model | 0.007175 | 0.007175 | 0.004964 | 0.004964 | False | False | 0.0 |
| ma_crossover_model | 0.007222 | 0.007175 | 0.005021 | 0.004964 | False | False | 49.64 |
| regime_trend_model | 0.007218 | 0.007175 | 0.005019 | 0.004964 | False | False | 43.07 |
| r2_only_model | 0.007188 | 0.007175 | 0.004992 | 0.004964 | False | False | 24.35 |
| r1_risk_off_model | 0.007188 | 0.007175 | 0.004992 | 0.004964 | False | False | 24.35 |
| volatility_breakout_model | 0.007231 | 0.007175 | 0.005042 | 0.004964 | False | False | 5.13 |
| mean_reversion_range_model | 0.007185 | 0.007175 | 0.004975 | 0.004964 | False | False | 4.06 |
| carry_proxy_model | 0.007183 | 0.007175 | 0.004971 | 0.004964 | False | False | 16.08 |
| dollar_stress_model | 0.00718 | 0.007175 | 0.004977 | 0.004964 | False | False | 31.62 |
| flow_pressure_model | 0.007175 | 0.007175 | 0.004965 | 0.004964 | True | False | 34.25 |
| ensemble_vote_model | 0.007217 | 0.007175 | 0.005 | 0.004964 | False | False | 24.3 |

---

## 4. Trading P&L results

| model_name | total_return_net | sharpe_net | max_drawdown_net | number_of_trades | total_transaction_cost | percent_time_in_market |
| --- | --- | --- | --- | --- | --- | --- |
| random_walk_model | 0.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| buy_and_hold_model | 82.87 | 0.273 | -35.04 | 1 | 0.02 | 100.0 |
| always_flat_model | 0.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| ma_crossover_model | 34.01 | 0.162 | -39.88 | 118 | 4.7 | 100.0 |
| regime_trend_model | 6.22 | 0.077 | -45.71 | 239 | 4.78 | 87.2 |
| r2_only_model | -16.14 | -0.08 | -46.81 | 395 | 7.9 | 50.3 |
| r1_risk_off_model | -16.14 | -0.08 | -46.81 | 395 | 7.9 | 50.3 |
| volatility_breakout_model | -21.24 | -0.252 | -33.13 | 1041 | 20.84 | 16.1 |
| mean_reversion_range_model | -30.02 | -0.534 | -32.33 | 335 | 6.76 | 8.3 |
| carry_proxy_model | -4.98 | -0.017 | -28.14 | 174 | 3.48 | 30.7 |
| dollar_stress_model | 90.35 | 0.312 | -28.06 | 603 | 12.06 | 60.4 |
| flow_pressure_model | -10.65 | -0.002 | -37.23 | 539 | 10.78 | 72.1 |
| ensemble_vote_model | 77.53 | 0.305 | -26.57 | 290 | 5.8 | 48.4 |

---

## 5. Hedge-governance results

| model_name | volatility_reduction | hedge_turnover | total_hedge_cost | cost_adjusted_risk_reduction | average_hedge_ratio | regret_proxy |
| --- | --- | --- | --- | --- | --- | --- |
| conservative_hedge_model | 6.81 | 106.1 | 2.122 | 4.688 | 0.614 | 3.05 |
| no_change_in_range_model | 7.163 | 26.9 | 0.538 | 6.625 | 0.66 | 2.781 |

---

## 6. Walk-forward results

| model_name | model_type | total_return_net | sharpe_net | max_drawdown_net | rmse_model | rmse_random_walk | mae_model | mae_random_walk | hedge_volatility_reduction | windows_tested |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_flat_model | trading | 0.0 | 0.0 | 0.0 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| buy_and_hold_model | trading | 2.9345 | 0.1619 | -11.092 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| carry_proxy_model | hybrid | -0.555 | -0.1966 | -5.7025 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| conservative_hedge_model | hedge_governance | nan | nan | nan | 0.0072 | 0.0072 | 0.0053 | 0.0053 | 6.8225 | 20 |
| dollar_stress_model | hybrid | 3.7685 | 0.2319 | -9.458 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| ensemble_vote_model | hybrid | 0.4375 | -0.0738 | -8.163 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| flow_pressure_model | hybrid | -2.173 | -0.2426 | -10.555 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| ma_crossover_model | hybrid | 1.3245 | 0.0091 | -11.7215 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| mean_reversion_range_model | hybrid | -1.3645 | -0.7942 | -3.1475 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| no_change_in_range_model | hedge_governance | nan | nan | nan | 0.0072 | 0.0072 | 0.0053 | 0.0053 | 7.2397 | 20 |
| r1_risk_off_model | hybrid | -1.253 | -0.218 | -6.899 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| r2_only_model | hybrid | -1.253 | -0.218 | -6.899 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| random_walk_model | forecast | 0.0 | 0.0 | 0.0 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| regime_trend_model | hybrid | 0.235 | -0.099 | -11.518 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| volatility_breakout_model | hybrid | -1.784 | -0.511 | -4.2055 | 0.0073 | 0.0072 | 0.0054 | 0.0053 | nan | 20 |

---

## 7. What worked

- At least one model beats random walk by RMSE on full sample
- Best net Sharpe: dollar_stress_model (0.312)
- Best hedge cost-adj risk reduction: no_change_in_range_model (6.625)
---

## 8. What failed

- No model beats random walk by MAE
---

## 9. Data limitations

- Results depend on data quality (Tier 1 spot preferred; yfinance fallback possible).
- Macro / flow columns may be missing on base feature files — some models skip gracefully.
- Full-sample metrics can overstate edge; prefer walk-forward and random-walk comparisons.
- Hedge metrics use simplified exposure math, not ASC 815 / IFRS 9 effectiveness testing.

---

## 10. Next model candidates

- Regime-switching forecast combinations with strict holdout discipline
- Vol-scaled position sizing (not binary ±1)
- Corridor-specific flow models with longer history
- Cost-aware ensemble with veto rules
- Hedge policies with explicit turnover caps

---

## Commands

```bash
python scripts/run_model_zoo.py
python scripts/generate_model_zoo_report.py
```

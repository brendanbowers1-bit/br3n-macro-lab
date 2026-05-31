# BR3N Macro Labs — Model Zoo Report

**Generated:** 2026-05-31 06:30

> Research and education only. Not investment advice. No guaranteed returns. No live trading.

The model zoo is designed to prevent overreliance on a single rule. The objective is **not** to find one perfect FX predictor, but to test whether different model families provide value under different regimes and decision contexts.

This tests **conditional forecastability** — not proof that FX is predictable.

---

## 1. Purpose

Compare simple, explainable models against random walk, buy-and-hold, and always-flat benchmarks under transaction costs, walk-forward splits, and separate forecast / trading / hedge-governance lenses.

---

## 2. Models tested

- **Attempted:** 24
- **Successful:** 24
- **Skipped:** 0

- random_walk_model
- buy_and_hold_model
- always_flat_model
- ma_crossover_model
- regime_trend_model
- r2_only_model
- r2_only_vol_scaled_model
- r1_risk_off_model
- volatility_breakout_model
- mean_reversion_range_model
- carry_proxy_model
- carry_regime_model
- carry_fragility_risk_off_model
- r2_carry_confirmed_model
- carry_adjusted_hedge_model
- dollar_stress_model
- flow_pressure_model
- ensemble_vote_model
- conservative_hedge_model
- no_change_in_range_model
- news_stress_risk_off_model
- r2_news_confirmed_model
- r1_news_escalation_model
- news_flow_pressure_model

### Run log

| model_name | status | reason | required_columns_missing |
| --- | --- | --- | --- |
| random_walk_model | success | nan | nan |
| buy_and_hold_model | success | nan | nan |
| always_flat_model | success | nan | nan |
| ma_crossover_model | success | nan | nan |
| regime_trend_model | success | nan | nan |
| r2_only_model | success | nan | nan |
| r2_only_vol_scaled_model | success | nan | nan |
| r1_risk_off_model | success | nan | nan |
| volatility_breakout_model | success | nan | nan |
| mean_reversion_range_model | success | nan | nan |
| carry_proxy_model | success | nan | nan |
| carry_regime_model | success | nan | nan |
| carry_fragility_risk_off_model | success | nan | nan |
| r2_carry_confirmed_model | success | nan | nan |
| carry_adjusted_hedge_model | success | nan | nan |
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
| r2_only_vol_scaled_model | 0.007186 | 0.007175 | 0.004989 | 0.004964 | False | False | 24.35 |
| r1_risk_off_model | 0.007188 | 0.007175 | 0.004992 | 0.004964 | False | False | 24.35 |
| volatility_breakout_model | 0.007231 | 0.007175 | 0.005042 | 0.004964 | False | False | 5.13 |
| mean_reversion_range_model | 0.007185 | 0.007175 | 0.004975 | 0.004964 | False | False | 4.06 |
| carry_proxy_model | 0.007183 | 0.007175 | 0.004971 | 0.004964 | False | False | 7.97 |
| carry_regime_model | 0.007178 | 0.007175 | 0.004967 | 0.004964 | False | False | 2.58 |
| r2_carry_confirmed_model | 0.00718 | 0.007175 | 0.004971 | 0.004964 | False | False | 7.97 |
| dollar_stress_model | 0.00718 | 0.007175 | 0.004977 | 0.004964 | False | False | 31.62 |
| flow_pressure_model | 0.007175 | 0.007175 | 0.004965 | 0.004964 | True | False | 34.25 |
| ensemble_vote_model | 0.007219 | 0.007175 | 0.005003 | 0.004964 | False | False | 25.36 |
| news_stress_risk_off_model | 0.007175 | 0.007175 | 0.004964 | 0.004964 | False | False | 0.0 |
| r2_news_confirmed_model | 0.007186 | 0.007175 | 0.004989 | 0.004964 | False | False | 19.84 |
| news_flow_pressure_model | 0.007175 | 0.007175 | 0.004964 | 0.004964 | False | False | 0.0 |

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
| r2_only_vol_scaled_model | -17.06 | -0.094 | -45.99 | 1036 | 7.8364 | 50.3 |
| r1_risk_off_model | -16.14 | -0.08 | -46.81 | 395 | 7.9 | 50.3 |
| volatility_breakout_model | -21.24 | -0.252 | -33.13 | 1041 | 20.84 | 16.1 |
| mean_reversion_range_model | -30.02 | -0.534 | -32.33 | 335 | 6.76 | 8.3 |
| carry_proxy_model | -1.02 | 0.007 | -13.46 | 106 | 2.12 | 16.5 |
| carry_regime_model | -10.39 | -0.242 | -15.41 | 184 | 3.68 | 5.5 |
| r2_carry_confirmed_model | 2.38 | 0.044 | -23.38 | 192 | 3.84 | 16.4 |
| dollar_stress_model | 90.35 | 0.312 | -28.06 | 603 | 12.06 | 60.4 |
| flow_pressure_model | -10.65 | -0.002 | -37.23 | 539 | 10.78 | 72.1 |
| ensemble_vote_model | 76.76 | 0.302 | -25.93 | 434 | 8.68 | 50.6 |
| news_stress_risk_off_model | 0.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| r2_news_confirmed_model | -20.48 | -0.133 | -43.35 | 909 | 18.18 | 40.9 |
| news_flow_pressure_model | 0.0 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |

---

## 5. Hedge-governance results

| model_name | volatility_reduction | hedge_turnover | total_hedge_cost | cost_adjusted_risk_reduction | average_hedge_ratio | regret_proxy |
| --- | --- | --- | --- | --- | --- | --- |
| carry_fragility_risk_off_model | 6.665 | 69.5 | 1.39 | 5.275 | 0.568 | 3.293 |
| carry_adjusted_hedge_model | 8.098 | 115.05 | 2.301 | 5.797 | 0.68 | 2.293 |
| conservative_hedge_model | 6.81 | 106.1 | 2.122 | 4.688 | 0.614 | 3.05 |
| no_change_in_range_model | 7.163 | 26.9 | 0.538 | 6.625 | 0.66 | 2.781 |
| r1_news_escalation_model | 6.541 | 193.0 | 3.86 | 2.681 | 0.534 | 3.49 |

---

## 6. Walk-forward results

| model_name | model_type | total_return_net | sharpe_net | max_drawdown_net | rmse_model | rmse_random_walk | mae_model | mae_random_walk | hedge_volatility_reduction | windows_tested |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_flat_model | trading | 0.0 | 0.0 | 0.0 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| buy_and_hold_model | trading | 2.9345 | 0.1619 | -11.092 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| carry_adjusted_hedge_model | hedge_governance | nan | nan | nan | 0.0072 | 0.0072 | 0.0053 | 0.0053 | 8.0756 | 20 |
| carry_fragility_risk_off_model | hedge_governance | nan | nan | nan | 0.0072 | 0.0072 | 0.0053 | 0.0053 | 6.6944 | 20 |
| carry_proxy_model | hybrid | 0.5255 | 0.2032 | -3.235 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| carry_regime_model | hybrid | 0.0525 | -0.0755 | -1.306 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| conservative_hedge_model | hedge_governance | nan | nan | nan | 0.0072 | 0.0072 | 0.0053 | 0.0053 | 6.8225 | 20 |
| dollar_stress_model | hybrid | 3.7685 | 0.2319 | -9.458 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| ensemble_vote_model | hybrid | 0.837 | 0.106 | -8.2345 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| flow_pressure_model | hybrid | -2.173 | -0.2426 | -10.555 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| ma_crossover_model | hybrid | 1.3245 | 0.0091 | -11.7215 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| mean_reversion_range_model | hybrid | -1.3645 | -0.7942 | -3.1475 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| news_flow_pressure_model | hybrid | 0.0 | 0.0 | 0.0 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| news_stress_risk_off_model | hybrid | 0.0 | 0.0 | 0.0 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| no_change_in_range_model | hedge_governance | nan | nan | nan | 0.0072 | 0.0072 | 0.0053 | 0.0053 | 7.2397 | 20 |
| r1_news_escalation_model | hedge_governance | nan | nan | nan | 0.0072 | 0.0072 | 0.0053 | 0.0053 | 6.4728 | 20 |
| r1_risk_off_model | hybrid | -1.253 | -0.218 | -6.899 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| r2_carry_confirmed_model | hybrid | -0.0805 | -0.0168 | -3.656 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| r2_news_confirmed_model | hybrid | -1.4985 | -0.2354 | -6.0595 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |
| r2_only_model | hybrid | -1.253 | -0.218 | -6.899 | 0.0072 | 0.0072 | 0.0053 | 0.0053 | nan | 20 |

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

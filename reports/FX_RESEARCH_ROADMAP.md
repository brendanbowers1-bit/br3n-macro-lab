# FX Research Roadmap

*Generated: 2026-06-01 06:41*

## Purpose

Organize the major unresolved academic and practical questions in FX, and connect each question to testable models, data needs, scorecards, and research outputs. Research-only — not investment advice.

## Highest-Level Thesis

FX markets may be mostly random-walk-like as price processes, but not all FX decisions are price forecasts. Regime, carry, news, flow, and stress variables may fail to predict exchange rates directly while still improving hedge governance, risk escalation, and decision discipline.

The question is not only whether FX can be predicted. The question is whether FX decisions can be improved when prediction fails.

Bowers Frontier Macro Labs does not need to prove that FX is predictable to create research value. The strongest current path is testing whether regime intelligence improves hedge-governance decisions when price prediction fails.

## Current Flagship Lane

**Forecast Failure and Hedge Usefulness**

- **Core question:** Can FX regime models fail to beat random walk as forecasts but still improve hedge governance?
- **Status:** Flagship active research lane.
- **Hypothesis:** Regime-based and no-change-in-range hedge policies reduce hedge turnover and cost-adjusted exposure volatility versus static hedge policies, even when price forecasts fail random-walk tests.

## Priority Research Questions

### 1. Forecast Failure and Hedge Usefulness

- **Question:** Can FX regime models fail to beat random walk as forecasts but still improve hedge governance?
- **Status:** Flagship active research lane.
- **Modules:** hedge_governance.py, carry_hedge_governance.py, random_walk_validity.py, model_zoo.py
- **Outputs:** data/outputs/hedge_governance_scorecard.csv, data/outputs/carry_hedge_governance_scorecard.csv, data/outputs/flagship_hedge_oos_scorecard.csv, data/outputs/random_walk_validity_map.csv, data/outputs/model_zoo_hedge_scorecard.csv, reports/FLAGSHIP_RESEARCH_LANE.md

### 2. Regime-Dependent UIP

- **Question:** Is uncovered interest parity wrong, incomplete, or regime-dependent?
- **Status:** Active — carry layer and UIP tests running on policy-rate proxy; forward points placeholder.
- **Modules:** carry_features.py, carry_models.py, carry_tests.py, forward_points.py
- **Outputs:** data/processed/usdmxn_features_regimes_carry.csv, data/outputs/carry_regime_test_results.csv, reports/CARRY_RESEARCH_FRAMEWORK.md

### 3. Carry Fragility

- **Question:** Are carry returns payment for bearing rare disaster risk, or evidence of market inefficiency?
- **Status:** Active — carry fragility index and regime tests implemented.
- **Modules:** carry_features.py, carry_models.py, carry_tests.py, carry_hedge_governance.py
- **Outputs:** data/processed/usdmxn_features_regimes_carry.csv, data/outputs/carry_regime_test_results.csv, data/outputs/carry_hedge_governance_scorecard.csv

### 4. Public Flow Proxies

- **Question:** Can public proxies approximate private flow pressure well enough to improve FX risk decisions?
- **Status:** Active — USD/MXN flow proxy tests running; exploratory, not causal.
- **Modules:** flow_proxies.py, flow_pressure_tests.py
- **Outputs:** data/processed/usdmxn_features_regimes_flow.csv, data/outputs/flow_pressure_test_results.csv

### 5. R1 vs R2 Trend Quality

- **Question:** Are high-volatility FX trends less forecastable because they reflect forced liquidation rather than information?
- **Status:** Active — regime intelligence and early R1/R2 comparisons in validity and news tests.
- **Modules:** regimes.py, random_walk_validity.py, news_features.py, carry_features.py
- **Outputs:** data/outputs/r1_r2_trend_quality_comparison.csv, data/outputs/random_walk_validity_map.csv, data/outputs/regime_attribution_flat_range.csv, data/outputs/news_feature_test_results.csv

## Data Needed by Question

- **Forecast Failure and Hedge Usefulness:** FX spot, regime labels, hedge policy rules, transaction cost assumptions, forward points later, exposure schedules later
- **Regime-Dependent UIP:** policy rate differentials, forward points, FX swaps, spot returns, VIX / dollar stress, news stress, regime labels
- **Carry Fragility:** policy rates, forward points, volatility, dollar stress, news stress, liquidity/spread proxies, regime labels
- **Public Flow Proxies:** FX spot, corridor calendar proxies, remittance seasonality, central-bank calendars, holidays
- **Remittance Flow Pressure:** FX spot per corridor, official remittance data, public calendar proxies, central bank remittance data
- **R1 vs R2 Trend Quality:** FX spot, regime labels, news stress, carry fragility, VIX/dollar stress, flow window proxies
- **Fundamentals Disconnect:** FX spot, interest rates, inflation, policy rates, trade/current account proxies, VIX / dollar stress, news uncertainty, regime labels
- **Random Walk Failure:** FX spot, regime labels, daily returns, walk-forward splits
- **Corporate Hedge Objective Function:** FX spot, regime labels, hedge cost assumptions, exposure schedules, forward points later
- **No-Arbitrage Breakdown:** forward points, cross-currency basis, FX swaps, bid/ask spreads, funding stress proxies, professional data source
- **Central-Bank Intervention:** central bank intervention data, reserves, policy dates, FX spot, volatility, regime labels
- **AI Decision Architecture:** model outputs, regime labels, hedge scorecards, publication memos

## Model Modules by Question

- **Forecast Failure and Hedge Usefulness:** hedge_governance.py, carry_hedge_governance.py, random_walk_validity.py, model_zoo.py
- **Regime-Dependent UIP:** carry_features.py, carry_models.py, carry_tests.py, forward_points.py
- **Carry Fragility:** carry_features.py, carry_models.py, carry_tests.py, carry_hedge_governance.py
- **Public Flow Proxies:** flow_proxies.py, flow_pressure_tests.py
- **Remittance Flow Pressure:** corridor_runner.py, corridor_reporting.py, flow_proxies.py, flow_pressure_tests.py
- **R1 vs R2 Trend Quality:** regimes.py, random_walk_validity.py, news_features.py, carry_features.py
- **Fundamentals Disconnect:** features.py, regimes.py, news_features.py, carry_features.py, research_runner.py
- **Random Walk Failure:** random_walk_validity.py, model_evaluation.py, model_walk_forward.py, ladder/level2_oos.py, ladder/level4_forecast.py
- **Corporate Hedge Objective Function:** hedge_governance.py, carry_hedge_governance.py, hedge_costs.py, fx_desk_framework.py
- **No-Arbitrage Breakdown:** forward_points.py, hedge_costs.py, carry_features.py
- **Central-Bank Intervention:** regimes.py, features.py
- **AI Decision Architecture:** luxury_dashboard.py, flagship_memo.py, lab_status.py, self_improve/runner.py

## Output Files by Question

- **Forecast Failure and Hedge Usefulness:** data/outputs/hedge_governance_scorecard.csv, data/outputs/carry_hedge_governance_scorecard.csv, data/outputs/flagship_hedge_oos_scorecard.csv, data/outputs/random_walk_validity_map.csv, data/outputs/model_zoo_hedge_scorecard.csv, reports/FLAGSHIP_RESEARCH_LANE.md
- **Regime-Dependent UIP:** data/processed/usdmxn_features_regimes_carry.csv, data/outputs/carry_regime_test_results.csv, reports/CARRY_RESEARCH_FRAMEWORK.md
- **Carry Fragility:** data/processed/usdmxn_features_regimes_carry.csv, data/outputs/carry_regime_test_results.csv, data/outputs/carry_hedge_governance_scorecard.csv
- **Public Flow Proxies:** data/processed/usdmxn_features_regimes_flow.csv, data/outputs/flow_pressure_test_results.csv
- **Remittance Flow Pressure:** data/outputs/corridor_master_scorecard.csv, data/outputs/corridor_flow_pressure_summary.csv, reports/corridor_roadmap_report.md
- **R1 vs R2 Trend Quality:** data/outputs/r1_r2_trend_quality_comparison.csv, data/outputs/random_walk_validity_map.csv, data/outputs/regime_attribution_flat_range.csv, data/outputs/news_feature_test_results.csv
- **Fundamentals Disconnect:** data/processed/usdmxn_features_regimes.csv, data/outputs/academic_test_results.csv, data/outputs/news_feature_test_results.csv
- **Random Walk Failure:** data/outputs/random_walk_validity_map.csv, data/outputs/model_zoo_forecast_scorecard.csv, data/outputs/walkforward_oos.csv, reports/research_ladder/level4_forecast_summary.csv
- **Corporate Hedge Objective Function:** data/outputs/hedge_governance_scorecard.csv, data/outputs/hedge_policy_scorecard.csv, data/outputs/fx_desk_scorecard.csv
- **No-Arbitrage Breakdown:** data/raw/forwards_usdmxn.csv.example, reports/CARRY_RESEARCH_FRAMEWORK.md
- **Central-Bank Intervention:** — (not yet defined)
- **AI Decision Architecture:** reports/LAB_STATUS.md, reports/publication/HEDGE_GOVERNANCE_MEMO.md, reports/publication/UNANSWERED_FX_QUESTIONS_SUMMARY.md

## Current Status

- **Forecast Failure and Hedge Usefulness** — Flagship active research lane.
- **Regime-Dependent UIP** — Active — carry layer and UIP tests running on policy-rate proxy; forward points placeholder.
- **Carry Fragility** — Active — carry fragility index and regime tests implemented.
- **Public Flow Proxies** — Active — USD/MXN flow proxy tests running; exploratory, not causal.
- **Remittance Flow Pressure** — Active — multi-corridor roadmap with flow and hedge scorecards.
- **R1 vs R2 Trend Quality** — Active — regime intelligence and early R1/R2 comparisons in validity and news tests.
- **Fundamentals Disconnect** — Partial — regime and stress layers exist; dedicated fundamental panel not yet built.
- **Random Walk Failure** — Active — random-walk validity map and model zoo forecast scorecards available.
- **Corporate Hedge Objective Function** — Active — hedge policy suite and FX desk scorecards implemented.
- **No-Arbitrage Breakdown** — Planned — forward points CSV ingest wired; basis and funding stress data not yet integrated.
- **Central-Bank Intervention** — Planned — intervention calendar and event study not yet built.
- **AI Decision Architecture** — Partial — dashboard, memos, and lab status exist; formal AI-layer evaluation not yet scored.

## Next 30-Day Plan

- Extend OOS hedge-governance tests on flagship lane (forecast failure vs hedge usefulness).
- Ingest forward-points CSV and rerun carry layer with trading-grade carry economics.
- Add R1 vs R2 trend-quality comparison table to regime intelligence outputs.
- Validate news-stress and carry-fragility interaction in stress sub-samples.
- Expand corridor flow-proxy tests with remittance seasonality where data quality allows.
- Document intervention calendar requirements for USD/MXN (planned lane).
- Regenerate LAB_STATUS and FX_RESEARCH_ROADMAP after each nightly pipeline run.

## Claim Discipline

The lab does not claim FX prediction certainty, random-walk disproof, guaranteed trading returns, or live-trading readiness. Results depend on data quality. Forecast accuracy, trading P&L, and hedge usefulness are evaluated separately.

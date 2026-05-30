# Research Snapshot Summary

**Snapshot date:** 2026-05-30  
**Git commit:** `310efc523a9d0275a3817b4b79bc825d4c22546c`  
**Project:** BR3N Macro Labs — FX Lab

> Research and risk-framing only. Not investment advice. No live trading.

## Scripts typically run before snapshot

- `python scripts/run_usdmxn_backtest.py`
- `python scripts/run_under_tested_research.py`
- `python scripts/run_research_ladder.py --refresh`
- `python scripts/run_model_zoo.py`
- `python scripts/generate_model_zoo_report.py`
- `python scripts/build_site.py`

## Key output files copied

- `research_snapshots/2026-05-30/data/outputs/US_CO_hedge_governance_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/corridor_hedge_governance_summary.csv`
- `research_snapshots/2026-05-30/data/outputs/academic_test_results.csv`
- `research_snapshots/2026-05-30/data/outputs/US_MX_hedge_governance_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/US_MX_hedge_governance_detail.csv`
- `research_snapshots/2026-05-30/data/outputs/model_zoo_forecast_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/US_CO_hedge_governance_detail.csv`
- `research_snapshots/2026-05-30/data/outputs/hedge_governance_detail.csv`
- `research_snapshots/2026-05-30/data/outputs/corridor_download_log.csv`
- `research_snapshots/2026-05-30/data/outputs/US_CO_random_walk_validity_map.csv`
- `research_snapshots/2026-05-30/data/outputs/hedge_policy_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/corridor_random_walk_validity.csv`
- `research_snapshots/2026-05-30/data/outputs/usdmxn_backtest_detail.csv`
- `research_snapshots/2026-05-30/data/outputs/US_CO_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/regime_attribution_flat_range.csv`
- `research_snapshots/2026-05-30/data/outputs/US_MX_random_walk_validity_map.csv`
- `research_snapshots/2026-05-30/data/outputs/US_BR_flow_pressure_test_results.csv`
- `research_snapshots/2026-05-30/data/outputs/US_IN_random_walk_validity_map.csv`
- `research_snapshots/2026-05-30/data/outputs/corridor_flow_pressure_summary.csv`
- `research_snapshots/2026-05-30/data/outputs/US_PH_hedge_governance_detail.csv`
- `research_snapshots/2026-05-30/data/outputs/.gitkeep`
- `research_snapshots/2026-05-30/data/outputs/ml_direction_model_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/data_quality_manifest.csv`
- `research_snapshots/2026-05-30/data/outputs/forecast_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/US_PH_hedge_governance_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/model_zoo_trading_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/hedge_governance_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/US_IN_flow_pressure_test_results.csv`
- `research_snapshots/2026-05-30/data/outputs/usdmxn_labeled.csv`
- `research_snapshots/2026-05-30/data/outputs/US_PH_random_walk_validity_map.csv`
- `research_snapshots/2026-05-30/data/outputs/strategy_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/US_BR_random_walk_validity_map.csv`
- `research_snapshots/2026-05-30/data/outputs/random_walk_validity_map.csv`
- `research_snapshots/2026-05-30/data/outputs/US_BR_hedge_governance_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/hedge_policy_detail.csv`
- `research_snapshots/2026-05-30/data/outputs/US_IN_scorecard.csv`
- `research_snapshots/2026-05-30/data/outputs/US_MX_flow_pressure_test_results.csv`
- `research_snapshots/2026-05-30/data/outputs/US_CO_flow_pressure_test_results.csv`
- `research_snapshots/2026-05-30/data/outputs/walkforward_in_sample.csv`
- `research_snapshots/2026-05-30/data/outputs/model_zoo_walk_forward_scorecard.csv`
- ...

**Total files copied:** 91

## Latest state

| Item | Value |
|------|-------|
| USD/MXN regime | R2_trend_low_vol |
| Best trading model (Sharpe net) | dollar_stress_model (sharpe_net=0.312) |
| Best hedge policy (cost-adj risk reduction) | no_change_in_range_model (cost_adjusted_risk_reduction=6.625) |
| Random-walk forecast status | 1 model(s) beat random walk by RMSE (mostly marginal) |
| Data quality | see data_quality_report.csv in snapshot |

## Flagship thesis

A model may fail as a price forecast but still be useful for hedge governance.

## Disclaimer

Research and education only. Not investment advice. No guaranteed returns. No live trading.

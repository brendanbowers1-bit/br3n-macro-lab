# USD/MXN Flagship Research Memo

**Bowers Frontier Macro Labs · FX Lab**  
**Generated:** 2026-05-30 14:42  
**Pair:** USD/MXN  
**Latest observation:** 2026-05-22 · Price 17.2977 · Regime **R1_trend_high_vol**

> Research and risk-framing only. Not investment advice. No live trading.  
> Independent research — not affiliated with any employer, bank, or payment company.

---

## Executive Summary

Bowers Frontier Macro Labs tests whether USD/MXN is **conditionally forecastable** across observable regimes — not uniformly predictable. The flagship memo integrates regime intelligence, random-walk benchmarks, hedge-governance scorecards, and explicit data-quality tiering.

**Desk framing (US_MX corridor):** Overall desk risk level is High. Hedge timing posture: High-volatility trend. Forecast evidence is weak, but regime information may still be useful for hedge governance and risk framing. High-volatility trend: treat as stress framing, not blind trend-following.

---

## 1. Market State

| Field | Value |
|-------|-------|
| Latest date | 2026-05-22 |
| Spot | 17.2977 |
| Regime | R1_trend_high_vol |
| Best in-sample strategy (Sharpe) | buy_and_hold |
| Diebold–Mariano p-value (vs RW) | — |

---

## 2. Random-Walk Validity by Regime

High-risk noise: R4_range_low_vol; Potential structure: R1_trend_high_vol, R2_trend_low_vol, R3_range_high_vol

| regime | random_walk_validity_label | average_daily_return | annualized_volatility |
| --- | --- | --- | --- |
| R1_trend_high_vol | Potential structure | 0.000328 | 16.489 |
| R2_trend_low_vol | Potential structure | -6e-05 | 8.921 |
| R3_range_high_vol | Potential structure | 0.000914 | 13.329 |
| R4_range_low_vol | High-risk noise | -5.7e-05 | 8.016 |


**Interpretation:** Regimes labeled *Potential structure* merit deeper study; *Random-walk-like* regimes support discipline and minimal hedge churn.

---

## 3. Strategy Scorecard (net of transaction costs)

| strategy | total_return_pct | ann_return_pct | ann_vol_pct | sharpe | max_drawdown_pct | win_rate_pct | trades | pct_flat | total_cost_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| buy_and_hold | 58.08 | 2.02 | 12.3 | 0.224 | -35.61 | 47.7 | 1 | 0.0 | 0.02 |
| legacy | 15.36 | 0.63 | 12.3 | 0.112 | -39.43 | 50.5 | 114 | 0.0 | 4.54 |
| flat_range | 20.99 | 0.84 | 11.68 | 0.13 | -32.61 | 42.5 | 213 | 15.9 | 4.26 |
| r2_only | 18.31 | 0.74 | 6.13 | 0.15 | -25.06 | 23.5 | 292 | 53.8 | 5.84 |
| random_walk | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 100.0 | 0.0 |


---

## 4. Hedge Governance (US entity long MXN)

**Best cost-adjusted risk reduction policy:** `fully_hedged`

| policy_name | hedge_turnover | cost_adjusted_risk_reduction | volatility_reduction |
| --- | --- | --- | --- |
| never_hedged | 0.0 | 0.0 | 0.0 |
| half_hedged | 0.5 | 6.14 | 6.15 |
| mostly_hedged | 0.75 | 9.21 | 9.225 |
| fully_hedged | 1.0 | 12.276 | 12.296 |
| regime_based | 87.3 | 6.019 | 7.765 |
| r2_active_policy | 103.0 | 3.613 | 5.673 |
| no_change_in_range | 23.2 | 7.272 | 7.736 |
| volatility_triggered | 72.1 | 5.744 | 7.186 |


**Key insight:** Hedge effectiveness and trading alpha are separate questions. A weak forecast can still support **hedge timing discipline**.

---

## 5. Data Quality Layer

| Field | Value |
|-------|-------|
| Primary source | yfinance |
| Tier | Prototype data |
| Quality flag | OK |

| role | label | source_name | tier_label | data_quality_flag | observation_count |
| --- | --- | --- | --- | --- | --- |
| primary_spot | USD/MXN spot (primary pipeline) | yfinance | Prototype data | OK | 5857 |
| official_spot | USD/MXN spot (FRED H.10 Tier 1) | fed_h10 | missing | MISSING | 0 |
| features_regimes | USD/MXN features + regimes | pipeline | unknown | OK | 5773 |
| macro_panel | Macro context panel (FRED + Yahoo) | fred_yahoo_mix | unknown | OK | 14177 |
| bis_eer | BIS Mexico nominal broad EER | bis_eer | missing | MISSING | 0 |
| corridor_spot | Corridor US_MX spot | yfinance | Prototype data | success | 0 |
| corridor_spot | Corridor US_IN spot | yfinance | Prototype data | success | 0 |
| corridor_spot | Corridor US_PH spot | yfinance | Prototype data | success | 0 |
| corridor_spot | Corridor US_CO spot | yfinance | Prototype data | success | 0 |
| corridor_spot | Corridor US_BR spot | yfinance | Prototype data | success | 0 |


**Standard:** Tier 1 (FRED H.10 / BIS) for publication-grade spot and macro context; Tier 4 (yfinance) for prototype only.

---

## 6. Recommended Actions (Research / Desk Framing)

1. Confirm exposure by entity, value date, and corridor before any hedge adjustment.
2. Treat **R1_trend_high_vol** as the active regime lens — not a trading signal.
3. Prefer **fully_hedged** governance framing when turnover discipline matters.
4. Re-run on Tier 1 official spot before external publication claims.
5. Require independent replication for any superconductivity-adjacent or non-FX claims (N/A here).

---

## 7. Limitations

- Rule-based regimes; no forward curve, no live execution prices.
- Prototype or official daily spot — not bid/ask or executable customer rates.
- In-sample and walk-forward results may degrade out-of-sample.
- Flow proxies are calendar-based, not transaction-level payment data.

---

## Disclaimer

This memo is for education, analysis, and risk-framing only. It is not investment advice, does not guarantee returns, and is not intended for automated live trading.

Bowers Frontier Macro Labs is an independent research project.

# Remittance Corridor Roadmap Report

*Bowers Frontier Macro Labs — research only, not investment advice.*

## 1. Purpose

The corridor roadmap expands Bowers Frontier Macro Labs from USD/MXN into major remittance and payment corridors. This is exploratory research that separates **forecast accuracy**, **trading P&L**, and **hedge-governance usefulness**. Public calendar proxies are **not** actual order-flow or payment-flow data.

## 2. Corridor roadmap

| corridor_id | sender_country | receiver_country | model_pair | official_pair_label | priority | corridor_theme | data_warning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| US_MX | United States | Mexico | USDMXN=X | USD/MXN | 1 | remittance_heavy | None |
| US_IN | United States | India | USDINR=X | USD/INR | 1 | remittance_heavy_policy_sensitive | INR may require NDF/official data validation for serious research. |
| US_PH | United States | Philippines | USDPHP=X | USD/PHP | 1 | remittance_heavy | Validate against BSP or official data for publication. |
| US_CO | United States | Colombia | USDCOP=X | USD/COP | 1 | latam_remittance_oil_risk | COP can be volatile and oil/risk sensitive. |
| US_BR | United States | Brazil | USDBRL=X | USD/BRL | 1 | latam_macro_risk | BRL can be volatile and sensitive to global risk/commodities. |
| US_GT | United States | Guatemala | USDGTQ=X | USD/GTQ | 2 | central_america_remittance_heavy | Yahoo data may be limited or unreliable. Official or bank data may be needed. |
| GULF_IN_PROXY | UAE/Saudi Arabia proxy | India | USDINR=X | USD/INR proxy for Gulf pegs | 2 | gulf_to_india_proxy | AED and SAR are USD-pegged, so USD/INR is a proxy, not a direct corridor pair. |

## 3. Data availability summary

| corridor_id | model_pair | official_pair_label | status | error_message | observations | start_date | end_date | data_source | data_tier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US_MX | USDMXN=X | USD/MXN | success | nan | 6183 | 2001-09-14 | 2026-05-15 | cache_resanitized | prototype |
| US_IN | USDINR=X | USD/INR | success | nan | 5749 | 2004-03-19 | 2026-05-22 | cache_resanitized | prototype |
| US_PH | USDPHP=X | USD/PHP | success | nan | 5745 | 2004-03-22 | 2026-05-22 | cache_resanitized | prototype |
| US_CO | USDCOP=X | USD/COP | success | nan | 5757 | 2004-03-23 | 2026-05-22 | cache_resanitized | prototype |
| US_BR | USDBRL=X | USD/BRL | success | nan | 5335 | 2004-03-19 | 2026-05-25 | cache_resanitized | prototype |

- **Succeeded:** US_MX, US_IN, US_PH, US_CO, US_BR
- **Failed:** none

## 4. Strategy comparison by corridor

| corridor_id | best_sharpe_mode | best_sharpe | best_drawdown_mode | max_drawdown |
| --- | --- | --- | --- | --- |
| US_BR | r2_only | 0.333 | r2_only | -21.62 |
| US_CO | flat_range | 0.121 | r2_only | -33.53 |
| US_IN | legacy | 0.261 | flat_range | -24.2 |
| US_MX | r2_only | 0.268 | r2_only | -33.12 |
| US_PH | flat_range | 0.127 | r2_only | -20.38 |

Full scorecard (selected columns):
| corridor_id | mode | sharpe | max_drawdown | total_return | number_of_trades |
| --- | --- | --- | --- | --- | --- |
| US_MX | buy_and_hold | 0.273 | -35.04 | 82.87 | 1 |
| US_MX | legacy | 0.162 | -39.88 | 34.01 | 118 |
| US_MX | flat_range | 0.124 | -44.27 | 20.36 | 231 |
| US_MX | r2_only | 0.268 | -33.12 | 39.69 | 327 |
| US_MX | random_walk | 0.0 | 0.0 | 0.0 | 0 |
| US_IN | buy_and_hold | 0.479 | -16.66 | 113.25 | 1 |
| US_IN | legacy | 0.261 | -25.09 | 46.87 | 120 |
| US_IN | flat_range | 0.212 | -24.2 | 31.61 | 211 |
| US_IN | r2_only | -0.253 | -26.47 | -19.55 | 302 |
| US_IN | random_walk | 0.0 | 0.0 | 0.0 | 0 |
| US_PH | buy_and_hold | 0.087 | -29.38 | 8.93 | 1 |
| US_PH | legacy | 0.05 | -39.64 | 1.78 | 101 |
| US_PH | flat_range | 0.127 | -35.86 | 16.3 | 203 |
| US_PH | r2_only | 0.102 | -20.38 | 7.1 | 293 |
| US_PH | random_walk | 0.0 | 0.0 | 0.0 | 0 |
| US_CO | buy_and_hold | 0.173 | -40.03 | 40.98 | 1 |
| US_CO | legacy | -0.039 | -62.67 | -42.92 | 112 |
| US_CO | flat_range | 0.121 | -41.89 | 14.22 | 213 |
| US_CO | r2_only | 0.072 | -33.53 | 4.93 | 333 |
| US_CO | random_walk | 0.0 | 0.0 | 0.0 | 0 |
| US_BR | buy_and_hold | 0.233 | -52.25 | 73.27 | 1 |
| US_BR | legacy | 0.234 | -52.43 | 73.93 | 102 |
| US_BR | flat_range | 0.278 | -41.34 | 103.28 | 201 |
| US_BR | r2_only | 0.333 | -21.62 | 78.02 | 300 |
| US_BR | random_walk | 0.0 | 0.0 | 0.0 | 0 |

## 5. Random-walk validity by corridor

| corridor_id | regime | random_walk_validity_label | annualized_volatility | autocorrelation_1d | interpretation |
| --- | --- | --- | --- | --- | --- |
| US_MX | R1_trend_high_vol | High-risk noise | 15.221 | 0.0025 | Elevated vol with weak direction — avoid over-adjusting hedge ratios. |
| US_MX | R2_trend_low_vol | Random-walk-like | 8.275 | -0.0087 | Directional metrics near random-walk benchmarks; static hedge may dominate. |
| US_MX | R3_range_high_vol | Potential structure | 12.98 | 0.056 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_MX | R4_range_low_vol | Potential structure | 7.3 | 0.0755 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_IN | R1_trend_high_vol | Potential structure | 10.122 | -0.1838 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_IN | R2_trend_low_vol | Potential structure | 5.588 | -0.0828 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_IN | R3_range_high_vol | Potential structure | 9.436 | -0.1587 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_IN | R4_range_low_vol | Random-walk-like | 4.873 | -0.0418 | Directional metrics near random-walk benchmarks; static hedge may dominate. |
| US_PH | R1_trend_high_vol | Potential structure | 10.704 | -0.237 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_PH | R2_trend_low_vol | Potential structure | 5.603 | -0.0793 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_PH | R3_range_high_vol | Potential structure | 9.359 | -0.3487 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_PH | R4_range_low_vol | Potential structure | 5.061 | -0.1271 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_CO | R1_trend_high_vol | Potential structure | 24.086 | -0.2087 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_CO | R2_trend_low_vol | Potential structure | 14.17 | -0.1295 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_CO | R3_range_high_vol | Potential structure | 25.97 | -0.2544 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_CO | R4_range_low_vol | Potential structure | 11.551 | -0.0874 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_BR | R1_trend_high_vol | Potential structure | 24.364 | -0.141 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_BR | R2_trend_low_vol | Potential structure | 13.415 | -0.067 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_BR | R3_range_high_vol | Potential structure | 20.32 | -0.1986 | Some trend or autocorrelation — conditional models may warrant testing OOS. |
| US_BR | R4_range_low_vol | Potential structure | 10.278 | -0.0275 | Some trend or autocorrelation — conditional models may warrant testing OOS. |

## 6. Flow-pressure window results

_Exploratory only — calendar proxies are not causal payment-flow data._

| corridor_id | observations_flow_window | observations_normal | volatility_flow_window | volatility_normal | p_value_return_difference | interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| US_MX | 4458 | 1725 | 10.9398 | 12.473 | 0.1397 | Flow windows show volatility differences but weak return evidence. |
| US_IN | 4251 | 1498 | 7.535 | 7.4924 | 0.0809 | No strong evidence from public flow proxies. |
| US_PH | 5146 | 599 | 8.1516 | 7.2989 | 0.8379 | No strong evidence from public flow proxies. |
| US_CO | 3963 | 1794 | 18.5999 | 18.4713 | 0.1327 | No strong evidence from public flow proxies. |
| US_BR | 3657 | 1678 | 17.3841 | 20.1473 | 0.3611 | Flow windows show volatility differences but weak return evidence. |

## 7. Hedge-governance results

_Simplified hedge-governance research — not ASC 815 / IFRS 9 hedge accounting._

Best policy by cost-adjusted risk reduction:

| corridor_id | policy_name | cost_adjusted_risk_reduction | hedge_turnover | total_hedge_cost | average_hedge_ratio |
| --- | --- | --- | --- | --- | --- |
| US_BR | fully_hedged | 18.274 | 1.0 | 0.02 | 1.0 |
| US_CO | fully_hedged | 18.538 | 1.0 | 0.02 | 1.0 |
| US_IN | fully_hedged | 7.501 | 1.0 | 0.02 | 1.0 |
| US_MX | fully_hedged | 11.365 | 1.0 | 0.02 | 1.0 |
| US_PH | fully_hedged | 8.042 | 1.0 | 0.02 | 1.0 |

## 8. Strongest corridors for further research

- **US_MX** (USD/MXN): remittance_heavy
- **US_IN** (USD/INR): remittance_heavy_policy_sensitive
- **US_PH** (USD/PHP): remittance_heavy
- **US_CO** (USD/COP): latam_remittance_oil_risk
- **US_BR** (USD/BRL): latam_macro_risk

## 9. Weakest / unreliable data corridors

- US_IN — INR may require NDF/official data validation for serious research.
- US_PH — Validate against BSP or official data for publication.
- US_CO — COP can be volatile and oil/risk sensitive.
- US_BR — BRL can be volatile and sensitive to global risk/commodities.

## 10. Next data upgrades

- Federal Reserve H.10 / FRED spot series where available (USD/MXN, USD/INR, etc.)
- BIS effective exchange rates for cross-checks
- World Bank remittance inflows by corridor
- Central bank remittance and spot data (Banxico, RBI, BSP, Banrep, BCB)
- Professional forward/FX data (Bloomberg, LSEG, FactSet) for bid/ask and forward points
- Legally usable proprietary payment-flow data only with proper authorization

---

**Disclaimer:** This is exploratory research. Public calendar proxies are not actual order-flow or payment-flow data. Results should be treated as hypotheses until validated with academic-grade data and, where legally available, proprietary payment-flow data.
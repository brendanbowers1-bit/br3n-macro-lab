# Bowers Frontier Macro Labs — USD/MXN Model Run

Date: 2024-07-01
Data mode: synthetic
Dataset: /Users/brendanbowers/fx_regime_lab/data-lake/processed/corridors/usd_mxn_canonical_sample.csv
Validation status: Warning

## Carry Signal
- Signal: positive
- Confidence: 0.65
- Rate differential 5.50% with recent spot trend -0.22% under normal vol regime. Research indicator only.

## Volatility Regime
- Regime: low
- 20-day annualized vol 0.0165 mapped to low using fixed research thresholds.

## Anomaly Detector
- Score: 100/100
- Robust z-score exceeded threshold on: spread_proxy_bps.

## Corridor Risk Score
- Score: 40.2/100
- Regime: Moderate

### Component breakdown
- volatility: 3.29
- spread_liquidity: 100
- rate_diff_change: 0
- event_risk: 15
- settlement_holiday: 10
- anomaly: 100

## Limitations
Uses synthetic/sample proxies where live connectors are unavailable. Spread and liquidity are research proxies, not executable market depth.

## Not Financial Advice
This is research and decision support, not a trading recommendation.

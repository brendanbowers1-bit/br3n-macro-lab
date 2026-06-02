# Bowers Frontier Macro Labs — USD/MXN Corridor Intelligence Brief

Corridor: USD/MXN (United States → Mexico)
Date: 2024-07-01
Data Mode: **synthetic**
Model Provider: deterministic_fallback
Model Name: transparent_models_v1
Validation Status: Warning

## Executive Summary
- Corridor risk score 40.2/100 (Moderate) on 2024-07-01 — synthetic data.
- Volatility regime: low; carry signal: positive.
- Validation status: Warning.
- Anomaly score 100/100 — Robust z-score exceeded threshold on: spread_proxy_bps.
- Dataset uses clearly labeled synthetic/sample data — not live market feeds.

## Market Snapshot
- Spot: 17.2618
- Volatility regime: normal
- Rate differential: 5.50%
- Carry proxy aligns with rate differential (research only)

## Corridor Risk Score
Score: **40.2/100**
Regime: **Moderate**

Component breakdown:
- volatility: 3.29
- spread_liquidity: 100
- rate_diff_change: 0
- event_risk: 15
- settlement_holiday: 10
- anomaly: 100

## What Changed
Latest row reflects no macro event flag and no holiday flag.

## Treasury / Settlement Watchpoints
Monitor cut-off calendars, holiday liquidity, and remittance cost proxies. This brief does not provide operational payment instructions.

## Stablecoin / Alternative Settlement Notes
On-chain rails may alter settlement windows but introduce separate issuer and off-ramp risks. Non-hype research context only.

## Model Confidence
Low–Medium (synthetic sample data)

## Data Limitations
Uses synthetic/sample proxies where live connectors are unavailable. Spread and liquidity are research proxies, not executable market depth.
This run uses synthetic/sample data explicitly labeled in the canonical dataset.

## RAG Context Used
- corridor_risk_notes.md (score 6)
- fx_basics.md (score 5)
- settlement_risk_notes.md (score 4)

## Not Financial Advice
Research and decision support only. Not investment advice. Not a trading signal.

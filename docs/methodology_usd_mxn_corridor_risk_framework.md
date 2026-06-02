# USD/MXN Corridor Risk Framework — Methodology

**Lab:** Bowers Frontier Macro Labs  
**Product:** USD/MXN Corridor Intelligence System  
**Status:** Research framework — not financial advice

## 1. Purpose

Study USD/MXN corridor risk across FX, rates, volatility, settlement, liquidity, remittance, and macro-event dimensions using explainable indicators.

## 2. What the score is

A transparent **0–100 corridor risk score** from weighted components: volatility, spread/liquidity, rate differential change, macro events, settlement/holiday friction, and anomaly detection.

## 3. What the score is not

- Not a trading signal
- Not a forecast or guarantee
- Not financial advice
- Not a substitute for market judgment

## 4. Data inputs

USD/MXN spot, US and Mexico policy rates, rate differential, volatility, spread and liquidity proxies, event and holiday flags, remittance cost proxy — documented in `data-lake/metadata/`.

## 5. Data quality standards

Source registry, immutable raw data, validation reports, explicit `data_mode`, stale-data warnings, source lineage on all dashboard numbers.

## 6. Feature construction

Daily returns, 20-day rolling volatility, volatility regime buckets, carry proxy from rate differential, event/holiday flags from curated calendars.

## 7. Risk score construction

See `src/models/corridor_risk_score.js` (Node sample pipeline) and `src/corridor_intelligence/risk_score.py` (Python remittance CRS).

## 8. Model layer

Transparent models first; LLMs generate narrative from structured outputs; RAG supplies research context only.

## 9. Evaluation

25-question eval battery with scoring on factuality, domain specificity, data grounding, uncertainty, actionability, hallucination control, financial safety.

## 10. Limitations

Synthetic sample data until live connectors validated; proxies ≠ executable spreads; remittance data may be starter/quarterly.

## 11. Next upgrades

Live FX, FRED/Banxico connectors (partially implemented in Python lake), real holiday feeds, RPW expansion, additional corridors only after USD/MXN milestone.

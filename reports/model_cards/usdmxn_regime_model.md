# Model Card: usdmxn_regime_v1

| Field | Value |
|-------|-------|
| **Name** | usdmxn_regime_v1 |
| **Type** | Rule-based regime classifier |
| **Pair** | USDMXN=X |

## Purpose
Classify when USD/MXN is in trend vs range and high vs low vol to study forecastability and dynamic hedge ratios.

## Inputs
Daily `price`, MA20, MA60, 20d realized vol percentile (config in `config.yaml`).

## Outputs
- Regime: R1_trend_high_vol, R2_trend_low_vol, R3_range_high_vol, R4_range_low_vol
- Strategy signals: legacy, flat_range, r2_only, buy_and_hold, random_walk (flat)

## Intended use
Local research, treasury risk framing, education.

## Not for
Live trading, order placement, broker APIs, regulatory filings.

## Benchmarks
- buy_and_hold (long USD/MXN)
- random_walk (flat — no edge)

## Validation plan
Walk-forward 5y train / 1y test; add forward carry and spreads in v2.

## Known weaknesses
In-sample thresholds; short history limits OOS folds; costs are simplified bps on turnover.

---
*Not investment advice.*

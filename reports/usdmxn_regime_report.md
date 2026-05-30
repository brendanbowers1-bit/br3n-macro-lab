# USD/MXN Regime Research Report

**Generated:** 2026-05-30 11:05  
**Ticker:** USDMXN=X  
**Period:** 2023-04-25 → 2026-05-22  
**Bars:** 799

> Research only. Not investment advice. No live trading.

## Latest snapshot

| Field | Value |
|-------|-------|
| Date | 2026-05-22 |
| Price | 17.2977 |
| Regime | R1_trend_high_vol |
| MA20 | 17.3324 |
| MA60 | 17.5341 |

## Strategy scorecard (net of 2.0 bps turnover cost)

| strategy | total_return_pct | ann_return_pct | ann_vol_pct | sharpe | max_drawdown_pct | win_rate_pct | trades | pct_flat | total_cost_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| buy_and_hold | -3.73 | -1.19 | 11.29 | -0.05 | -19.23 | 45.7 | 1 | 0.1 | 0.02 |
| legacy | 32.25 | 9.22 | 11.27 | 0.838 | -9.77 | 52.9 | 9 | 0.1 | 0.34 |
| flat_range | 21.93 | 6.45 | 10.68 | 0.639 | -11.21 | 46.1 | 21 | 12.1 | 0.42 |
| r2_only | 32.0 | 9.15 | 5.77 | 1.547 | -4.03 | 28.3 | 26 | 50.8 | 0.52 |
| random_walk | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 100.0 | 0.0 |

**Best Sharpe:** `r2_only` (1.547)  
**flat_range beats legacy (after costs):** No

## Walk-forward (train 5y / test 1y)

### In-sample (train windows)
_Insufficient history for walk-forward._

### Out-of-sample (test windows)
_Insufficient history for walk-forward._


## Regime mix

- R2_trend_low_vol: 51.2%
- R1_trend_high_vol: 38.0%
- R4_range_low_vol: 9.1%
- R3_range_high_vol: 1.6%

## Hedging guidance (US entity long MXN)

**Regime:** R1_trend_high_vol
**Exposure:** us_entity_long_mxn
**Hedge ratio:** 60% – 80%
**Instruments:** Forwards + options
**Notes:** Tranches, options, collars.


## Limitations

- Rule-based regimes; no forward curve or live execution.
- Transaction costs are turnover-based bps only.
- Walk-forward requires long history; short samples bias results.

---
_BR3N Macro Lab_

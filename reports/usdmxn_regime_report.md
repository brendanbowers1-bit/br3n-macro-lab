# USD/MXN Regime Research Report

**Generated:** 2026-05-30 13:44  
**Ticker:** USDMXN=X  
**Period:** 2004-03-19 → 2026-05-22  
**Bars:** 5773

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
| buy_and_hold | 58.08 | 2.02 | 12.3 | 0.224 | -35.61 | 47.7 | 1 | 0.0 | 0.02 |
| legacy | 15.36 | 0.63 | 12.3 | 0.112 | -39.43 | 50.5 | 114 | 0.0 | 4.54 |
| flat_range | 20.99 | 0.84 | 11.68 | 0.13 | -32.61 | 42.5 | 213 | 15.9 | 4.26 |
| r2_only | 18.31 | 0.74 | 6.13 | 0.15 | -25.06 | 23.5 | 292 | 53.8 | 5.84 |
| random_walk | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 100.0 | 0.0 |

**Best Sharpe:** `buy_and_hold` (0.224)  
**flat_range beats legacy (after costs):** Yes

## Walk-forward (train 5y / test 1y)

### In-sample (train windows)
| strategy | total_return_pct | ann_return_pct | ann_vol_pct | sharpe | max_drawdown_pct | win_rate_pct | fold | sample | period |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| legacy | 15.06 | 2.76 | 12.4 | 0.281 | -20.26 | 48.4 | 0 | in_sample | 2004-03-19_2009-03-18 |
| flat_range | 20.11 | 3.62 | 11.98 | 0.356 | -16.83 | 37.0 | 0 | in_sample | 2004-03-19_2009-03-18 |
| legacy | 9.76 | 1.82 | 13.61 | 0.2 | -21.7 | 49.0 | 1 | in_sample | 2005-03-19_2010-03-18 |
| flat_range | 17.22 | 3.13 | 13.16 | 0.3 | -18.69 | 40.6 | 1 | in_sample | 2005-03-19_2010-03-18 |
| legacy | -5.53 | -1.1 | 14.15 | -0.008 | -31.44 | 48.4 | 2 | in_sample | 2006-03-19_2011-03-18 |
| flat_range | 6.33 | 1.2 | 13.69 | 0.155 | -27.36 | 41.1 | 2 | in_sample | 2006-03-19_2011-03-18 |
| legacy | 8.7 | 1.63 | 15.17 | 0.182 | -34.09 | 50.5 | 3 | in_sample | 2007-03-19_2012-03-18 |
| flat_range | 20.61 | 3.7 | 14.56 | 0.322 | -29.33 | 44.7 | 3 | in_sample | 2007-03-19_2012-03-18 |
| legacy | 10.81 | 2.01 | 15.51 | 0.205 | -34.09 | 50.6 | 4 | in_sample | 2008-03-19_2013-03-18 |
| flat_range | 17.35 | 3.15 | 14.91 | 0.282 | -29.33 | 46.0 | 4 | in_sample | 2008-03-19_2013-03-18 |
| legacy | -29.34 | -6.49 | 12.3 | -0.484 | -32.56 | 49.2 | 5 | in_sample | 2009-03-19_2014-03-18 |
| flat_range | -23.03 | -4.93 | 11.39 | -0.387 | -25.87 | 42.6 | 5 | in_sample | 2009-03-19_2014-03-18 |
| legacy | -3.35 | -0.66 | 11.18 | -0.003 | -21.68 | 50.2 | 6 | in_sample | 2010-03-19_2015-03-18 |
| flat_range | -1.93 | -0.38 | 10.37 | 0.016 | -19.77 | 43.7 | 6 | in_sample | 2010-03-19_2015-03-18 |
| legacy | 22.13 | 3.94 | 11.31 | 0.398 | -19.07 | 51.6 | 7 | in_sample | 2011-03-19_2016-03-18 |
| flat_range | 21.93 | 3.9 | 10.55 | 0.416 | -18.44 | 45.0 | 7 | in_sample | 2011-03-19_2016-03-18 |
| legacy | -5.8 | -1.15 | 11.83 | -0.038 | -26.44 | 50.8 | 8 | in_sample | 2012-03-19_2017-03-18 |
| flat_range | -3.16 | -0.62 | 11.31 | 0.002 | -22.68 | 43.8 | 8 | in_sample | 2012-03-19_2017-03-18 |
| legacy | -2.01 | -0.39 | 11.9 | 0.027 | -26.44 | 51.1 | 9 | in_sample | 2013-03-19_2018-03-18 |
| flat_range | 7.66 | 1.44 | 11.36 | 0.183 | -22.68 | 44.9 | 9 | in_sample | 2013-03-19_2018-03-18 |
| legacy | 6.15 | 1.16 | 12.09 | 0.156 | -26.81 | 51.8 | 10 | in_sample | 2014-03-19_2019-03-18 |
| flat_range | 8.64 | 1.61 | 11.57 | 0.197 | -22.68 | 46.2 | 10 | in_sample | 2014-03-19_2019-03-18 |
| legacy | -4.59 | -0.9 | 12.76 | -0.007 | -33.0 | 51.1 | 11 | in_sample | 2015-03-19_2020-03-18 |
| flat_range | -3.71 | -0.73 | 12.04 | -0.0 | -29.0 | 43.7 | 11 | in_sample | 2015-03-19_2020-03-18 |
| legacy | -11.26 | -2.28 | 14.29 | -0.09 | -29.89 | 50.0 | 12 | in_sample | 2016-03-19_2021-03-18 |
| flat_range | -8.83 | -1.77 | 13.67 | -0.062 | -26.11 | 43.7 | 12 | in_sample | 2016-03-19_2021-03-18 |
| legacy | -9.3 | -1.87 | 12.84 | -0.083 | -22.3 | 49.4 | 13 | in_sample | 2017-03-19_2022-03-18 |
| flat_range | -6.06 | -1.2 | 12.08 | -0.04 | -24.28 | 41.2 | 13 | in_sample | 2017-03-19_2022-03-18 |
| legacy | -10.05 | -2.03 | 12.97 | -0.093 | -25.36 | 50.5 | 14 | in_sample | 2018-03-19_2023-03-18 |
| flat_range | -13.92 | -2.85 | 12.26 | -0.175 | -22.37 | 41.1 | 14 | in_sample | 2018-03-19_2023-03-18 |
| legacy | -0.28 | -0.05 | 12.56 | 0.058 | -25.36 | 51.3 | 15 | in_sample | 2019-03-19_2024-03-18 |
| flat_range | 0.56 | 0.11 | 11.93 | 0.069 | -22.37 | 41.9 | 15 | in_sample | 2019-03-19_2024-03-18 |
| legacy | 8.37 | 1.57 | 12.92 | 0.185 | -25.36 | 51.7 | 16 | in_sample | 2020-03-19_2025-03-18 |
| flat_range | 5.99 | 1.13 | 12.35 | 0.153 | -22.37 | 44.4 | 16 | in_sample | 2020-03-19_2025-03-18 |
| legacy | 20.16 | 3.63 | 10.86 | 0.382 | -22.4 | 52.7 | 17 | in_sample | 2021-03-19_2026-03-18 |
| flat_range | 12.32 | 2.28 | 10.2 | 0.272 | -19.36 | 44.0 | 17 | in_sample | 2021-03-19_2026-03-18 |

### Out-of-sample (test windows)
| strategy | total_return_pct | ann_return_pct | ann_vol_pct | sharpe | max_drawdown_pct | win_rate_pct | fold | sample | period |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| legacy | -13.71 | -13.27 | 14.1 | -0.939 | -17.45 | 47.9 | 0 | out_of_sample | 2009-03-19_2010-03-18 |
| flat_range | -9.19 | -8.88 | 13.15 | -0.642 | -12.6 | 41.0 | 0 | out_of_sample | 2009-03-19_2010-03-18 |
| legacy | -11.44 | -11.06 | 10.82 | -1.03 | -16.06 | 49.8 | 1 | out_of_sample | 2010-03-19_2011-03-18 |
| flat_range | -11.5 | -11.13 | 10.17 | -1.109 | -15.49 | 42.9 | 1 | out_of_sample | 2010-03-19_2011-03-18 |
| legacy | 7.51 | 7.27 | 14.96 | 0.543 | -10.02 | 52.3 | 2 | out_of_sample | 2011-03-19_2012-03-18 |
| flat_range | 9.48 | 9.17 | 13.51 | 0.717 | -8.27 | 50.0 | 2 | out_of_sample | 2011-03-19_2012-03-18 |
| legacy | -2.09 | -2.02 | 9.9 | -0.157 | -10.3 | 49.4 | 3 | out_of_sample | 2012-03-19_2013-03-18 |
| flat_range | -5.27 | -5.09 | 9.53 | -0.501 | -10.71 | 42.5 | 3 | out_of_sample | 2012-03-19_2013-03-18 |
| legacy | -12.3 | -11.9 | 10.93 | -1.104 | -16.66 | 46.0 | 4 | out_of_sample | 2013-03-19_2014-03-18 |
| flat_range | -7.81 | -7.55 | 9.96 | -0.738 | -13.29 | 35.6 | 4 | out_of_sample | 2013-03-19_2014-03-18 |
| legacy | 16.35 | 15.75 | 8.06 | 1.856 | -3.21 | 52.5 | 5 | out_of_sample | 2014-03-19_2015-03-18 |
| flat_range | 15.3 | 14.73 | 7.83 | 1.795 | -3.21 | 46.7 | 5 | out_of_sample | 2014-03-19_2015-03-18 |
| legacy | 11.43 | 10.97 | 11.49 | 0.964 | -8.08 | 56.5 | 6 | out_of_sample | 2015-03-19_2016-03-18 |
| flat_range | 9.55 | 9.17 | 11.05 | 0.849 | -7.56 | 49.2 | 6 | out_of_sample | 2015-03-19_2016-03-18 |
| legacy | -16.79 | -16.32 | 16.8 | -0.975 | -23.03 | 48.8 | 7 | out_of_sample | 2016-03-19_2017-03-18 |
| flat_range | -12.76 | -12.39 | 16.3 | -0.729 | -19.53 | 44.6 | 7 | out_of_sample | 2016-03-19_2017-03-18 |
| legacy | 1.22 | 1.18 | 10.32 | 0.165 | -8.36 | 50.4 | 8 | out_of_sample | 2017-03-19_2018-03-18 |
| flat_range | 4.68 | 4.53 | 9.8 | 0.501 | -8.13 | 47.3 | 8 | out_of_sample | 2017-03-19_2018-03-18 |
| legacy | -3.88 | -3.75 | 12.01 | -0.258 | -12.37 | 49.8 | 9 | out_of_sample | 2018-03-19_2019-03-18 |
| flat_range | -6.88 | -6.65 | 11.1 | -0.564 | -11.73 | 42.1 | 9 | out_of_sample | 2018-03-19_2019-03-18 |
| legacy | 6.46 | 6.23 | 12.22 | 0.555 | -13.25 | 49.4 | 10 | out_of_sample | 2019-03-19_2020-03-18 |
| flat_range | 3.21 | 3.09 | 10.89 | 0.333 | -12.25 | 34.9 | 10 | out_of_sample | 2019-03-19_2020-03-18 |
| legacy | 0.46 | 0.44 | 18.18 | 0.115 | -16.03 | 50.6 | 11 | out_of_sample | 2020-03-19_2021-03-18 |
| flat_range | 0.54 | 0.52 | 18.0 | 0.119 | -15.98 | 48.7 | 11 | out_of_sample | 2020-03-19_2021-03-18 |
| legacy | -15.15 | -14.67 | 9.24 | -1.669 | -16.91 | 46.0 | 12 | out_of_sample | 2021-03-19_2022-03-18 |
| flat_range | -10.32 | -9.98 | 7.73 | -1.321 | -12.01 | 32.2 | 12 | out_of_sample | 2021-03-19_2022-03-18 |
| legacy | 0.91 | 0.88 | 11.07 | 0.135 | -6.19 | 55.4 | 13 | out_of_sample | 2022-03-19_2023-03-18 |
| flat_range | -3.56 | -3.45 | 10.85 | -0.27 | -7.77 | 46.5 | 13 | out_of_sample | 2022-03-19_2023-03-18 |
| legacy | 6.12 | 5.9 | 9.6 | 0.645 | -8.92 | 54.0 | 14 | out_of_sample | 2023-03-19_2024-03-18 |
| flat_range | 9.2 | 8.87 | 9.13 | 0.976 | -8.22 | 46.0 | 14 | out_of_sample | 2023-03-19_2024-03-18 |
| legacy | 19.96 | 19.29 | 14.23 | 1.311 | -6.49 | 51.5 | 15 | out_of_sample | 2024-03-19_2025-03-18 |
| flat_range | 12.79 | 12.37 | 13.32 | 0.942 | -7.54 | 47.7 | 15 | out_of_sample | 2024-03-19_2025-03-18 |
| legacy | 11.76 | 11.52 | 9.2 | 1.231 | -5.06 | 55.6 | 16 | out_of_sample | 2025-03-19_2026-03-18 |
| flat_range | 6.9 | 6.76 | 9.02 | 0.77 | -5.06 | 47.1 | 16 | out_of_sample | 2025-03-19_2026-03-18 |
| legacy | -1.15 | -6.01 | 9.24 | -0.626 | -5.08 | 48.9 | 17 | out_of_sample | 2026-03-19_2026-05-22 |
| flat_range | -2.53 | -12.85 | 8.75 | -1.529 | -4.96 | 44.7 | 17 | out_of_sample | 2026-03-19_2026-05-22 |

### Walk-forward vs full-sample

- **legacy:** mean train Sharpe 0.070, mean OOS Sharpe 0.042 — OOS weaker than in-sample
- **flat_range:** mean train Sharpe 0.114, mean OOS Sharpe -0.022 — OOS weaker than in-sample

## Regime mix

- R2_trend_low_vol: 49.1%
- R1_trend_high_vol: 36.8%
- R4_range_low_vol: 11.4%
- R3_range_high_vol: 2.7%

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
_BR3N Macro Labs_

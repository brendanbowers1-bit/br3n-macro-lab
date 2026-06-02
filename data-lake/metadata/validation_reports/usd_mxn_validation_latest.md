# USD/MXN Dataset Validation Report

Status: **Warning**

Dataset: `/Users/brendanbowers/fx_regime_lab/data-lake/processed/corridors/usd_mxn_canonical_sample.csv`
Rows: 130
Date range: 2024-01-02 → 2024-07-01
Data mode: synthetic
Generated at: 2026-06-02T04:09:59.080Z

## Checks
- **file_exists**: pass
- **required_columns**: pass
- **valid_dates**: pass
- **duplicate_dates**: pass
- **monotonic_date_ordering**: pass
- **missing_values**: pass — [object Object]
- **suspicious_extreme_one_day_change**: pass
- **volatility_regime**: pass
- **data_mode**: pass — synthetic
- **synthetic_disclosure**: warn — Dataset is synthetic/sample — not live market data
- **source_lineage**: pass
- **stale_source_warning**: warn — Latest date 2024-07-01 is 700 days old
- **event_descriptions**: pass
- **holiday_descriptions**: pass

## Warnings
- synthetic_disclosure: Dataset is synthetic/sample — not live market data
- stale_source_warning: Latest date 2024-07-01 is 700 days old

> Research dataset. Synthetic/sample data is clearly labeled. Not financial advice.

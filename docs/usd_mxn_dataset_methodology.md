# USD/MXN Sample Dataset Methodology

## Purpose

Provide a **clearly labeled synthetic** canonical USD/MXN dataset for Model Lab pipeline development, validation, transparent models, brief generation, and dashboard integration.

## Fields

See `data-lake/metadata/data_dictionary.json` and canonical sample columns in `scripts/build_usd_mxn_sample_dataset.js`.

## Synthetic / sample status

All sample raw files and the canonical output use `data_mode: synthetic`. This is **not live market data**.

## Transformation logic

1. Generate business-day spine from raw FX sample.
2. Forward-fill Fed, Banxico, and quarterly remittance cost series.
3. Compute 1d/5d returns and 20d volatility.
4. Assign volatility regime buckets (low/normal/elevated/crisis).
5. Join event and holiday flags with descriptions.
6. Write `source_lineage` on every row.

## Known limitations

- Random walk FX is illustrative only.
- Policy rates are stepped synthetic series.
- Remittance cost is quarterly proxy.
- Does not replace Python `lake:run` mixed/live parquet.

## Live path

Run `npm run lake:run` for FRED/Banxico/RPW-backed canonical parquet; keep sample CSV for Model Lab JS pipeline isolation.

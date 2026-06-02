# FRED DFEDTARU ingest

**Source ID:** `rates_fed_policy`  
**Series:** DFEDTARU (Federal Funds Target Range — Upper Limit)

Ingest via:

```bash
python scripts/ingest_fred_policy_rate.py
```

Uses public FRED graph CSV (no API key). Each run writes a dated immutable file under `raw/rates/fed_policy_rate_dfedtaru_YYYYMMDD.csv` and updates the pipeline pointer `fed_policy_rate_dfedtaru.csv`.

Sidecar metadata: `fed_policy_rate_dfedtaru.meta.json`

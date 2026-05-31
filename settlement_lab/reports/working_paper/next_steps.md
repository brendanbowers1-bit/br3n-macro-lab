# Next Steps

## Completed (publication-grade Tier 1)

1. **Official BIS CPMI** — live pull from `stats.bis.org` SDMX API (`WS_CPMI_CASHLESS`, `WS_CPMI_SYSTEMS`)
2. **Live FRED SOFR/FEDFUNDS** — daily series via FRED CSV (`SOFR`, `FEDFUNDS`, `DGS10`)
3. **World Bank Global Findex 2024** — source=28 API (`account.t.d`, `g20.any`, `con1`, `fin22g`, etc.)
4. **Merchant fee panel** — Kansas City Fed US interchange schedules + Fed Reg II 2024 debit aggregate

Run:

```bash
cd settlement_lab && python scripts/fetch_settlement_data.py && python scripts/reproduce_settlement_lab.py
```

## Remaining enhancements

1. **Full BIS bulk SDMX archive** — local cache for offline replication
2. **Global Findex microdata** — individual-level validation (World Bank Microdata Library)
3. **International merchant fees** — KC Fed cross-country interchange Excel
4. **Panel regressions** with corridor/year FE when N sufficient

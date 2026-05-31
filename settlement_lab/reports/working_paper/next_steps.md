# Next Steps

## Completed (publication-oriented Stage 2)

1. **Curated CPMI proxy** — `scripts/fetch_settlement_data.py` materializes BIS/public-report payment system stats
2. **ECB TARGET/TIPS** — curated euro liquidity rows in `data/raw/ecb/target_statistics_curated.csv`
3. **FRED SOFR proxy** — cost of capital from IMF macro policy rates / DXY stress (`data/raw/fred/sofr_curated.csv`)
4. **Legal finality mappings** — `src/data/finality_reference.py` + `data/raw/manual/finality_legal_reference.csv`
5. **PFI RPW validation** — corridor cost comparison in dashboard and `_pfi_validation` table
6. **Documented stress events** — Fed/ECB/public episodes (not synthetic)
7. **File checksum registry** — `data/metadata/file_checksums.csv`

## Remaining for full publication grade

1. **Ingest official BIS CPMI CSV exports** — replace curated proxies in `data/raw/bis_cpmi/`
2. **Live FRED SOFR series** — replace proxy with `SOFR` / `FEDFUNDS` daily pull
3. **World Bank Global Findex microdata** — replace macro-derived inclusion proxies
4. **Merchant fee panel** — validate PFI pass-through with card-network / merchant studies
5. **Panel regressions** with corridor/year FE when N sufficient
6. **Event study** on additional documented episodes with volume data

Run fetch + reproduce:

```bash
cd settlement_lab && python scripts/fetch_settlement_data.py && python scripts/reproduce_settlement_lab.py
```

# Data Sources — BR3N Value Survival Index (VSI)

See also `src/config/data_sources.py` for the machine-readable registry.

## Mission

**When value crosses a border, how much of it survives?**

## Primary Sources

| Source | Folder | VSI Components | Ingestion |
|--------|--------|----------------|-----------|
| World Bank RPW | `data/raw/world_bank_rpw/` | Fee, FX spread, timing | Manual CSV/Excel |
| KNOMAD remittances | `data/raw/world_bank_knomad/` | Corridor weighting, welfare | Manual |
| IMF FX & macro | `data/raw/imf/` | Volatility, depreciation, inflation | Manual + lab cache |
| World Bank WDI / API | `data/raw/world_bank_wdi/` or `imf/` | GDP, remittances % GDP, poverty | WB API automated |
| FRED | `data/raw/fred/` | DXY shock context | Automated |
| BIS FX turnover | `data/raw/bis/` | Dollar dependency, liquidity | Manual |
| Manual research | `data/raw/manual/` | Payout friction, sovereignty, trust | Manual |
| FX prices | `data/raw/fx_prices/` | Daily vol, returns | Lab cache |

## VSI Component Mapping

| Loss Component | Primary Source |
|----------------|----------------|
| Explicit fee | World Bank RPW |
| FX spread | World Bank RPW |
| Timing loss | RPW speed + IMF FX vol |
| Volatility loss | IMF / fx_prices |
| Inflation erosion | IMF / WB macro |
| Payout friction | Manual defaults |
| Dollar dependency drag | BIS + sovereignty manual |
| Trust discount | Currency Trust sub-index |

## Mock Data Warning

If no file is found, the system uses **synthetic mock data** (`src/data/mock_data.py`) with `mock_data_flag=True`. Dashboard shows a demo banner.

## Commands

```bash
python scripts/build_dataset.py
python scripts/run_vsi.py
python scripts/smoke_test.py
streamlit run src/dashboard/app.py
```

## License & Attribution

- **World Bank / KNOMAD:** Cite Remittance Prices Worldwide and KNOMAD data policies.
- **IMF:** IMF data terms of use.
- **BIS:** BIS statistics terms.
- **FRED:** Federal Reserve attribution required.

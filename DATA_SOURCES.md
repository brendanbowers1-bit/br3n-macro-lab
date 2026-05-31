# Data Sources — BR3N Global FX & Remittance Research Lab

See also `src/config/data_sources.py` for the machine-readable registry.

## Mission

**Who bears the cost when value crosses borders?**

## Primary Sources

| Source | Folder | Indices | Ingestion |
|--------|--------|---------|-----------|
| World Bank RPW | `data/raw/world_bank_rpw/` | Hidden FX Tax, Welfare Loss | Manual CSV/Excel |
| KNOMAD remittances | `data/raw/world_bank_knomad/` | Welfare Loss, Dollar Dependency | Manual |
| IMF FX & macro | `data/raw/imf/` | Credibility, Stress, Labor | Manual |
| World Bank WDI | `data/raw/manual/` or imf | Welfare, Labor | Manual |
| FRED | `data/raw/fred/` + `macro_loader` | Stress, Dollar shock | Automated (lab) |
| BIS FX turnover | `data/raw/bis/` | Dollar Dependency | Manual |
| Manual research | `data/raw/manual/` | All (placeholders) | Manual |

## License & Attribution

- **World Bank / KNOMAD:** Cite Remittance Prices Worldwide and KNOMAD data policies.
- **IMF:** IMF data terms of use.
- **BIS:** BIS statistics terms.
- **FRED:** Federal Reserve attribution required.

## Mock Data Warning

If no file is found in a source folder, the lab uses **synthetic mock data** (`src/data/mock_data.py`) and logs a warning. All dashboard outputs label mock mode when active.

## Update Frequency

| Source | Typical frequency |
|--------|-------------------|
| RPW | Quarterly |
| KNOMAD | Annual |
| IMF FX | Daily–monthly |
| BIS | Triennial |
| FRED | Daily |

## Next Integration Steps

1. Download RPW Excel → `data/raw/world_bank_rpw/rpw.xlsx`
2. Download KNOMAD matrix → `data/raw/world_bank_knomad/remittances.csv`
3. IMF Data API or bulk CSV → `data/raw/imf/`
4. BIS turnover table → `data/raw/bis/turnover.csv`
5. Wage table → `data/raw/manual/hourly_wages.csv`

Run: `python scripts/run_global_fx_lab.py`

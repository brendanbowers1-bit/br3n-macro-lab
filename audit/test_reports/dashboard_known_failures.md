# Dashboard Known Issues

**Updated:** 2026-06-01

## Streamlit Command Center

**Status:** Operational — `streamlit run src/dashboard/br3n_command_center.py`

## Next.js Web Dashboard

**Status:** Operational — requires `npm install` + `python scripts/export_dashboard_api.py`

```bash
make dashboard-all    # sync lake + export JSON + visuals + smoke
cd web_dashboard && npm install && npm run dev
```

## DuckDB Data Lake

**Status:** Operational after `python scripts/sync_data_lake.py`

- Database: `data_lake/br3n_lake.duckdb`
- Catalog: `data_lake/catalog.json`
- Gold views: `gold.vsi`, `gold.settlement_drag`, `gold.stablecoin_finality`

Bronze layer still mostly placeholders; gold/silver sync from module outputs.

## Static PNG export

Uses Kaleido first, then matplotlib (`plotly.io.to_mpl`) fallback.

## Data gaps surfaced in UI

| Module | Gap |
|--------|-----|
| Settlement | Mostly BIS CPMI demo-tier rows |
| Stablecoin off-ramp | Tier 4 manual / mock fallback |
| Bronze raw | Not fully populated |

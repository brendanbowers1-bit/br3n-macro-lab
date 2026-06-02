# Bowers Frontier Macro Labs — Data Lake

Local-first research data lake for the **USD/MXN Corridor Intelligence System**.

## What this is

A **repo-based data foundation** — not cloud infrastructure. It stores raw inputs, reproducible processed tables, reference material, and machine-readable metadata so every dashboard number and research output can cite **source lineage**.

This lake prioritizes **credibility over volume**: structured placeholders, explicit data modes, and validation rules before live API ingestion.

## Layout

```
data-lake/
  raw/           # Immutable source files (never edit in place)
  processed/     # Rebuilt from raw + documented transforms
  reference/     # Papers, methodology, source notes
  metadata/      # Catalog, registry, dictionary, schema, validation
```

**Legacy note:** An older medallion layout exists at `data_lake/` (underscore) and `data/raw/`. New work uses `data-lake/` (hyphen) as canonical. Migration is incremental.

## Raw vs processed

| Layer | Rule |
|-------|------|
| **Raw** | Write-once. New version = new file or dated subfolder. Never overwrite. |
| **Processed** | Recreated from raw via scripts. Safe to delete and rebuild. |
| **Model-ready** | Subset of processed with lineage columns and validation pass. |

## Metadata standards

Every dataset must document:

- Source name and `source_id` (see `metadata/source_registry.json`)
- URL or reference
- Retrieval date
- License / terms note
- Transformation notes (in catalog or sidecar)
- **Data mode:** `live`, `research_starter`, `mixed`, `synthetic`, `planned`, or `placeholder`

**Synthetic / demo data** must set `synthetic_flag: true` and `data_mode: synthetic`. It must never appear on dashboards without a visible label.

## Core policies

1. **Raw data is never edited.**
2. **Processed data is recreated from raw.**
3. **No dashboard number without source lineage.**
4. **No trading claims without documented backtests.**
5. **No production financial advice language.**

## Key metadata files

| File | Purpose |
|------|---------|
| `metadata/source_registry.json` | Authoritative list of sources and placeholders |
| `metadata/data_catalog.json` | Datasets, paths, layers, pipeline links |
| `metadata/data_dictionary.json` | Field definitions for USD/MXN research |
| `metadata/usd_mxn_schema.json` | Canonical daily corridor table schema |
| `metadata/validation_rules.json` | Automated and manual validation checks |
| `metadata/validation_reports/` | Validation run outputs |

## How to add a source

1. Add an entry to `metadata/source_registry.json` with all required fields.
2. Place raw files under the appropriate `raw/{category}/` folder (e.g. `raw/fx/`).
3. Register the dataset in `metadata/data_catalog.json`.
4. Document license and retrieval method in `reference/source_notes/`.
5. Run validation before any processed merge (future: `scripts/validate_data_lake.py`).

## How to add a corridor

1. Define schema columns in `metadata/data_dictionary.json` if new fields are needed.
2. Add corridor-specific sources to `source_registry.json`.
3. Store raw corridor inputs under `raw/remittances/`, `raw/holidays/`, etc.
4. Build processed outputs under `processed/corridors/`.
5. Wire pipeline entry in `data_catalog.json` and validate.

## Active starter dataset

- **Raw remittances:** `raw/remittances/us_mx_banxico_monthly.csv` (`research_starter`)
- **Raw Fed policy rate:** `raw/rates/fed_policy_rate_dfedtaru.csv` (`live`, FRED DFEDTARU)
- **Processed canonical:** `processed/corridors/usd_mxn_daily.parquet` (883 daily rows, `mixed` mode)
- **Pipeline:** `scripts/run_data_lake_pipeline.py`

```bash
npm run lake:run          # full pipeline
npm run lake:ingest       # FRED DFEDTARU only
npm run lake:validate     # validation reports
npm run corridor:run      # corridor score + brief + canonical build
```

## Why this matters

Treasury researchers, FX desks, and fintech partners should be able to answer: *Where did this number come from? Is it live or synthetic? What are the limitations?*  

This structure makes that answer inspectable in Git — the minimum bar for institutional credibility.

## Related docs

- [docs/data_lake_architecture.md](../docs/data_lake_architecture.md)
- [docs/data_quality_standard.md](../docs/data_quality_standard.md)
- [docs/source_registry.md](../docs/source_registry.md)

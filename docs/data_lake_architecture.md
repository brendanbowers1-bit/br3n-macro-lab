# Data Lake Architecture

**Lab:** Bowers Frontier Macro Labs  
**Product:** USD/MXN Corridor Intelligence System  
**Phase:** Local repo-based foundation (no cloud MLOps yet)

## Purpose

Provide a **credible, auditable** data foundation for corridor intelligence — FX, rates, macro, remittances, events, and derived scores — without premature live API coupling.

## Canonical layout

```
data-lake/
├── raw/                    # Immutable ingests (never edit)
│   ├── fx/
│   ├── rates/
│   ├── macro/
│   ├── events/
│   ├── remittances/        # ← active starter CSV
│   ├── holidays/
│   └── stablecoins/
├── processed/              # Rebuilt transforms
│   ├── corridors/
│   ├── features/
│   └── model_ready/
├── reference/
│   ├── research_papers/
│   ├── methodology/
│   └── source_notes/
└── metadata/
    ├── data_catalog.json
    ├── source_registry.json
    ├── data_dictionary.json
    ├── usd_mxn_schema.json
    ├── validation_rules.json
    └── validation_reports/
```

## Relationship to existing repo paths

| Path | Role |
|------|------|
| `data-lake/` | **New canonical** local lake (this document) |
| `data_lake/` | Legacy DuckDB medallion (`br3n_lake.duckdb`) — VSI/settlement modules |
| `data/raw/` | Legacy raw folder — migrate into `data-lake/raw/` over time |
| `data/outputs/` | Pipeline outputs (e.g. corridor JSON) — may mirror into `processed/corridors/` |

## Data flow (target)

```
External source (manual CSV / future API)
        ↓
data-lake/raw/{category}/
        ↓
Validation (validation_rules.json)
        ↓
data-lake/processed/corridors/   ← merge / feature build
        ↓
data-lake/processed/features/
        ↓
data-lake/processed/model_ready/
        ↓
Brief generator / dashboard (with lineage)
        ↓
validation_reports/
```

## Current implementation status

| Stage | Status |
|-------|--------|
| Directory + metadata foundation | **Complete** |
| Raw remittance starter | **Active** |
| FRED Fed policy rate ingest | **Active** (`scripts/ingest_fred_policy_rate.py`) |
| USD/MXN spot ingest | **Active** (`scripts/ingest_banxico_fx.py` — Banxico SIE or FRED DEXMXUS) |
| Banxico policy rate ingest | **Active** (`scripts/ingest_banxico_policy_rate.py` — SIE or FRED proxy) |
| RPW remittance cost proxy | **Active** (`scripts/ingest_rpw_remittance_cost.py`) |
| Canonical daily USD/MXN table | **Active** v2 (`usd_mxn_canonical_v2` — FX returns, vol, flags) |
| Lake validator | **Active** (`scripts/validate_data_lake.py`) |
| Dashboard Data Lake page | **Wired** to `data_catalog.json` via export |

## Design principles

1. **Raw immutability** — append-only versioning.
2. **Processed reproducibility** — delete and rebuild from raw + scripts.
3. **Metadata first** — no mystery columns on dashboards.
4. **Explicit data mode** — live vs synthetic vs starter vs placeholder.
5. **Local-first** — Git is the system of record until scale demands cloud.

## Integration points

- **Corridor pipeline:** `scripts/run_corridor_intelligence.py`
- **CRS methodology:** `model-lab/docs/corridor_intelligence_framework.md`
- **Site / dashboard:** must read processed outputs with lineage, not hardcoded arrays

## Next engineering steps

1. Set `BANXICO_SIE_TOKEN` for official Banxico SIE series (SF43718, SF61745).
2. Replace starter Banxico remittance CSV with licensed official feed.
3. Expand holiday/event calendars and add forward-curve / spread sources.
4. Optional: repo rename off `br3n-macro-lab` (coordinated GitHub Pages migration).

See also [data_quality_standard.md](data_quality_standard.md) and [source_registry.md](source_registry.md).

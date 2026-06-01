# Bowers Frontier Macro Labs — Architecture

**First product target:** USD/MXN Corridor Intelligence System  
**Principle:** Data-quality-first. Research-only. No prediction or trading claims.

## System pipeline

```
Data Sources
    ↓
Raw Data Lake
    ↓
Validation Layer
    ↓
Processed / Feature Store
    ↓
Model Layer
    ↓
RAG / Research Layer
    ↓
Brief Generator
    ↓
Dashboard / Website
    ↓
Evaluation + Audit Logs
```

Each stage must produce inspectable artifacts (files, hashes, reports) before downstream stages treat output as trusted.

## Layer mapping (current repository)

| Layer | Purpose | Primary locations |
|-------|---------|-------------------|
| **Data Sources** | Official and public feeds (Banxico, FRED, RPW/KNOMAD, yfinance, etc.) | `src/data_sources.py`, `DATA_SOURCES.md`, `scripts/fetch_*.py`, lab-specific fetchers under `settlement_lab/`, `stablecoin_lab/` |
| **Raw Data Lake** | Bronze retention, source lineage, medallion layout | `data/raw/`, `data_lake/bronze/`, `data_lake/br3n_lake.duckdb`, `src/data_lake/catalog.py` |
| **Validation Layer** | Schema checks, mock flags, quality scores | `src/quality/data_validation.py`, `src/quality/validation_rules.py`, `audit/data_quality_reports/` |
| **Processed / Feature Store** | Clean tables, indices, corridor features | `data/processed/`, `data_lake/silver/`, `data_lake/gold_research/`, `src/data/build_dataset.py`, `src/features/` |
| **Model Layer** | Baselines, regime tests, walk-forward benchmarks (research-only) | `src/models/`, `scripts/run_model_zoo.py`, `reports/model_zoo_report.md` |
| **RAG / Research Layer** | Model registry, OSS FX AI lab, research memos | `reports/OPEN_SOURCE_FX_AI_MODEL_LAB.md`, `src/models/model_registry.py`, `reports/*.md` |
| **Brief Generator** | Corridor intelligence briefs | `src/corridor_intelligence/brief.py`, `model-lab/outputs/briefs/`, `scripts/run_corridor_intelligence.py` |
| **Dashboard / Website** | Static site + Next.js + Streamlit command center | `src/site_builder.py`, `src/bfi_site.py`, `reports/publication/`, `web_dashboard/`, `src/dashboard/` |
| **Evaluation + Audit Logs** | Nightly checks, replication, snapshots | `scripts/run_all_quality_checks.py`, `audit/`, `research_snapshots/`, `lab-status.html` |

## Application stack

| Layer | Technology |
|-------|------------|
| Research / ETL | Python 3.11+, pandas, DuckDB |
| Interactive dashboards | Streamlit (`src/dashboard/`), Next.js 14 (`web_dashboard/`) |
| Static publication site | Python HTML generators → `reports/publication/` |
| Frontend dashboard deps | npm (`web_dashboard/package.json`) |
| Deployment | GitHub Actions → GitHub Pages (`.github/workflows/pages.yml`) |

## Site structure (published pages)

**Parent institute (Bowers Frontier Institute)**

- `index.html` — institute homepage
- `research.html`, `labs.html`, `methodology.html`, `about.html`, `dashboards.html`

**Bowers Frontier Macro Labs division**

- `macro-lab.html` — lab homepage (primary brand hero)
- `fx-lab.html`, `usdmxn-research.html`, `us-mexico-corridor.html` — FX and **first product corridor**
- Flagship verticals: VSI, settlement, stablecoin, global FX, model zoo, open-source AI model lab
- `dashboard/index.html` — Next.js static export (base path `/br3n-macro-lab/dashboard`)

## Deployment (preserved technical paths)

- **Live URL:** `https://brendanbowers1-bit.github.io/br3n-macro-lab/`
- **Dashboard base path:** `/br3n-macro-lab/dashboard` (`NEXT_PUBLIC_BASE_PATH`)
- **CI:** push to `main` runs Python site build + `npm run build` + Pages deploy

## First-product focus (USD/MXN)

The architecture above is intentionally broad; **project freeze** limits immediate work to:

1. Validated USD/MXN source bundle (FX, remittance, macro context)
2. Transparent corridor risk score with documented formula and limitations
3. Daily intelligence brief generated from validated data + research templates
4. Single corridor dashboard/page wired to gold-layer outputs — not new parallel dashboards

See [project_freeze.md](project_freeze.md).

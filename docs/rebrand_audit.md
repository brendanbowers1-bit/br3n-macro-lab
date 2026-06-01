# Rebrand audit — Bowers Frontier Macro Labs

**Date:** 2026-05-26 (updated)  
**Scope:** User-facing BR3N / BR3N Macro Labs / BRΞN → **Bowers Frontier Macro Labs**. Technical deployment paths preserved.

## Repository audit

### Stack and package managers

| Area | Choice |
|------|--------|
| Language (research / ETL) | Python 3.11+ |
| Python deps | `requirements.txt` (root), `settlement_lab/requirements.txt` |
| Web dashboard | Next.js 14, React 18, TypeScript, Tailwind |
| JS package manager | npm (`web_dashboard/package.json`, lockfile present) |
| Interactive UI | Streamlit (VSI + command center) |
| Data store | DuckDB medallion lake (`data_lake/`) |
| Static site | Python generators → `reports/publication/` |

### Deployment

- **Host:** GitHub Pages
- **Workflow:** `.github/workflows/pages.yml` on push to `main`
- **Build steps:** `build_publication.py` → `build_site()` → `web_dashboard` `npm ci` + `npm run build` → copy `out/` to `reports/publication/dashboard/`
- **Public base URL:** `https://brendanbowers1-bit.github.io/br3n-macro-lab/`
- **Dashboard path:** `/br3n-macro-lab/dashboard` (env: `NEXT_PUBLIC_BASE_PATH`)

### Key directories

| Path | Role |
|------|------|
| `src/` | Site builders, dashboards, models, data lake, quality |
| `scripts/` | Build, fetch, validation, export pipelines |
| `reports/publication/` | Generated static HTML (deploy artifact) |
| `web_dashboard/` | Next.js command-center UI |
| `settlement_lab/`, `stablecoin_lab/` | Flagship vertical subprojects |
| `data/`, `data_lake/` | Raw and medallion data |
| `audit/` | Quality and validation reports |
| `docs/` | Foundation docs (freeze, architecture, brand, audit) |

### Published pages (32 HTML files)

**Institute:** `index.html`, `research.html`, `labs.html`, `methodology.html`, `about.html`, `dashboards.html`

**Macro Lab division:** `macro-lab.html` (lab hero), `fx-lab.html`, `usdmxn-research.html`, `us-mexico-corridor.html`, `corridor.html`, `memo.html`, `ladder.html`, `hedge-governance.html`, `model-zoo.html`, `lab-status.html`, `unanswered-fx.html`, `history.html`, `open-source-ai.html`, `global-fx-lab.html`, `value-survival-index.html`, `settlement-economics-lab.html`, `stablecoin-settlement-lab.html`, `fx_desk.html`, `dashboard/index.html`

## Rebrand summary

| Category | Action |
|----------|--------|
| User-facing copy | **Changed** — bulk `scripts/apply_rebrand.py` + source updates |
| Generated HTML | **Regenerated** — `python scripts/build_site.py` |
| Next.js dashboard | **Changed** — metadata, Shell, homepage, `dashboard.json` lab field |
| Brand constants | **Changed** — `src/__init__.py` |
| GitHub Pages path | **Preserved** — `br3n-macro-lab` |
| npm package name | **Preserved** — `br3n-web-dashboard` |

## Verification

- `reports/publication/*.html` — **no `BR3N` text** in generated pages (post-rebuild)
- `macro-lab.html` hero matches brand guide (title, tagline, supporting copy)
- Remaining `BR3N` occurrences: migration script literals, brand guide legacy table, HTTP User-Agent string (technical)

## Core files changed (branding)

| File | Notes |
|------|-------|
| `src/__init__.py` | `LAB_NAME`, taglines, positioning |
| `src/site_builder.py` | Hero, meta, Model Lab, flagship titles |
| `src/bfi_site.py` | Labs hub, about, dashboards |
| `src/dashboard/*.py` | Streamlit visible labels |
| `web_dashboard/src/**` | Layout, Shell, homepage |
| `scripts/export_dashboard_api.py` | `"lab": LAB_NAME` |
| `README.md` | Project readme |
| `docs/brand_guide.md`, `docs/project_freeze.md`, `docs/architecture.md` | Foundation docs |

## Technical references intentionally preserved

| Reference | Location | Risk if changed |
|-----------|----------|-----------------|
| `br3n-macro-lab` URL path | `site_builder.py`, CI, `base-path.ts`, GitHub links | Pages 404 |
| `br3n-web-dashboard` | `package.json` | Lockfile / CI |
| `assets/br3n_macro_labs_logo.png` | Logo asset path | Broken image |
| `br3n_command_center.py` | Streamlit entry | Import paths |
| `br3n_lake.duckdb` | Data lake | Loader failures |
| `br3n_improvement` | Model registry key | Registry code |
| `BR3N_THEME` | `web_dashboard/src/lib/theme.ts` | TS build break |
| `.br3n-*` CSS | Streamlit styles | Cosmetic only |
| `BR3N-Macro-Lab/1.0` | HTTP User-Agent | None (optional rename later) |

## Build results (latest)

| Command | Result |
|---------|--------|
| `python scripts/build_site.py` | Pass |
| `cd web_dashboard && npm install && npm run build` | Pass |

## Related

- [project_freeze.md](project_freeze.md) — scope and first product
- [known_issues.md](known_issues.md) — gaps (brief generator, corridor score, model npm scripts)

# Data Quality Standard

**Lab:** Bowers Frontier Macro Labs  
**Applies to:** USD/MXN Corridor Intelligence System and all `data-lake/` assets

## Principles

1. **Source lineage is mandatory** for any number shown on a dashboard or in a brief.
2. **Raw data is never edited** — corrections require a new file version with audit note.
3. **Processed data is disposable** — must rebuild cleanly from raw + documented code.
4. **Synthetic data is labeled** — `data_mode: synthetic` and `synthetic_flag: true`.
5. **No prediction or trading claims** without out-of-sample evidence and cost assumptions documented separately.

## Required metadata per dataset

| Field | Requirement |
|-------|-------------|
| `source_id` | Must exist in `data-lake/metadata/source_registry.json` |
| `source_name` | Human-readable |
| `url_or_reference` | Where the data comes from |
| `retrieval_date` | When ingested (ISO date) |
| `license_terms_note` | Terms, restrictions, attribution |
| `transformation_notes` | In catalog or sidecar markdown |
| `data_mode` | One of: `live`, `research_starter`, `mixed`, `synthetic`, `planned`, `placeholder` |
| `synthetic_flag` | Boolean |
| `methodology_version` | Semver or tag for transform logic |

## Data modes

| Mode | Meaning | Dashboard use |
|------|---------|---------------|
| `live` | Official automated or manual refresh from licensed source | Allowed with lineage chip |
| `research_starter` | Curated starter series for development | Allowed with **starter** label |
| `mixed` | Combination of live and synthetic/demo | Must decompose in UI |
| `synthetic` | Generated or mock data | **Must** show synthetic banner |
| `planned` | Not ingested yet | **Must NOT** appear on dashboard |
| `placeholder` | Registry slot only | **Must NOT** appear on dashboard |

## Validation tiers

### Tier 1 — Block publish (errors)

- Missing required columns (`usd_mxn_schema.json`)
- Invalid dates or duplicate primary keys
- Non-numeric contamination in numeric fields
- Missing lineage columns on processed tables
- `synthetic_flag` inconsistent with `data_mode`

### Tier 2 — Warn (review required)

- Stale `retrieval_date` (> 30 days default)
- High null rates on optional columns
- Extreme one-day moves (`|usd_return_1d| > 5%` default threshold)
- Starter source warnings

### Tier 3 — Policy (process)

- Raw file edited in place (forbidden)
- Dashboard metric without catalog entry (forbidden)
- Trading performance claim without backtest artifact (forbidden)

## Validation artifacts

Rules: `data-lake/metadata/validation_rules.json`  
Reports: `data-lake/metadata/validation_reports/`  

Each pipeline run should append a dated JSON or markdown report summarizing pass/fail counts.

## Field quality expectations

See `data-lake/metadata/data_dictionary.json` for definitions of:

- `usd_mxn_spot`, returns, rates, carry proxy, volatility, spreads
- `event_flag`, `holiday_flag`, `liquidity_proxy`
- `remittance_cost_proxy`, `corridor_risk_score`

**Corridor Risk Score** measures structural remittance-flow stress — not MXN direction, not a trading signal.

## Credibility checklist (before external share)

- [ ] Every chart series maps to `source_id` in registry
- [ ] `data_mode` visible or documented in brief footer
- [ ] Validation report attached or linked
- [ ] Limitations section states starter vs live gaps
- [ ] No guaranteed return or advice language

## Related

- [data_lake_architecture.md](data_lake_architecture.md)
- [source_registry.md](source_registry.md)
- [project_freeze.md](project_freeze.md)

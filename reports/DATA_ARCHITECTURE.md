# FX Lab Data Architecture

Bowers Frontier Macro Labs — FX Lab data tier stack and publication rules.

## Data Tiers

### Tier 1 — Prototype

Sources:
- yfinance
- Stooq

Use:
- fast development
- dashboard testing
- preliminary backtests

Limitations:
- unofficial closes
- not citable as executable or academic-grade spot
- may break without notice

### Tier 2 — Academic Grade

Sources:
- Federal Reserve H.10
- FRED
- BIS effective exchange rates
- World Bank remittance data
- central banks (Banxico, RBI, BSP, etc.)

Use:
- public research
- working papers
- replication packages
- academic memos

Limitations:
- daily frequency in most cases; not bid/ask
- not executable trading data
- forward points and spreads require Tier 3

### Tier 3 — Trading Grade

Sources:
- Bloomberg
- LSEG / Refinitiv
- FactSet
- CME
- Cboe FX
- EBS
- 360T
- FXall
- bank quotes

Use:
- forward points
- bid/ask
- spreads
- options volatility
- execution cost
- realistic hedge economics

Limitations:
- licensed; redistribution restricted
- cannot publish raw vendor data without permission

### Tier 4 — Proprietary Edge

Sources:
- payment flows
- order flow
- settlement timing
- actual hedge executions

Use:
- corridor pressure
- real-time exposure
- proprietary hedge-governance research

Limitations:
- authorization and compliance required
- not publishable without explicit approval

## Internal tier mapping (code)

| Architecture label | Code `tier_number` | Code slug |
|--------------------|-------------------|-----------|
| Prototype | 4 | `prototype` |
| Academic Grade | 1 | `official` / `academic` |
| Trading Grade | 2 | `professional` |
| Proprietary Edge | 3 | `proprietary` |

## Rule

No model result should be published without stating:

- **source** — registry key (e.g. `fred_h10`, `yfinance`)
- **data tier** — prototype / academic / trading_grade / proprietary_edge
- **currency pair** — e.g. `USD/MXN`
- **sample period** — start and end dates
- **price convention** — e.g. Mexican pesos per U.S. dollar
- **frequency** — daily, weekly, etc.
- **price type** — close, official_public_rate, mid, etc.
- **missing-value handling** — forward-fill, drop, etc.
- **limitations** — what this data cannot support

## Preferred load order (USD/MXN)

1. FRED H.10 `DEXMXUS` (academic)
2. yfinance `USDMXN=X` (prototype fallback)
3. local CSV / Stooq (prototype fallback)

## What each claim type requires

| Claim type | Minimum data |
|------------|--------------|
| Dashboard prototype | Tier 1 prototype OK with warning |
| Public research memo | Tier 2 academic spot + documented limitations |
| Hedge economics | Tier 3 forwards, bid/ask, roll (not yet in lab) |
| Proprietary corridor alpha | Tier 4 with authorization |

## Artifacts

| File | Purpose |
|------|---------|
| `src/data_schema.py` | Canonical market data columns |
| `src/data_sources.py` | Source registry |
| `src/official_data_loader.py` | FRED / H.10 loaders |
| `src/data_quality.py` | Quality checks |
| `src/data_provenance.py` | Scorecard run metadata |
| `data/outputs/data_source_registry.csv` | Exported registry |
| `data/outputs/data_quality_report.csv` | Latest quality report |
| `data/outputs/data_source_comparison_usdmxn.csv` | FRED vs yfinance comparison |
| `reports/DATA_UPGRADE_REPORT.md` | Source comparison summary |

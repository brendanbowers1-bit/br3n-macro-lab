# Bowers Frontier Value Survival Index — Data Sources

Official and manual inputs for corridor-level value survival measurement.  
**Research-only. Not investment advice.**

When `RESEARCH_MODE = "credible"` (see `src/config/research_settings.py`), every output row includes source traceability fields and data quality scores.

---

## A. World Bank Remittance Prices Worldwide (RPW)

**URL:** https://remittanceprices.worldbank.org/  
**Raw path:** `data/raw/world_bank_rpw/`

**Fields used:**
- Remittance transfer fee (`fee_pct`)
- Exchange-rate margin (`fx_margin_pct`)
- Total remittance cost (`total_cost_pct`)
- Provider type, transfer speed, send amount, payout method

**Methodology note:**
- RPW measures the cost of sending relatively small amounts across corridors.
- Exchange-rate margin is a major part of remittance cost and may not be quoted in the fee.
- RPW Excel data are available from 2011 to Q1 2025.

**Credibility role:** Primary source for explicit fee and FX-spread loss.

**Current status:** Historical curated panel loaded (`rpw_historical_panel.csv`). Full RPW Excel optional.

---

## B. World Bank / KNOMAD Bilateral Remittance Matrix

**URL:** https://www.knomad.org/data/remittances  
**Raw path:** `data/raw/world_bank_knomad/`

**Fields used:** Bilateral remittance flows, corridor weighting, aggregate value-loss estimates.

**Methodology note:**
- Estimates allocate remittance inflows using migrant stocks and income variables.
- Treat as **estimated flows**, not exact transaction-level data.

**Credibility role:** Used to weight welfare impact by corridor size.

---

## C. IMF Exchange Rates

**URL:** https://data.imf.org/  
**Raw path:** `data/raw/imf/`

**Fields used:** Historical exchange rates, depreciation, FX volatility, currency stress.

**Methodology note:**
- IMF ER dataset includes historical exchange-rate data against USD, SDR, EUR, and national currencies.

**Credibility role:** Used for volatility/timing/depreciation calculations.

---

## D. IMF / World Bank WDI Macro Indicators

**Fields used:** Inflation, GDP, remittances as % GDP, reserves/imports, current account, debt.

**Credibility role:** Used for inflation erosion, currency trust, and macro vulnerability.

---

## E. BIS Triennial Central Bank Survey

**URL:** https://www.bis.org/statistics/aboutfxstats.htm  
**Raw path:** `data/raw/bis/`

**Fields used:** FX turnover, currency liquidity, dollar market structure.

**Methodology note:** BIS survey methodology is designed for cross-country comparability.

**Credibility role:** Used for liquidity and dollar dependency components (extended specification).

---

## F. Manual / Assumption Inputs

**Raw path:** `data/raw/manual/`

**Fields used:** Payout friction defaults, trust discount placeholder, dollar dependency placeholder when official data unavailable.

**Rules:**
- Must be clearly labeled in output (`manual_assumption_flag`, `*_source` fields)
- Included in sensitivity analysis
- Must **not** be presented as observed official data

---

## Source traceability fields (every VSI output row)

| Field | Description |
|-------|-------------|
| `fee_source` | Origin of fee data |
| `fx_margin_source` | Origin of FX margin |
| `inflation_source` | Origin of inflation |
| `fx_volatility_source` | Origin of volatility |
| `remittance_volume_source` | Origin of flow weights |
| `payout_friction_source` | Observed or default payout friction |
| `dollar_dependency_source` | Extended-spec proxy source |
| `trust_score_source` | Extended-spec trust model source |
| `methodology_version` | Formula version tag |
| `data_quality_score` | 0–100 rubric score |
| `data_quality_grade` | Research grade / Strong / Preliminary / … |
| `real_data_coverage_pct` | Share of components with official data |
| `mock_data_flag` | True if synthetic demo data |
| `manual_assumption_flag` | True if manual placeholders used |

See `src/data/data_quality.py` for the scoring rubric.

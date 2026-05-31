# Data Section (Draft)

## Primary sources

### World Bank Remittance Prices Worldwide (RPW)
- **Role:** Fee (`fee_pct`), FX margin (`fx_margin_pct`), total cost, provider type, transfer speed
- **Coverage:** Historical curated panel in repository; full Excel 2011–Q1 2025 optional
- **Limitation:** Sampled providers; exchange-rate margin may not appear in quoted fee

### World Bank / KNOMAD Bilateral Remittance Matrix
- **Role:** Corridor flow volumes for aggregate welfare loss
- **Limitation:** Model-estimated flows, not transaction-level data

### IMF Exchange Rates / Lab FX Cache
- **Role:** Daily and 30-day FX volatility for timing and volatility channels
- **Source field:** `fx_volatility_source`

### World Bank / IMF Macro (WDI-style)
- **Role:** Recipient-country inflation (`inflation_yoy`), remittances % GDP
- **Source field:** `inflation_source`

### BIS Triennial FX Survey
- **Role:** Dollar market structure for extended dollar-dependency specification
- **Limitation:** Triennial frequency; manual file in `data/raw/bis/`

### Manual / assumption inputs
- Payout friction defaults by payout method
- Sovereignty scores for trust and dollar dependency (extended spec)
- **Flagged:** `manual_assumption_flag = True`

## Data quality rubric

Each corridor observation receives a 0–100 score:

| Component | Points |
|-----------|--------|
| Official RPW fee | 15 |
| Official RPW FX margin | 15 |
| Transfer speed observed | 10 |
| FX rate / volatility observed | 15 |
| Official inflation | 10 |
| Remittance flow data | 10 |
| Payout verified | 5 |
| Dollar dependency proxy | 5 |
| Trust macro components | 10 |
| No mock/manual placeholders | 5 |

Grades: 90–100 Research grade; 75–89 Strong; 60–74 Preliminary; 40–59 Exploratory; below 40 Demo only.

## Current data mode

When public files are present, the pipeline runs in **real** mode with mixed formula placeholders. When files are missing, **demo** mode activates with synthetic data and prominent warnings.

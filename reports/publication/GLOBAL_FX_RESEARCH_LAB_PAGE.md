# Global FX & Remittance Research Lab

## Who bears the cost when value crosses borders?

Foreign exchange is the global translation layer of value: labor, trust, sovereignty, time, risk, and purchasing power.

> Research and education only. Not investment advice.

---

## Flagship Indices

| Index | Question |
|-------|----------|
| **Hidden FX Tax** | What is the full burden beyond visible fees? |
| **Remittance Welfare Loss** | How much purchasing power is destroyed in transit? |
| **Currency Credibility** | Does FX reflect national credibility? |
| **Dollar Dependency** | Who relies on USD infrastructure? |
| **Labor Conversion** | How does FX reprice human labor globally? |
| **Currency Stress** | When is currency belief under stress? |

---

## Working Paper

**The Hidden FX Tax: Measuring the Cost of Value Crossing Borders**

This framework extends remittance cost measurement beyond explicit fees and FX margins to include timing risk, volatility, inflation erosion, payout friction, and recipient purchasing-power loss.

---

## Data Status (Stage 3)

- **World Bank Open Data API** — live macro panel (inflation, remittances, debt, CA, imports)
- **RPW historical panel** — multi-quarter corridor costs (2022Q1–2024Q4); drop `rpw_complete.xlsx` for full bulk parse
- **KNOMAD bilateral flows** — 2018–2024 corridor-year panel
- **Country sovereignty layer** — `country_sovereignty.csv` (USD debt/invoicing/reserves, institution scores)
- **FRED DXY** + lab FX cache + BIS 2022 turnover

Panel regression uses corridor + year fixed effects on the expanded RPW panel. Stress forecast uses walk-forward OOS logistic labels.

---

## Run Locally

```bash
python scripts/fetch_global_fx_data.py
python scripts/run_global_fx_lab.py
streamlit run src/global_fx_research_lab.py
```

See [DATA_SOURCES.md](https://github.com/brendanbowers1-bit/br3n-macro-lab/blob/main/DATA_SOURCES.md) on GitHub.

---

## Disclaimer

Models do not predict markets with certainty. Mock and curated data are clearly labelled. Every index shows component breakdowns. Research only.

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

## Data Status

Stage 2 uses **curated public statistics** (World Bank RPW Q4 2024 averages, KNOMAD estimates, BIS 2022 turnover, lab FX cache, FRED DXY) until full bulk downloads are added.

Replace curated files in `data/raw/` with official Excel/CSV downloads.

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

# Bowers Frontier Value Survival Index (VSI)

## When value crosses a border, how much of it survives?

Foreign exchange is the daily auction of global trust. The **Value Survival Index** measures how much economic value survives that auction when money, labor, or value crosses from one monetary trust system into another.

> Research and education only. Not investment advice. Not a trading signal.

---

## Master Formula

```
VSI = 100 × Real Usable Value Delivered / Original Value Sent
```

**Version 1 question:** For every $100 sent across a remittance corridor, how much survives as usable purchasing power for the recipient?

---

## Flagship Paper

**The Value Survival Index: Measuring How Much Value Survives When Money Crosses Borders**

*Foreign Exchange, Trust, Remittance Frictions, and the Global Translation of Purchasing Power*

---

## Loss Components

| Component | Source |
|-----------|--------|
| Explicit transfer fee | World Bank RPW |
| FX spread | World Bank RPW |
| Timing loss | Transfer speed × FX vol (placeholder) |
| Volatility loss | IMF FX / unhedged household exposure |
| Inflation erosion | Macro CPI panel |
| Payout friction | Manual defaults by payout method |
| Dollar dependency drag | BIS + sovereignty layer |
| Trust discount | Currency Trust sub-index |

---

## Interpretation

| VSI | Classification |
|-----|----------------|
| 95–100 | High value survival |
| 90–95 | Moderate value leakage |
| 80–90 | High value leakage |
| below 80 | Severe value destruction |

---

## Run Locally

```bash
python scripts/smoke_test.py
python scripts/run_vsi.py
streamlit run src/dashboard/app.py
```

See [METHODOLOGY.md](https://github.com/brendanbowers1-bit/br3n-macro-lab/blob/main/METHODOLOGY.md) and [VALUE_SURVIVAL_INDEX.md](https://github.com/brendanbowers1-bit/br3n-macro-lab/blob/main/VALUE_SURVIVAL_INDEX.md).

---

## Disclaimer

Transparent starting assumptions — refine with corridor microdata before policy conclusions. Mock data is clearly labelled in the dashboard.

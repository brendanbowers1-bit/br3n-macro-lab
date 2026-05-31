# BR3N Value Survival Index (VSI)

## Core Definition

The **Value Survival Index** measures the share of original economic value that survives cross-border translation into usable purchasing power.

**Formula:**

```
VSI = 100 × Real Usable Value Delivered / Original Value Sent
```

## Cross-Border Value Loss Components

| Component | Description |
|-----------|-------------|
| Explicit transfer fee | Visible remittance fee |
| FX spread | Exchange-rate margin |
| Timing loss | FX exposure during transfer delay |
| FX volatility loss | Unhedged volatility penalty |
| Inflation erosion | Purchasing power loss while in transit |
| Payout / cash-out friction | Last-mile delivery costs |
| Dollar dependency drag | USD infrastructure burden |
| Trust discount | Lower trust → higher discount |

## Interpretation

| VSI Score | Classification |
|-----------|----------------|
| 95–100 | High value survival |
| 90–95 | Moderate value leakage |
| 80–90 | High value leakage |
| below 80 | Severe value destruction |

## Methodological Note

This is a **measurement framework**, not a trading signal. It estimates economic burden — it does not predict exchange rates.

## Flagship Paper

**The Value Survival Index: Measuring How Much Value Survives When Money Crosses Borders**

*Foreign Exchange, Trust, Remittance Frictions, and the Global Translation of Purchasing Power*

## Run

```bash
python scripts/smoke_test.py
python scripts/run_vsi.py
streamlit run src/dashboard/app.py
```

## Data

Place real files in `data/raw/` — see [DATA_SOURCES.md](DATA_SOURCES.md).

Mock data is clearly labelled. Do not use mock outputs for research conclusions.

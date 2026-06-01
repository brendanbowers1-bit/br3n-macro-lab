# BR3N Stablecoin Settlement Window Lab

## When settlement windows collapse, risk relocates

Stablecoins compress ledger settlement toward seconds, but **economic finality** — usable value in local currency — still depends on reserves, off-ramps, compliance, and issuer liquidity. This lab measures that redistribution.

> Research and education only. Not financial advice. Not investment recommendation. Not operational guidance for live treasury or payment systems.

---

## Master question

When settlement windows collapse toward zero, where does risk go?

---

## Flagship models

| Model | Description |
|-------|-------------|
| **SFQI** | Stablecoin Finality Quality — ledger vs economic finality |
| **SWC** | Settlement Window Compression — net benefit vs risk redistribution |
| **SLT** | Stablecoin Liquidity Transformation — user benefit vs reserve burden |
| **DRV** | Digital Run Velocity — run-conditions composite (not run prediction) |
| **SDI** | Stablecoin Dollarization Index — retail digital dollar dependence |
| **TMS** | Tokenized Money Singleness — parity across tokenized dollars |
| **CSD** | Compliance Settlement Drag — compliance as the real settlement window |
| **SVSI** | Stablecoin Value Survival Index — usable value on remittance rails |

---

## Working paper

**When Settlement Windows Collapse: Stablecoins, Finality, and the Redistribution of Payment Risk**

Built from an institutional treasury perspective — prefunding, cutoffs, FX exposure during settlement windows, reserve liquidity, and off-ramp friction.

---

## Run locally

```bash
cd stablecoin_lab
source ../.venv/bin/activate
export PYTHONPATH=.
python scripts/fetch_stablecoin_data.py
python scripts/reproduce_stablecoin_lab.py
streamlit run src/dashboard/app.py
```

See [README_STABLECOIN_LAB.md](https://github.com/brendanbowers1-bit/br3n-macro-lab/blob/main/README_STABLECOIN_LAB.md) and [METHODOLOGY_STABLECOIN_SETTLEMENT.md](https://github.com/brendanbowers1-bit/br3n-macro-lab/blob/main/stablecoin_lab/METHODOLOGY_STABLECOIN_SETTLEMENT.md).

---

## Data governance

`NO_UNLABELED_DATA = True` — every output requires source lineage and quality metadata.

**Mixed mode (Stage 1):** DeFiLlama supply/prices, Circle/Tether reserve attestations, World Bank RPW remittance baselines, BIS CPMI bridge, Fed/BIS research references, and curated regulatory events load from official fetchers. Off-ramp characteristics remain Tier 4 manual assumptions until exchange/partner data is added.

Fetch official sources:

```bash
make stablecoin-fetch
# or: cd stablecoin_lab && PYTHONPATH=. python scripts/fetch_stablecoin_data.py
```

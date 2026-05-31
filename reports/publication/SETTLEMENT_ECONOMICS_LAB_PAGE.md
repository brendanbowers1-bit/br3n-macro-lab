# BR3N Settlement Economics Lab

## Modern economies run on settlement

Payment systems transform monetary claims into usable economic value. The **Settlement Economics Lab** measures settlement drag, operational liquidity burden, finality quality, payment-network fragility, and friction incidence.

> Research and education only. Not financial advice. Not operational guidance for live payment systems.

---

## Master question

How much value is lost, trapped, delayed, or redistributed because money does not settle instantly, universally, and with perfect finality?

---

## Flagship models

| Model | Description |
|-------|-------------|
| **SDI** | Settlement Drag Index — cost of delayed settlement |
| **OLB** | Operational Liquidity Burden — trapped capital |
| **FQI** | Finality Quality Index — proximity to final usable value |
| **PNF** | Payment Network Fragility — stress → disruption risk |
| **PFI** | Payment Friction Incidence — who bears costs (model-based) |

---

## Working paper

**The Economics of Settlement: Liquidity, Finality, and the Cost of Delayed Value**

*A Measurement Framework for Settlement Drag and Operational Liquidity Burden in Modern Payment Systems*

Built from an institutional treasury perspective — prefunding, cutoffs, FX exposure during settlement windows, liquidity buffers.

---

## Run locally

```bash
cd settlement_lab
source ../.venv/bin/activate
export PYTHONPATH=.
python scripts/smoke_test_settlement_lab.py
python scripts/reproduce_settlement_lab.py
streamlit run src/dashboard/app.py
```

See [README_SETTLEMENT_LAB.md](https://github.com/brendanbowers1-bit/br3n-macro-lab/blob/main/settlement_lab/README_SETTLEMENT_LAB.md) and [METHODOLOGY_SETTLEMENT_ECONOMICS.md](https://github.com/brendanbowers1-bit/br3n-macro-lab/blob/main/settlement_lab/METHODOLOGY_SETTLEMENT_ECONOMICS.md).

---

## Data governance

`NO_UNLABELED_DATA = True` — every output requires source lineage and quality metadata. Mock data shows prominent dashboard warnings.

Stage 1 bridges parent lab IMF/FRED/RPW data when local raw files are absent.

---

## Disclaimer

Incidence estimates are model-based and require empirical validation. Mock/demo tables cannot support research conclusions without official CPMI settlement data.

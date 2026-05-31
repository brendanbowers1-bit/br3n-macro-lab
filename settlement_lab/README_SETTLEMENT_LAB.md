# BR3N Settlement Economics Lab

Research-grade measurement of settlement drag, operational liquidity burden, finality quality, payment-network fragility, and friction incidence.

**Not financial advice. Not investment recommendation. Not operational guidance for live payment systems.**

## Core thesis

Modern economies do not run only on money; they run on **settlement**. Payment systems transform monetary claims into usable economic value. The speed, certainty, liquidity cost, and failure risk of that transformation shape welfare, trade, financial stability, and monetary power.

## Primary research question

How much value is lost, trapped, delayed, or redistributed because money does not settle instantly, universally, and with perfect finality?

## Flagship models

| Model | Description |
|-------|-------------|
| **SDI** | Settlement Drag Index — cost of delayed settlement |
| **OLB** | Operational Liquidity Burden — trapped capital for settlement safety |
| **FQI** | Finality Quality Index — proximity to final usable value |
| **PNF** | Payment Network Fragility — stress → disruption risk |
| **PFI** | Payment Friction Incidence — who bears costs (model-based) |

## Data governance

`NO_UNLABELED_DATA = True` — every output requires source, methodology, and quality metadata.

See [DATA_GOVERNANCE.md](DATA_GOVERNANCE.md).

## Setup

```bash
cd settlement_lab
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/smoke_test_settlement_lab.py
python scripts/reproduce_settlement_lab.py
streamlit run src/dashboard/app.py
```

## Adding official data

Place files in `data/raw/`:

| Folder | Source |
|--------|--------|
| `bis_cpmi/` | BIS CPMI payment system statistics |
| `world_bank/` | Findex, RPW |
| `imf/` | FX rates, macro |
| `fred/` | SOFR, fed funds, stress indices |
| `ecb/` | TARGET/TIPS statistics |
| `swift/` | Currency share reports |
| `company_public_reports/` | Payment company filings |
| `manual/` | Labeled expert assumptions only |

## Replication

See [REPLICATION_SETTLEMENT_LAB.md](REPLICATION_SETTLEMENT_LAB.md).

## Disclaimers

- Research and education only
- Mock data cannot be used for conclusions
- Manual assumptions require sensitivity testing
- Incidence estimates require empirical validation

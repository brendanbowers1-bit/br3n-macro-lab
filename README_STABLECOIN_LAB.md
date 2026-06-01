# Bowers Frontier Stablecoin Settlement Window Lab

Research-grade measurement of stablecoin settlement windows, finality quality, liquidity transformation, digital run conditions, dollarization pressure, tokenized-money singleness, compliance drag, and value survival on remittance rails.

**Not financial advice. Not investment recommendation. Not operational guidance for live treasury or payment systems.**

## Core thesis

Stablecoins do not eliminate settlement risk; they change its location, speed, and legal form.

**Deeper thesis:** When money settles instantly, trust must settle somewhere else.

## Master research question

When settlement windows collapse toward zero, where does risk go?

## Flagship models

| Model | Description |
|-------|-------------|
| **SFQI** | Stablecoin Finality Quality Index — ledger vs economic finality |
| **SWC** | Settlement Window Compression — net benefit vs risk redistribution |
| **SLT** | Stablecoin Liquidity Transformation — user benefit vs issuer reserve burden |
| **DRV** | Digital Run Velocity — run-conditions composite (not run prediction) |
| **SDI** | Stablecoin Dollarization Index — retail digital dollar dependence |
| **TMS** | Tokenized Money Singleness — parity across tokenized dollars |
| **CSD** | Compliance Settlement Drag — compliance as the real settlement window |
| **SVSI** | Stablecoin Value Survival Index — usable value on remittance rails |

## Data governance

`NO_UNLABELED_DATA = True` — every output requires source, methodology, and quality metadata.

See [stablecoin_lab/DATA_SOURCES_STABLECOIN.md](stablecoin_lab/DATA_SOURCES_STABLECOIN.md) and [stablecoin_lab/STABLECOIN_RESEARCH_DISCIPLINE.md](stablecoin_lab/STABLECOIN_RESEARCH_DISCIPLINE.md).

## Setup

```bash
cd stablecoin_lab
source ../.venv/bin/activate
export PYTHONPATH=.
python scripts/fetch_stablecoin_data.py   # DeFiLlama, attestations, RPW, BIS/Fed refs
python scripts/smoke_test_stablecoin_lab.py
python scripts/reproduce_stablecoin_lab.py
streamlit run src/dashboard/app.py
```

From repo root: `make stablecoin-fetch` and `make stablecoin-reproduce`.

## Adding official data

Run the fetch script (network required) or place CSVs manually in `stablecoin_lab/data/raw/` (see [stablecoin_lab/DATA_SOURCES_STABLECOIN.md](stablecoin_lab/DATA_SOURCES_STABLECOIN.md)).

**Mixed mode:** supply, prices, reserves, redemption, remittance traditional leg, regulatory events, and research references load from official sources. Off-ramp tables still use Tier 4 manual assumptions until exchange data is added.

## Replication

See [stablecoin_lab/REPLICATION_STABLECOIN_LAB.md](stablecoin_lab/REPLICATION_STABLECOIN_LAB.md).

## Methodology

See [stablecoin_lab/METHODOLOGY_STABLECOIN_SETTLEMENT.md](stablecoin_lab/METHODOLOGY_STABLECOIN_SETTLEMENT.md).

## Disclaimers

- Research and education only
- Mixed mode: verify `mock_data_flag` per table before drawing conclusions
- Manual assumptions (off-ramp, partial stablecoin rail costs) require sensitivity testing
- DRV scores describe conditions — they do not predict runs
- Do not assume stablecoins are cheaper — measure value survival

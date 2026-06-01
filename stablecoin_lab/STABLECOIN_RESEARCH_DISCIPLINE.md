# Stablecoin Research Discipline

Rules for credible research outputs in the Stablecoin Settlement Window Lab.

## Purpose

This lab studies stablecoin settlement windows, finality, liquidity relocation, dollarization, and payment-infrastructure risk. It is **not** a trading bot, investment product, or operational treasury system.

## Permitted language

Use verbs and phrases such as:

- estimates
- suggests
- is associated with
- under this specification
- measurement framework
- descriptive association

## Forbidden claims

Never use mock data as evidence. Never claim:

- proves / proof
- guarantees
- predicts returns or run timing
- investment advice or buy/sell/hold recommendations
- operational guidance for live payment systems

## Data quality grades

| Score | Grade |
|-------|-------|
| 90–100 | Publication grade |
| 80–89 | Research grade |
| 70–79 | Strong preliminary |
| 60–69 | Exploratory |
| 40–59 | Demo/weak |
| below 40 | Do not use for inference |

**Mock data:** quality score ≤ 30, grade = "Demo only", `mock_data_flag = True`.

## Lineage requirement

No model output without:

- `source_id`
- `methodology_version`
- `mock_data_flag`
- `data_quality_score` / `data_quality_grade`
- `observed_vs_estimated_flag`

## Identification limits

- Indices are **associations**, not causal estimates, unless a separate identification strategy is documented.
- Bivariate Spearman tests in the dashboard are exploratory — controls in `hypotheses.py` are not fully implemented.
- DRV describes run **conditions** — not run probability or timing.
- SVSI compares rails under stated frictions — do not assume stablecoins are cheaper.

## Sensitivity and robustness

Every manual assumption (off-ramp time, compliance delay, redemption window, depeg penalty) must be run through conservative / baseline / severe cases before any external claim.

Robustness target: Spearman rank correlation ≥ 0.85 across specification variants.

## Working paper tone

Disciplined academic tone. Associations only. Limitations section mandatory. No causal language without identification.

## Review checklist before external use

1. Confirm `mock_data_flag` is false for all cited rows
2. Confirm credibility tier ≤ 3 for core variables (tier 1–2 preferred)
3. Run `reproduce_stablecoin_lab.py` end-to-end
4. Run `pytest tests/` and smoke test
5. Document assumptions in sensitivity output
6. Limit claims to what evidence supports

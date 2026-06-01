# Methodology (Draft)

Methodology version: `stablecoin-lab-credible-1.0`

See [METHODOLOGY_STABLECOIN_SETTLEMENT.md](../../../METHODOLOGY_STABLECOIN_SETTLEMENT.md) for full index specifications.

## Data pipeline

1. Load bronze/silver tables (or mock fallback)
2. Standardize dates, stablecoin names, networks
3. Build feature panel
4. Compute indices and models
5. Validate lineage and quality scores
6. Run sensitivity (conservative / baseline / severe)
7. Run robustness rank-stability checks

## Identification stance

All index outputs are **descriptive composites** under stated assumptions. Exploratory Spearman tests report associations only. Causal claims require exogenous variation or structural identification not provided by default.

## Sensitivity

Compliance delay, off-ramp time, redemption time, depeg penalty, chain fees, and reserve weights vary across three cases.

## Robustness

Rank stability (Spearman ρ) across: excluding manual rows, alternate SFQI weights, ledger vs economic finality rankings, stablecoin vs traditional VSI corridors.

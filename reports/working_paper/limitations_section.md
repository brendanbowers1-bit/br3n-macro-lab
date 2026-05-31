# Limitations Section (Draft)

## Measurement limits

The VSI is a **measurement framework**, not a causal welfare evaluation. Component formulas combine observed RPW costs with modeling assumptions for timing, volatility, payout, and—under the extended specification—trust and dollar dependency.

## Identification

Cross-corridor associations (e.g., higher RPW cost associated with lower VSI) do not establish causal effects on household welfare. Aggregate welfare loss figures multiply estimated flows by estimated loss rates; they are arithmetic summaries, not survey-based welfare measures.

## Data coverage

- Full RPW Excel may not be loaded; curated historical panel used instead.
- KNOMAD flows are estimated at the bilateral level.
- Payout friction relies on method defaults unless corridor-specific verification exists.
- Trust and dollar-drag components are research proxies, excluded from VSI_CORE.

## Not claimed

- Does not prove causal welfare effects
- Does not predict FX rates
- Does not provide investment or trading advice
- Does not replace household remittance surveys
- Does not assert that extended-specification components are directly observed

## Sensitivity and robustness

Results should be interpreted alongside sensitivity cases (conservative / baseline / severe) and robustness checks on rank stability. Corridors with low data quality scores (below 60) should be treated as exploratory only.

## Mock and demo data

When synthetic data is used, all outputs carry `mock_data_flag = True` and dashboard warnings. No research conclusions should be drawn from demo mode.

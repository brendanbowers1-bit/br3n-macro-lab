# Methodology — Stablecoin Settlement Economics

Methodology version: `stablecoin-lab-credible-1.0`

## Core framing

Stablecoins compress **ledger** settlement windows toward seconds, but **economic** finality still depends on redemption, compliance, off-ramp, and legal enforceability. Indices measure associations under stated assumptions — not causal welfare effects without identification.

## Stablecoin Finality Quality Index (SFQI)

Weighted composite (0–100) separating:

- **Ledger finality** — chain confirmation time, congestion
- **Economic finality** — redemption, off-ramp, compliance, legal enforceability, peg stability

Key output columns: `stablecoin_finality_quality_index`, `ledger_finality_score`, `economic_finality_score`, `effective_economic_finality_hours`.

## Settlement Window Compression (SWC)

Compares traditional settlement window hours to effective economic finality hours on stablecoin rails.

```
time_reduction = (traditional_hours − effective_hours) / traditional_hours
SWC_core = f(time_reduction, counterparty risk reduction, working capital benefit)
SWC_risk_adjusted = SWC_core − liquidity_pressure − operational_fragility
SWC_extended = SWC_risk_adjusted − run_speed − compliance_drag
```

Specifications: **SWC_core**, **SWC_risk_adjusted**, **SWC_extended**

## Stablecoin Liquidity Transformation (SLT)

Measures whether users gain liquidity convenience while issuers absorb reserve and redemption burden.

Components: `user_liquidity_benefit_score`, `issuer_reserve_burden_score`, `redemption_run_exposure_score`.

## Digital Run Velocity (DRV)

Risk-conditions composite — **not a run forecast**. Drivers include 24/7 transferability, thin exchange liquidity, redemption gates, information speed, composability.

## Stablecoin Dollarization Index (SDI)

Combines stablecoin usage proxies with macro pressure: inflation, FX volatility, banking access, capital controls, remittance dependence.

## Tokenized Money Singleness Index (TMS)

Weighted parity across price, redemption, reserve quality, legal claim, liquidity depth, CB-money convertibility, freeze risk.

## Compliance Settlement Drag (CSD)

```
compliance_drag_hours = compliance + off_ramp + redemption + legal_finality
effective_hours = ledger_hours + compliance_drag_hours
compliance_drag_index = 100 − f(drag_ratio, compliance_drag_hours)
```

## Stablecoin Value Survival Index (SVSI)

Extends Bowers Frontier value-survival logic to remittance corridors:

```
stablecoin_vsi = 100 × (1 − total_stablecoin_loss_pct)
traditional_vsi = 100 × (1 − total_traditional_loss_pct)
```

Loss components: on-ramp, spread, chain, bridge, off-ramp, local FX, compliance delay, depeg penalty, inflation erosion.

**Do not assume stablecoins are cheaper — measure it.**

## Sensitivity cases

`conservative`, `baseline`, `severe` — vary compliance delay, off-ramp time, redemption time, depeg penalty, chain fee multiplier, reserve liquidity weight.

## Robustness

Spearman rank stability ≥ 0.85 across specification variants (exclude manual rows, alternate weight sets, ledger vs economic finality).

## Language

Use: *estimates*, *suggests*, *is associated with*, *under this specification*.

Do not claim: *proves*, *guarantees*, *predicts returns*, *investment advice*.

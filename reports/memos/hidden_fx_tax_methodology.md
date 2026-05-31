# Hidden FX Tax Index — Methodology

## Definition
Measures the full burden of moving money across currencies beyond visible fees.

## Components
- fee_pct, fx_margin_pct, timing_risk_pct, volatility_penalty_pct
- inflation_erosion_pct, payout_friction_pct, transparency_penalty

## Formula
hidden_fx_tax_pct = sum(components)

## Limitations
- Mock volatility/inflation when real data missing
- Timing risk is modelled, not observed settlement delay
- Does not capture informal FX markets

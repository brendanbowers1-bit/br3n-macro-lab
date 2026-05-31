# Methodology Section (Draft)

## Value Survival Index

The Value Survival Index (VSI) is defined as:

**VSI = 100 × Real Usable Value Delivered / Original Value Sent**

where Real Usable Value Delivered is one minus the sum of specified value-loss components, capped at 50% total loss for numerical stability.

## Three specifications

| Specification | Components | Use case |
|---------------|------------|----------|
| **VSI_CORE** | Fee, FX spread, timing, inflation, payout | Empirically clean baseline |
| **VSI_RISK_ADJUSTED** | VSI_CORE + volatility exposure | Primary reported index |
| **VSI_EXTENDED** | VSI_RISK_ADJUSTED + dollar drag + trust discount | Extended specification only |

Dollar dependency and trust discount are **excluded** from the baseline index because they rely on model-based proxies rather than direct RPW observation.

## Component formulas (baseline)

1. **Explicit fee loss:** Observed `fee_pct` from RPW when available.

2. **FX spread loss:** Observed `fx_margin_pct` from RPW when available.

3. **Timing risk:**  
   `timing_loss_pct = transfer_speed_days × daily_fx_volatility × timing_risk_weight`  
   Weights: conservative 0.10, baseline 0.25, severe 0.50.

4. **Volatility exposure (risk-adjusted only):**  
   `volatility_loss_pct = 30d_fx_volatility × (1 - hedge_access_score) × volatility_weight`  
   Weights: conservative 0.05, baseline 0.10, severe 0.20.  
   Household hedge access defaults to 0.0.

5. **Inflation erosion:**  
   `inflation_erosion_pct = inflation_yoy × days_held / 365`

6. **Payout friction:** Observed when available; otherwise method defaults (bank 0.10%, mobile 0.20%, cash 0.50%, unknown 0.30%).

7. **Dollar dependency drag (extended only):**  
   `dollar_dependency_drag_pct = dollar_dependency_score / 100 × 0.75%`

8. **Trust discount (extended only):**  
   `trust_discount_pct = (100 - currency_trust_score) / 100 × 1%`

## Language conventions

Under `RESEARCH_MODE = "credible"`, outputs use: *estimates*, *suggests*, *is associated with*, *under this specification*. The term *proves* is reserved for designs with explicit causal identification.

## Methodology version

`vsi-credible-1.0`

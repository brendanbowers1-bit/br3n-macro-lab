# Methodology — Settlement Economics

Methodology version: `settlement-lab-credible-1.0`

## Settlement Drag Index (SDI)

```
Settlement Drag Cost =
  value_in_transit × settlement_lag_days × (cost_of_capital / 365)
  + FX exposure cost (risk-adjusted)
  + failure cost (risk-adjusted)
  + operational cost (extended)

SDI = 100 − min(100, drag_cost_per_100_usd)
```

Specifications: **SDI_CORE**, **SDI_RISK_ADJUSTED**, **SDI_EXTENDED**

## Operational Liquidity Burden (OLB)

```
Required liquidity = prefunding + collateral + settlement balance + buffer
Opportunity cost = required_liquidity × cost_of_capital
OLB ratio = required_liquidity / average_daily_settlement_value
```

## Finality Quality Index (FQI)

Weighted composite (0–100) of legal finality, funds availability, settlement speed, operational finality, reconciliation quality, low failure risk, low reversibility risk.

## Payment Network Fragility (PNF)

Composite 0–100 score decreasing with settlement lag, failure rates, low liquidity buffers, FX volatility, and operational incidents.

Regimes: normal · watchlist · stressed · fragile · crisis

## Payment Friction Incidence (PFI)

Model-based pass-through shares across consumer, merchant, bank, network, recipient. **Requires empirical validation.**

## Language

Use: *estimates*, *suggests*, *is associated with*, *under this specification*.  
Do not claim causality without identification.

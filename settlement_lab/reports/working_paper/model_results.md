# Model Results (Working Paper Draft — Stage 1)

**Disclaimer:** Stage 1 uses synthetic settlement tables with bridged IMF/FRED/RPW where available. Results are **descriptive estimates** under stated assumptions.

## Settlement Drag Index

Card and RTGS rails show lower settlement drag than remittance operators and ACH batch rails under baseline cost-of-capital assumptions. SDI ranges compress under conservative sensitivity (lower cost of capital, lower failure weights).

## Operational Liquidity Burden

Prefunding-heavy rails exhibit higher liquidity burden ratios. OLB cost per $100 settled is highest for remittance and mobile-money rails in demo data.

## Finality Quality Index

RTGS/wire rails score highest on legal and operational finality. Card rails show higher reversibility risk (chargeback windows).

## Payment Network Fragility

Several demo corridors register **crisis** or **fragile** regimes when settlement lag and failure rates combine with low liquidity buffer proxies.

## Payment Friction Incidence

Under baseline pass-through assumptions, merchants bear the largest modeled share; consumer share rises under severe pass-through sensitivity.

## Inference

Insufficient official CPMI settlement-level data for publication-grade causal inference. See sensitivity and robustness outputs in `data/outputs/`.

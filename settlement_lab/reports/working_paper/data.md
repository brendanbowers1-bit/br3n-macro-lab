# Data (Working Paper Draft)

## Sources (Tier 1 when loaded)

| Source | Use |
|--------|-----|
| BIS CPMI | Payment systems, settlement lag |
| BIS Triennial FX | Currency turnover, settlement hierarchy |
| World Bank Findex | Payment access |
| World Bank RPW | Cross-border fees, transfer speed |
| IMF FX | Volatility, settlement exposure |
| FRED | Cost of capital proxies |

## Parent lab bridge

When `settlement_lab/data/raw/` is empty, loaders read from `fx_regime_lab/data/raw/` (IMF FX cache, FRED DXY, RPW panel, BIS turnover).

## Stage 1 status

Mixed mode: bridged official FX/RPW where available; settlement liquidity and finality tables remain demo-labeled until CPMI files are added.

## Quality rubric

0–100 score; mock capped at 30; validation fails on missing metadata when `NO_UNLABELED_DATA=True`.

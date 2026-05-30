# USD/MXN Regime Research — One Page

**2026-05-30** · Research only · Not investment advice

## Question
Should hedge timing depend on market regime — specifically, should you **go flat when USD/MXN is range-bound**?

## Method (30 seconds)
1. Label each day: **trend vs range** × **high vs low vol** (4 regimes).
2. Strategy: trend-follow (MA20/60) in trending regimes; **flat in range**.
3. Test with a 6-level ladder: descriptive → OOS → 9 pairs → forecasts → costs → overfitting checks.

## Three findings

**1. Regimes matter.**  
Spot returns and strategy P&L differ by regime. Most `flat_range` P&L sits in **R2 (trend + low vol)** (~1.11 bps/day in sample).

**2. MXN passes OOS — mostly.**  
`flat_range` beat “always flat” on all three test windows (2019–21, 2022–24, 2025–26). The first window was weak (+0.4%).

**3. It’s not a crystal ball.**  
- No forecast accuracy vs random walk  
- Full frictions cut 20y return from ~20.36% to ~-6.47%  
- White Reality Check p = 0.6075 → **does not** confirm data-mined alpha

## Cross-pair
9 pairs tested. **56.1%** of OOS cells beat flat benchmark. Only **MXN + TRY** win all 3 splits.

## Hedging sentence you can use
> “We use regime labels to decide when **not** to adjust the hedge — not to predict the exchange rate.”

## Reproduce
```bash
cd ~/fx_regime_lab
python scripts/run_research_ladder.py --refresh
python scripts/build_publication.py
```

Full memo: `reports/publication/FX_REGIME_RESEARCH_NOTE.md`

# Carry, UIP, and Regime-Dependent FX Risk

## When Yield Creates Structure and When Yield Hides Crash Risk

BR3N Macro Labs — FX Lab publication memo (research draft).

**Carry is not treated as a magic predictor. It is treated as a regime-dependent risk and hedge-cost feature.**

---

## 1. What is carry?

Interest-rate carry is the return earned or paid from holding one currency versus another because of interest-rate differences.

For USD/MXN, if Mexico's policy rate exceeds the U.S. policy rate, a holder of MXN against USD may earn positive carry — but spot depreciation can overwhelm that yield.

## 2. Why carry matters in FX

Every FX position is long one currency and short another. Treasury and payments desks care about:

- spot regime (trend vs range, vol high vs low)
- policy-rate differential (carry proxy)
- forward points and roll (true hedge cost)
- crash and dollar-stress environments

## 3. The uncovered interest parity puzzle

Uncovered interest parity (UIP) predicts that higher-yield currencies should depreciate enough to offset yield advantages.

Empirically, UIP often appears to fail in calm periods and reassert itself violently in stress. FX Lab tests whether this is constant mispricing or **regime-dependent** behavior.

## 4. Carry as crash-risk compensation

A leading interpretation: carry returns may compensate investors for bearing global crash, liquidity, and dollar-funding risk — not free money.

FX Lab identifies **carry fragility**: high carry combined with rising volatility, news stress, or dollar stress.

## 5. Carry as hedge-cost input

Hedge governance must account for forward points and carry drag. A hedge that reduces spot volatility may still be expensive once forward costs are included.

FX Lab tests carry-adjusted hedge policies against static and regime-only baselines.

## 6. How FX Lab tests carry by regime

| Test | Question |
|------|----------|
| High vs low carry | Do return/vol profiles differ? |
| Carry by R1–R4 | Is carry behavior regime-dependent? |
| R2 stable vs fragile | Is quiet high-carry R2 cleaner? |
| R1 high-carry stress | Are drawdowns worse in stress? |
| Carry compression | Do narrowing spreads precede vol spikes? |

Models (research only):
- `carry_proxy_model`, `carry_regime_model`
- `r2_carry_confirmed_model`, `carry_fragility_risk_off_model`
- `carry_adjusted_hedge_model`

## 7. Early limitations

- Policy rates from FRED are **proxies**, not executable forward points
- No bid/ask, FX swap, or bank quote data in default pipeline
- Results are in-sample exploratory unless walk-forward validated
- USD/MXN focus; corridor expansion requires per-country rate data

## 8. Next data upgrades

1. Banxico official policy rate series (direct)
2. Forward points CSV or Bloomberg/LSEG feed
3. FX swap implied carry
4. Cross-corridor carry panels for remittance pairs
5. Out-of-sample carry-regime tests on holdout window

---

*Research only. Not investment advice. Not trading-ready.*

See also: `reports/CARRY_RESEARCH_FRAMEWORK.md`

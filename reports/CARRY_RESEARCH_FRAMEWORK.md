# Interest-Rate Carry Research Framework

Bowers Frontier Macro Labs — FX Lab carry and UIP research layer.

## Purpose

Interest-rate carry is the return earned or paid from holding one currency versus another because the two countries have different interest rates.

In FX, every position is long one currency and short another. A trader or hedger is exposed not only to spot price movement, but also to interest-rate differentials, forward points, roll costs, and carry.

## Plain-English Definition

If Mexico's interest rate is higher than the U.S. interest rate, holding MXN against USD may earn positive carry. But if MXN weakens enough, the exchange-rate loss can overwhelm the carry.

Carry is not free money. It can look stable for long periods and then crash during stress regimes.

## Why Carry Matters for FX Lab

FX Lab currently studies spot regimes:

- R1 = trend + high volatility
- R2 = trend + low volatility
- R3 = range + high volatility
- R4 = range + low volatility

Carry adds a second layer:

- Is the trend supported by yield?
- Is the currency being held for carry?
- Is carry becoming fragile?
- Is the forward hedge expensive?
- Does hedge protection justify the carry/forward cost?

## Big Research Questions

### 1. Why does the carry trade exist?

In theory, high-interest-rate currencies should depreciate enough to offset the yield advantage. In practice, carry trades have often earned positive returns until they crash.

**Question:** Why do high-interest-rate currencies often deliver excess returns instead of simply depreciating as theory predicts?

### 2. Why does uncovered interest parity fail?

Uncovered interest parity says the interest-rate advantage of one currency should be offset by expected depreciation.

**Question:** Is UIP wrong, incomplete, or regime-dependent?

**FX Lab hypothesis:** UIP may appear to fail in calm regimes and reassert itself violently during stress regimes.

### 3. Is carry compensation for crash risk?

Carry may be the premium investors earn for bearing global crash, liquidity, and dollar-funding risk.

**Question:** Is FX carry the return for selling insurance against bad global states?

### 4. Can carry predict hedge urgency?

For treasury and payments risk, the key question is not only whether carry predicts returns. It is whether forward/carry cost changes the value of hedging.

**Question:** When does the forward/carry cost justify changing a hedge ratio?

### 5. Does carry become dangerous when crowded?

Carry trades may become fragile when many investors hold the same high-yield currency trade in low-volatility conditions.

**Question:** Can carry fragility be identified before stress regimes unwind the trade?

## FX Lab Carry Thesis

Carry is not a static signal.

Carry may be useful only after conditioning on:

- volatility regime
- trend regime
- dollar stress
- news stress
- liquidity stress
- forward cost
- policy-rate differential
- payment-flow pressure

## Key Hypothesis

Carry is most useful in stable regimes and most dangerous when volatility, dollar stress, liquidity stress, or news stress rises.

More formal: Carry-adjusted regime classification may improve hedge-governance decisions relative to spot-only regimes and static hedge policies.

## Data tiers

| Tier | Source | Use |
|------|--------|-----|
| Academic | FRED policy rates (`FEDFUNDS`, Banxico proxies) | Policy-rate carry proxy |
| Trading | Forward points, FX swaps, bid/ask | True hedge economics |
| Proprietary | Internal hedge executions | Real carry drag |

Policy-rate differentials are **proxies only**. Forward points are required for realistic hedge economics.

## Important Disclaimer

This research does **not** claim that carry predicts FX with certainty. It tests whether carry helps classify regimes, hedge costs, and risk conditions.

Carry is treated as a **regime-dependent risk and hedge-cost feature**, not a magic trading signal.

## Lab modules

| File | Role |
|------|------|
| `src/carry_features.py` | Carry feature engineering |
| `src/forward_points.py` | Forward point placeholders |
| `src/carry_tests.py` | Regime/carry tests |
| `src/carry_models.py` | Carry-aware model zoo entries |
| `src/carry_hedge_governance.py` | Carry-adjusted hedge policies |
| `scripts/run_carry_layer.py` | Pipeline runner |

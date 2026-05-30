# Forecast Failure and Hedge Usefulness

## Regime-Based FX Hedge Governance Under Random-Walk Benchmarks

**BR3N Macro Labs — FX Lab**  
**Generated:** 2026-05-30

> Research and risk-framing only. Not investment advice. No live trading.

---

## 1. Executive Summary

BR3N Macro Labs does **not** currently find robust evidence that the tested FX models forecast exchange rates better than random walk. However, the evidence suggests a more useful research direction: **regime labels may improve hedge governance** by reducing unnecessary hedge turnover, avoiding over-adjustment in noisy regimes, and supporting more disciplined hedge-ratio decisions.

This memo separates **forecast accuracy**, **trading P&L**, and **hedge-governance usefulness**. A model may fail as a price forecast but still be useful for hedge discipline.

---

## 2. Core Question

**Can regime classification improve hedge decisions even when price forecasts fail to beat random walk?**

---

## 3. Why This Matters

A **trading model** asks: Can this signal generate risk-adjusted returns after costs?

A **forecasting model** asks: Can this reduce RMSE or MAE versus random walk?

A **hedge-governance model** asks: Can this reduce unwanted exposure, turnover, cost, and decision noise?

These are different questions. FX Lab tests them separately so results are not over-interpreted.

---

## 4. Current Evidence

### Forecast accuracy

- **13 of 14** model-zoo forecast tests **do not** beat random walk by RMSE on USD/MXN full sample.
- **0** models beat random walk by MAE.
- One model (`flow_pressure_model`) shows a **marginal** RMSE improvement (~0.000001) — not economically meaningful.
- **Conclusion:** Conditional forecastability is **not supported** on standard forecast-error tests.

### Trading / strategy

- **Best in-sample trading Sharpe (net):** `dollar_stress_model` ≈ **0.31** — research framing only; walk-forward Sharpe weakens to ≈ **0.23**.
- **`r2_only_model` (unscaled):** Sharpe net ≈ **−0.08**, max drawdown ≈ **−46.8%**.
- **`flat_range` / regime trend:** modest full-sample returns; OOS mixed across ladder splits.
- **After full economic frictions** (Level 5): strategy value often weakens or turns negative.
- **Conclusion:** Trading results are **mixed** and **not robust** as evidence of forecastability.

### Data-snooping control

- **White Reality Check** (USD/MXN): best strategy `r2_only`, p-value ≈ **0.61** → **does not reject** data-mining at 5%.
- **Conclusion:** Best-of-strategy Sharpe is **not yet** statistically defended against snooping.

### Hedge governance (US entity long MXN)

| Policy | Hedge turnover | Total hedge cost (%) | Vol reduction | Cost-adj risk reduction | Avg hedge ratio |
|--------|----------------|----------------------|---------------|-------------------------|-----------------|
| never_hedged | 0.0 | 0.00 | 0.0 | 0.0 | 0.0 |
| half_hedged | 0.5 | 0.01 | 5.70 | 5.69 | 0.50 |
| mostly_hedged | 0.75 | 0.02 | 8.54 | 8.53 | 0.75 |
| fully_hedged | 1.0 | 0.02 | 11.39 | 11.37 | 1.0 |
| **no_change_in_range** | **26.9** | **0.54** | **7.16** | **6.63** | **0.66** |
| regime_based | 98.4 | 1.97 | 7.22 | 5.25 | 0.60 |
| r2_active_policy | 118.9 | 2.38 | 5.27 | 2.90 | 0.55 |
| volatility_triggered | 83.2 | 1.66 | 6.65 | 4.99 | 0.52 |

**Key comparison:** `no_change_in_range` vs `regime_based`:
- Turnover: **26.9 vs 98.4** (~73% lower)
- Hedge cost: **0.54% vs 1.97%**
- Cost-adjusted risk reduction: **6.63 vs 5.25** (better on cost-adjusted basis)

**Conclusion:** Reactive regime hedging can **over-trade**. Freezing adjustments in range regimes (`no_change_in_range`) may improve **hedge discipline** without claiming FX prediction.

---

## 5. Hedge Governance Hypothesis

**Range-bound regimes (R3/R4):** Frequent hedge-ratio changes may create more transaction cost and decision noise than risk reduction. *Hypothesis: hold hedge ratio steady in range regimes.*

**Orderly trend regimes (R2):** Gradual hedge-ratio adjustment toward a target may be more useful than daily reactive changes.

**High-volatility trend regimes (R1):** The correct response may be **risk escalation**, tranching, or option-style protection rather than blind directional hedging or constant ratio churn.

---

## 6. Policies Tested

- `never_hedged`
- `half_hedged`
- `mostly_hedged`
- `fully_hedged`
- `regime_based`
- `r2_active_policy`
- `no_change_in_range`
- `volatility_triggered`

---

## 7. Metrics

Each policy is evaluated on:

- hedge turnover
- total hedge cost
- average hedge ratio
- unhedged volatility
- hedged volatility
- volatility reduction
- max drawdown unhedged
- max drawdown hedged
- cost-adjusted risk reduction
- regret proxy

Source: `data/outputs/hedge_governance_scorecard.csv`, `data/outputs/model_zoo_hedge_scorecard.csv`

---

## 8. Main Interpretation

The most promising use case for the current FX Lab is **not price prediction**. It is **hedge discipline**: identifying when to avoid unnecessary hedge changes, when to adjust gradually, and when market regimes justify escalation.

Regime labels appear **descriptively meaningful** (Level 1 supported). They may be more useful for **organizing risk and hedge governance** than for beating random walk on exchange-rate forecasts.

**Level 8 reminder:** The headline hedge result (`no_change_in_range` vs `regime_based` on USD/MXN) is **not** institutional proof. It is a disciplined hypothesis that must pass the nine-requirement bar before claim upgrade.

---

## 9. Limitations and Level 8 proof bar

Level 7 results are **prototype evidence only**. Before hedge-governance claims can be treated as institutionally valid, FX Lab requires **Level 8 — institutional proof** across:

| Requirement | Pass threshold | Current status |
|-------------|----------------|----------------|
| Many currency pairs | ≥ 10 pairs with hedge scorecards | **Not met** — hedge: 1 pair; trading ladder: ~19 pairs |
| Multiple decades | ≥ 20 years per pair | **Partial** — ~20–25y on USD/MXN only |
| Official data | Tier-1 spot for all pairs in results | **Partial** — FRED H.10 when available; fallback possible |
| Real / realistic forward costs | Forward points + roll in comparisons | **Not met** |
| Static vs dynamic hedge policies | Same exposure + cost model | **Partial** — USD/MXN, mostly full sample |
| Transaction costs | All metrics net of explicit costs | **Partial** — simplified bps on turnover |
| Out-of-sample tests | Walk-forward OOS for hedge policies | **Not met** — trading OOS only |
| Data-snooping controls | Pre-registered; White RC p < 0.05 | **Not met** — White RC p ≈ 0.61 |
| Multiple corporate exposure types | ≥ 3 types published | **Partial** — mostly `us_entity_long_mxn` |

**Upgrade gate:** Do **not** upgrade claims from prototype to institutional until **all nine** requirements are **Met** (not Partial).

Additional limitations:

- No accounting hedge-effectiveness testing (ASC 815 / IFRS 9)
- No proprietary payment-flow data
- No real corporate exposure schedule yet
- No bid/ask spread history yet

Full matrix: [Research Ladder — Level 8](ladder.html#level-8-institutional-proof-requirements)

---

## 10. Next Tests

**Priority — Level 8 (pre-registered):** Multi-pair walk-forward OOS hedge policy test — see [Pre-Registration Log](../research_log/PRE_REGISTRATION_LOG.md).

- Run hedge scorecards on **≥ 10 pairs** with Tier-1 spot only
- Walk-forward OOS for `no_change_in_range` vs `regime_based` vs static 50% / 75%
- Add **forward points** and roll to cost model
- Test **≥ 3 exposure types** per pair where data allows
- White Reality Check on the **pre-registered policy set**
- Rerun on **FRED / Fed H.10** consistently (no prototype fallback in published results)
- Test **one new corridor** — preferably US_PH or US_IN
- Evaluate **R2-only vol-scaled** trading model (pre-registered) — separate from hedge governance claims

---

## 11. Disclaimer

Research and risk-framing only. Not investment advice. No guaranteed returns. No live trading.

BR3N Macro Labs does not claim that the current model predicts FX or disproves random walk.

---

## Related artifacts

- [Research Ladder](ladder.html)
- [Model Zoo](model-zoo.html)
- [Pre-Registration Log](../research_log/PRE_REGISTRATION_LOG.md)
- Latest snapshot: `research_snapshots/` (dated folders)

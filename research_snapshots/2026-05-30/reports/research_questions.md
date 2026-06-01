# BR3N Macro Labs — High-Level Research Questions

> Research and risk-framing only. Not investment advice.

---

## 1. When does random walk fail in FX?

**Question:** Are exchange rates mostly random, but conditionally forecastable during specific market regimes?

**Testable version:** Do regime-conditioned models reduce forecast error versus a random-walk benchmark out of sample?

**Metrics:**
- RMSE model vs RMSE random walk
- MAE model vs MAE random walk
- Directional accuracy
- Diebold-Mariano test
- Walk-forward performance

---

## 2. What creates conditional forecastability?

**Question:** Is forecastability caused by trend, volatility compression, carry, dollar stress, liquidity stress, flow pressure, or their interaction?

**Testable version:** Compare model performance across regimes:
- trend + high volatility
- trend + low volatility
- range + high volatility
- range + low volatility
- carry-friendly regimes
- dollar-stress regimes

---

## 3. Can payment flows predict currency pressure?

**Question:** Do remittance, corporate, holiday, payroll, or settlement-flow proxies reveal FX pressure before public macro data?

**Testable version (public proxies first):**
- holidays
- month-end
- payroll timing
- remittance seasonality
- corridor-specific calendar events

**Later:** proprietary payment or order-flow data if available and legally usable.

---

## 4. Can regime-based hedging beat static hedge policy?

**Question:** Can firms reduce hedge error, turnover, and unnecessary hedge adjustments without claiming to predict FX?

**Testable version:** Compare:
- always 0% hedged
- always 50% hedged
- always 75% hedged
- always 100% hedged
- regime-based hedge ratio
- volatility-based hedge ratio

**Metrics:**
- hedge error
- hedge turnover
- estimated hedge cost
- drawdown of unhedged exposure
- regret versus perfect hedge
- cost-adjusted risk reduction

---

## 5. Is FX a balance-sheet-constrained market?

**Question:** Are spot, forwards, carry, and basis jointly influenced by global dollar liquidity and dealer balance-sheet capacity?

**Initial proxy variables:**
- DXY
- VIX
- MOVE index (if available)
- U.S. yield changes
- cross-currency basis (later)
- quarter-end dummy
- year-end dummy

---

## Core principle

We do not use AI to claim certainty. We use AI to organize evidence, classify regimes, test hypotheses, and improve risk decisions.

---

# Under-Tested Research Questions for BR3N Macro Labs

## 1. Regime-Based Hedge Governance

**Question:** Can regime labels reduce hedge turnover, over-hedging, and hedge regret versus static hedge-ratio policies, even when exchange-rate forecasts fail to beat random walk?

**Why it matters:** Many FX models are judged only by trading alpha or forecast accuracy. Treasury teams care about decision quality, cost, risk reduction, hedge timing, and avoiding unnecessary hedge changes.

**Testable version:** Compare regime-based hedge policies against:
- always 0% hedged
- always 50% hedged
- always 75% hedged
- always 100% hedged
- monthly calendar-based hedge adjustment
- volatility-triggered hedge policy
- no-change-in-range policy

**Metrics:**
- hedge turnover
- hedge cost
- hedge error
- unhedged exposure volatility
- hedged exposure volatility
- volatility reduction
- max adverse exposure
- regret versus perfect hedge
- cost-adjusted risk reduction

**Core hypothesis:** Regime-based hedge governance may improve risk discipline even when the same regime model does not beat random walk as a pure FX forecast.

---

## 2. When Not to Hedge

**Question:** When should a treasury team intentionally avoid changing the hedge ratio?

**Why it matters:** Over-adjusting a hedge book in range-bound markets can create transaction costs, false precision, and unnecessary churn.

**Testable version:** Create a no-change-in-range policy:
- If regime is R3_range_high_vol or R4_range_low_vol, freeze the hedge ratio.
- If regime is R2_trend_low_vol, gradually adjust hedge ratio.
- If regime is R1_trend_high_vol, use cautious tranches or option-style logic rather than full forward reload.

**Metrics:**
- number of hedge changes
- hedge turnover
- hedge cost
- volatility reduction
- regret
- drawdown of unhedged exposure
- cost-adjusted risk reduction

**Core hypothesis:** In range-bound regimes, dynamic hedge adjustment may create more cost than risk reduction.

---

## 3. Payment-Corridor Flow Proxies

**Question:** Can public payment-flow proxies approximate private order-flow pressure in remittance-heavy FX corridors?

**Why it matters:** True order-flow data is usually private. But remittance-heavy corridors may have predictable flow windows around payroll, holidays, tax refunds, school fees, and migration/diaspora calendars.

**Initial corridors:** USD/MXN, USD/PHP, USD/INR, USD/COP, USD/BRL, USD/GTQ (if data available)

**Public proxy variables:**
- U.S. payday cycles
- month-end, quarter-end, year-end
- tax refund season
- Christmas, Mother's Day, Semana Santa
- local holidays, school-fee months
- central-bank meeting weeks
- major diaspora/cultural events
- remittance seasonality from public data if available

**Testable version:** Test whether corridor-specific calendar windows show abnormal returns, volatility, trend persistence, regime transitions, hedge cost proxy, or drawdown risk.

**Core hypothesis:** Some remittance-heavy FX corridors may show short-term pressure around predictable payment-flow windows, even if the effect is weak or inconsistent.

---

## 4. Hedge Demand Feedback Loops

**Question:** Does hedging demand amplify FX moves?

**Mechanism:**
1. Currency begins moving.
2. Corporates increase hedging.
3. Banks hedge the corporate hedge.
4. Dealer flows pressure forwards, spot, or liquidity.
5. Volatility rises.
6. More hedge triggers activate.

**Initial public proxies:** quarter-end dummy, year-end dummy, realized volatility, forward points (later), options skew (later), central-bank reserves (later), corporate FX disclosures (later).

**Testable version:** Do quarter-end or year-end hedging windows show abnormal FX volatility, trend persistence, or regime transition behavior after controlling for baseline volatility?

**Core hypothesis:** Hedging demand may be endogenous: hedge activity responds to FX moves and can amplify market pressure.

---

## 5. Forecast Failure vs Hedge Usefulness

**Question:** Can a model fail the forecast-accuracy test but still pass the hedge-governance test?

**Why it matters:** Forecast accuracy, trading alpha, and hedge usefulness are different objects. Treasury teams may benefit from models that improve risk discipline even when price forecasts remain weak.

**Testable version:** For each model, produce three independent scorecards:
1. **Forecast scorecard** — RMSE/MAE vs random walk, directional accuracy, Diebold-Mariano p-value
2. **Trading scorecard** — return, Sharpe, drawdown, turnover, costs, White Reality Check p-value
3. **Hedge-governance scorecard** — volatility reduction, hedge turnover, hedge cost, regret proxy, cost-adjusted risk reduction

**Core hypothesis:** A model may be rejected as a trading or forecasting model but still accepted as a hedge-governance tool.

---

## 6. Random-Walk Validity Map

**Question:** When is random walk a good assumption, and when is it dangerous?

**Testable version:** Create a regime-specific validity map:

- **R1_trend_high_vol:** Random-walk assumption may be unstable. Use caution, tranches, options, and stress framing.
- **R2_trend_low_vol:** Random-walk assumption may be weaker. Gradual hedge adjustment may be more useful.
- **R3_range_high_vol:** Random-walk may still describe direction poorly, but risk is high. Avoid over-adjustment.
- **R4_range_low_vol:** Random-walk assumption may be strongest. Maintain base hedge and avoid noise trading.

**Core hypothesis:** Random walk is not simply right or wrong. Its usefulness depends on the market regime and the decision being made.

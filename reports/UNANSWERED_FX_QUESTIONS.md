# Major Unanswered Questions in FX

## Core Theme

FX markets remain one of the hardest areas in finance and macroeconomics because exchange rates are difficult to forecast, random-walk benchmarks are hard to beat, and yet currencies sometimes appear structured under certain regimes.

BR3N Macro Labs studies this tension.

The lab does not assume that FX is predictable. It asks:

When do currency markets become less random?

And more importantly:

Can FX decisions improve even when FX forecasts fail?

---

## 1. Why Do Exchange Rates Disconnect from Fundamentals?

Macro fundamentals such as inflation, interest rates, productivity, trade balances, fiscal policy, and money supply should matter. Yet exchange rates often move in ways that appear disconnected from fundamentals, especially at short and medium horizons.

### Unanswered Question

When do fundamentals matter, and when are they overwhelmed by flows, positioning, liquidity, and risk appetite?

### FX Lab Test

Test whether fundamentals matter more in:

- R2 trend + low volatility regimes
- low-news-stress regimes
- low-dollar-stress regimes
- stable carry regimes

and matter less in:

- R1 high-volatility stress regimes
- R3/R4 range regimes
- high-news-stress environments
- high-liquidity-stress environments

### Data Needed

- FX spot
- interest rates
- inflation
- policy rates
- trade/current account proxies
- VIX / dollar stress
- news uncertainty
- regime labels

---

## 2. Why Does Uncovered Interest Parity Fail?

Uncovered interest parity says that high-interest-rate currencies should depreciate enough to offset the yield advantage. Empirically, this often fails.

### Unanswered Question

Is uncovered interest parity wrong, incomplete, or regime-dependent?

### FX Lab Hypothesis

UIP may appear to fail in calm regimes and reassert itself violently during stress regimes.

### FX Lab Test

Test whether carry works in:

- R2 trend + low volatility
- low-news-stress environments
- low-dollar-stress environments
- stable carry regimes

and fails or reverses in:

- R1 high-volatility trend regimes
- carry fragility regimes
- high VIX / dollar stress
- news stress spikes

### Data Needed

- policy rate differentials
- forward points
- FX swaps
- spot returns
- VIX / dollar stress
- news stress
- regime labels

---

## 3. Is FX Carry a Risk Premium, Behavioral Anomaly, or Liquidity Premium?

Carry trades may earn returns because investors are compensated for crash risk, liquidity risk, balance-sheet constraints, or because markets are inefficient.

### Unanswered Question

Are carry returns payment for bearing rare disaster risk, or evidence of market inefficiency?

### FX Lab Test

Build a Carry Fragility Index using:

- high carry
- low realized volatility
- strong trend
- rising news stress
- rising dollar stress
- rising volatility
- deteriorating liquidity proxy

Then test whether carry fragility predicts:

- worse drawdowns
- regime transitions
- volatility spikes
- carry trade reversal
- hedge escalation needs

### Data Needed

- policy rates
- forward points
- volatility
- dollar stress
- news stress
- liquidity/spread proxies
- regime labels

---

## 4. When Does Random Walk Fail?

Random walk remains a hard benchmark to beat in FX forecasting. But the unresolved question is whether random walk is universal or regime-specific.

### Unanswered Question

Is random walk a universal model of FX, or a regime-specific model?

### FX Lab Test

Build a Random-Walk Validity Map.

Regime labels:

- R1 trend + high volatility
- R2 trend + low volatility
- R3 range + high volatility
- R4 range + low volatility

Evaluate each regime using:

- RMSE vs random walk
- MAE vs random walk
- directional accuracy
- autocorrelation
- trend persistence
- volatility
- return asymmetry
- Diebold-Mariano test where appropriate

### Expected Interpretation

- R4 may be most random-walk-like.
- R2 may show potential structure.
- R1 may be high-risk stress structure or unstable liquidation.
- R3 may be high-risk noise.

---

## 5. Can Order Flow Bridge Macro and FX?

Order flow may be one of the missing links between macro fundamentals and exchange-rate movement. However, true order-flow data is usually private.

### Unanswered Question

Can public proxies approximate private flow pressure well enough to improve FX risk decisions?

### FX Lab Test

Use public payment-flow proxies:

- paydays
- month-end
- holidays
- tax refund season
- school-fee season
- remittance seasonality
- central-bank meeting weeks

Then test whether these proxy windows are associated with:

- higher volatility
- different regime distributions
- higher hedge turnover
- drawdown risk
- regime transitions

### Data Needed

- FX spot
- corridor calendar proxies
- remittance data
- central-bank calendars
- holidays
- ideally proprietary payment-flow data later

---

## 6. Do Payment and Remittance Flows Create Predictable FX Pressure?

Traditional FX research often focuses on macro, carry, asset pricing, or institutional order flow. Payment-corridor FX risk is less commonly framed as a public research system.

### Unanswered Question

Do millions of small cross-border payments create measurable short-term currency pressure in remittance-heavy corridors?

### FX Lab Test

Test corridors:

- US_MX / USD/MXN
- US_IN / USD/INR
- US_PH / USD/PHP
- US_CO / USD/COP
- US_BR / USD/BRL
- US_GT / USD/GTQ if data quality allows

Measure whether flow windows show:

- higher volatility
- different regime frequency
- abnormal returns
- hedge-governance stress
- increased no-change-in-range usefulness

### Data Needed

- FX spot
- official remittance data
- public calendar proxies
- central bank remittance data
- professional FX data later
- legally usable proprietary payment-flow data later

---

## 7. Can a Model Fail as a Forecast but Still Be Useful for Hedging?

Academia often evaluates FX models through forecast accuracy or trading returns. But corporate treasury decisions care about exposure volatility, hedge turnover, hedge cost, policy discipline, and risk governance.

### Unanswered Question

Is forecast accuracy the wrong success metric for some FX decision systems?

### FX Lab Thesis

A regime model may fail to beat random walk on RMSE or MAE but still reduce:

- hedge turnover
- over-adjustment
- cost-adjusted exposure volatility
- decision noise
- hedge regret
- unnecessary policy changes

### FX Lab Test

Compare:

- static 50% hedge
- static 75% hedge
- fully hedged
- regime_based
- r2_active_policy
- no_change_in_range
- volatility_triggered
- carry_adjusted_regime
- no_change_in_range_carry_aware

Metrics:

- hedge turnover
- hedge cost
- volatility reduction
- max drawdown hedged
- cost-adjusted risk reduction
- regret proxy

This is the current flagship research lane.

---

## 8. Why Do No-Arbitrage Relationships Break in FX?

Covered interest parity and forward pricing should be close to no-arbitrage relationships, but deviations can persist when funding markets, dealer balance sheets, collateral, or regulation matter.

### Unanswered Question

Is FX pricing partly determined by balance-sheet scarcity rather than pure no-arbitrage?

### FX Lab Test

Later, add:

- cross-currency basis
- forward points
- dollar funding stress
- quarter-end/year-end balance-sheet dates
- dealer balance-sheet proxies
- funding stress proxies

Then test:

- Are forward/carry anomalies larger during balance-sheet stress windows?
- Do quarter-end/year-end dates affect carry, spreads, and forward costs?
- Does hedge cost rise during balance-sheet stress regimes?

### Data Needed

- forward points
- cross-currency basis
- FX swaps
- bid/ask spreads
- funding stress proxies
- professional data source

---

## 9. When Does Central-Bank Intervention Work?

Central-bank intervention sometimes changes market behavior and sometimes fails.

### Unanswered Question

Does FX intervention work by changing supply, signaling policy, breaking momentum, or coordinating expectations?

### FX Lab Test

For EM pairs, collect:

- central-bank intervention dates
- reserve changes
- policy meeting dates
- rate decisions
- surprise moves
- pre/post intervention regimes

Then test:

- Does intervention work better in R1 stress?
- Does it break R2 trend?
- Does it reduce R3 high-volatility noise?
- Does volatility fall after intervention?
- Does random-walk validity change?

### Data Needed

- central bank intervention data
- reserves
- policy dates
- FX spot
- volatility
- regime labels

---

## 10. Are High-Volatility Trends Information or Forced Liquidation?

Not all trends are the same. R2 trend + low volatility may represent orderly information diffusion. R1 trend + high volatility may represent stress, liquidation, panic, crowded exits, or liquidity breakdown.

### Unanswered Question

Are high-volatility FX trends less forecastable because they reflect forced liquidation rather than information?

### FX Lab Test

Compare R1 vs R2 using:

- continuation probability
- drawdown profile
- news stress
- carry fragility
- VIX/dollar stress
- spread proxy
- flow window proxy
- trend persistence
- reversal probability

### Interpretation

R2 may be the cleaner trend regime.
R1 may be danger rather than opportunity.

This directly connects to early FX Lab findings.

---

## 11. What Is the Right Objective Function for Corporate FX Hedging?

Investors may care about return and Sharpe. Corporate treasury cares about cash-flow volatility, margins, liquidity, policy compliance, and avoiding speculation.

### Unanswered Question

What is the optimal hedge policy when prediction is weak, hedge costs are real, and over-adjustment is costly?

### FX Lab Test

Compare:

- static hedge policies
- calendar hedging
- regime hedging
- no-change-in-range
- carry-adjusted hedging
- stress-escalation hedging
- option/collar logic later

Metrics:

- exposure volatility
- hedge turnover
- hedge cost
- regret
- policy stability
- drawdown
- cost-adjusted protection

---

## 12. Can AI Improve FX Decisions Without Improving FX Forecasts?

AI may not beat random walk directly. But it may improve classification, explanation, monitoring, memo generation, anomaly detection, policy discipline, and decision architecture.

### Unanswered Question

Does AI create value in FX by improving decision architecture rather than prediction accuracy?

### FX Lab Test

Compare:

- raw model signals
- regime dashboard
- AI-generated hedge-governance memo
- policy checklist
- decision scorecard

Measure whether the AI layer improves:

- explanation quality
- consistency
- reduced over-adjustment
- clearer escalation
- better separation of hedging vs speculation

---

# Priority Questions for BR3N Macro Labs

The five best research lanes are:

## 1. Forecast Failure and Hedge Usefulness

Can FX regime models fail to beat random walk as forecasts but still improve hedge governance?

## 2. Regime-Dependent UIP

Does uncovered interest parity fail in calm regimes and reassert itself in stress regimes?

## 3. Carry Fragility

When does carry shift from stable yield to hidden crash risk?

## 4. Public Flow Proxies

Can public calendar/remittance proxies identify FX pressure windows in major payment corridors?

## 5. R1 vs R2 Trend Quality

Are low-volatility trends information-rich while high-volatility trends are liquidation/stress regimes?

---

# Highest-Level Thesis

FX markets may be mostly random-walk-like as price processes, but not all FX decisions are price forecasts.

Regime, carry, news, flow, and stress variables may fail to predict exchange rates directly while still improving hedge governance, risk escalation, and decision discipline.

The question is not only whether FX can be predicted.

The question is whether FX decisions can be improved when prediction fails.

# BR3N Macro Labs — FX Lab One-Pager

**Generated:** 2026-05-30  
**Flagship pair:** USD/MXN · **Latest regime:** R2_trend_low_vol

> Research and risk-framing only. Not investment advice. No live trading.

---

## 1. Research Question

**When do currency markets become less random?**

FX Lab tests whether exchange rates are mostly random-walk-like but **conditionally structured** when trend, volatility, carry, liquidity stress, and payment-flow pressure align.

---

## 2. Core Thesis

FX may be mostly random-walk-like unconditionally, but **conditionally forecastable** in specific regimes (R1–R4).

We do not claim universal predictability. We test conditional forecastability against honest benchmarks.

---

## 3. Three Scorecards

| Object | Question | Latest anchor |
|--------|----------|---------------|
| **Forecast scorecard** | Does the model beat random walk (RMSE, MAE, DM tests)? | — |
| **Trading scorecard** | Does the strategy survive costs, drawdowns, walk-forward? | Best Sharpe: `buy_and_hold` (0.273) |
| **Hedge-governance scorecard** | Does regime logic improve cost-adjusted risk vs static hedges? | Best policy: `fully_hedged` |

A model may fail forecast tests and still improve hedge discipline.

---

## 4. Flagship Use Case

**USD/MXN** regime and hedge-governance research.

- Regimes: R1 trend+high vol · R2 trend+low vol · R3 range+high vol · R4 range+low vol
- Separation of trading alpha vs treasury hedge effectiveness
- Desk memos and FX Desk Command Center for decision framing

---

## 5. Corridor Roadmap

Expansion to major payment/remittance corridors (25 in master scorecard):

- US_MX / USD/MXN
- US_IN / USD/INR
- US_PH / USD/PHP
- US_CO / USD/COP
- US_BR / USD/BRL

Corridor results are exploratory until rerun on official data tiers.

---

## 6. Academic Discipline

- Random-walk benchmark on every claim
- Out-of-sample and walk-forward testing
- Transaction costs on turnover
- Data-snooping awareness (White reality check where applicable)
- No holdout tuning for production claims

---

## 7. Data Standard

| Tier | Label | Current use |
|------|-------|-------------|
| 4 | Prototype | yfinance / Stooq (development) |
| 1 | Academic-grade | FRED, Fed H.10, BIS, central banks (publication target) |
| 2 | Trading-grade | Bloomberg, LSEG, bank quotes (execution research) |

**Current primary spot tier:** Prototype data · **Quality flag:** OK

Prototype results must be rerun on Tier 1 before publication-grade claims.

---

## 8. Disclaimer

This is research and risk-framing only. It is not investment advice, does not guarantee returns, and is not intended for automated live trading.

BR3N Macro Labs is an independent research project — not affiliated with any employer, bank, or payment company unless explicitly stated.

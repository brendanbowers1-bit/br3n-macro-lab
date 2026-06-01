# Working Paper Outline

## Conditional Forecastability in USD/MXN: A Regime-Based Research Framework

**Authors:** Brendan Bowers (Bowers Frontier Macro Labs)  
**Status:** Working paper outline — not peer-reviewed  
**Data tier:** Document source tier at submission (FRED H.10 / BIS / prototype)

---

## Abstract (draft)

We study whether USD/MXN exchange rate dynamics depart from a random-walk benchmark **conditionally** across volatility–trend regimes. Using daily spot data with explicit data-quality tiering, we classify markets into four regimes, test forecasting and hedge-governance policies net of transaction costs, and evaluate statistical significance with Diebold–Mariano and walk-forward protocols. We find that forecastability and hedge value are **regime-dependent** and should not be conflated with unconditional predictability.

---

## 1. Introduction

- Motivation: FX as mostly random, but potentially structured in specific states
- Contribution: Separates trading alpha, hedge governance, and data-quality discipline
- Scope: USD/MXN flagship; multi-corridor extension as robustness appendix

## 2. Literature Review

- Random walk and FX predictability (Meese–Rogoff; recent ML revisit)
- Regime-switching and volatility state models
- Transaction costs and forecast evaluation (DM tests, White reality check)
- Treasury hedge policy vs speculative FX trading

## 3. Data and Data-Quality Layer

- Tier stack: FRED H.10 (Tier 1), BIS EER (Tier 1 macro), yfinance (Tier 4 prototype)
- Quality manifest: missing data, suspicious returns, source metadata
- Macro panel: US–MX rate spread, VIX, broad dollar index

## 4. Regime Classification

- Features: moving averages, realized vol percentile, returns
- Regimes R1–R4: trend/range × high/low vol
- Stability and interpretability for desk users

## 5. Empirical Methods

- Benchmarks: buy-and-hold, random walk (flat), legacy MA crossover
- Primary strategy: flat in high-vol range regimes (`flat_range`)
- Walk-forward: 5y train / 1y test
- Academic tests: DM, SPA/White RC where sample allows

## 6. Results

- Strategy scorecard (full sample and OOS)
- Random-walk validity map by regime
- Hedge governance: turnover vs risk reduction tradeoff
- Flow-pressure proxy tests (calendar seasonality)

## 7. Discussion

- When regime logic helps hedging even if forecasts fail
- Data tier implications for publication
- Corridor heterogeneity (US_MX vs US_CO vs US_IN)

## 8. Limitations

- No forward points, carry implementation, or executable spreads
- Calendar flow proxies ≠ proprietary payment flows
- Single-pair depth vs multi-corridor breadth tradeoff

## 9. Conclusion

- Conditional forecastability framing vs oracle claims
- Policy implications for treasury and cross-border payments desks

## Appendix A — Multi-Corridor Roadmap Tables  
## Appendix B — Model Cards and Reproducibility  
## Appendix C — Data Source Registry  

---

## Target Venues (aspirational)

- Central bank / FX workshop
- Financial econometrics seminar
- Industry treasury research forum (non-commercial)

---

## Replication Package

- Repository: Bowers Frontier Macro Labs FX Lab
- Scripts: `run_usdmxn_backtest.py`, `run_under_tested_research.py`, `run_data_quality_layer.py`
- Config: `config.yaml` with tier flags documented

---

*Outline only — fill empirical tables from latest pipeline run before circulation.*

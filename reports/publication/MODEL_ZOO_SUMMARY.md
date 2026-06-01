# FX Lab Model Zoo

Bowers Frontier Macro Labs tests multiple model families rather than relying on one rule.

## Model families

- random walk benchmarks
- trend models
- regime-conditioned models
- range mean-reversion models
- carry proxy models
- dollar-stress models
- payment-flow proxy models
- ensemble models
- hedge-governance models

## Core principle

A model can be useful in one context and rejected in another. **Forecast accuracy**, **trading P&L**, and **hedge-governance usefulness** are separate tests.

The model zoo is designed to prevent overreliance on a single rule. The objective is not to find one perfect FX predictor, but to test whether different model families provide value under different regimes and decision contexts.

This work tests **conditional forecastability** against random-walk benchmarks. It does **not** claim that FX is predictable, that random walk is disproved, or that any strategy is live-trading ready.

> Research and education only. Not investment advice. No guaranteed returns. No live trading.

## Commands

```bash
python scripts/run_model_zoo.py
python scripts/generate_model_zoo_report.py
```

See also: `reports/model_zoo_report.md` after running the pipeline.

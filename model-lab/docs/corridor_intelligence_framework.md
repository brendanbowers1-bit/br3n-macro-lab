# USD/MXN Corridor Intelligence Framework

**Product:** USD/MXN Corridor Intelligence System  
**Lab:** Bowers Frontier Macro Labs

## Purpose

Produce a **transparent corridor risk score** and **daily intelligence brief** from validated remittance-flow data. This is treasury decision-support research — not a trading or FX prediction system.

## Pipeline

```
data/raw/corridor/us_mx_banxico_remittances.csv
    ↓ validate (src/corridor_intelligence/validate.py)
    ↓ score (src/corridor_intelligence/risk_score.py)
    ↓ brief (src/corridor_intelligence/brief.py)
    ↓ data/outputs/us_mx_corridor_daily.json
    ↓ data_lake/gold_research/us_mx_corridor/
    ↓ us-mexico-corridor.html (site build)
```

## Corridor Risk Score (CRS)

Scale: **0–100** (higher = elevated structural corridor stress)

| Component | Weight | Meaning |
|-----------|--------|---------|
| Momentum stress | 30% | Weakness in YoY flow growth |
| Volatility stress | 25% | Elevated month-over-month flow volatility |
| Drawdown stress | 25% | Distance from recent peak flow |
| Data quality gap | 20% | Penalty for validation warnings / starter data |

**Bands:** Low (&lt;33), Moderate (33–66), Elevated (&gt;66)

## Brief format

Title: **Bowers Frontier Macro Labs — Corridor Intelligence Brief**

Sections: executive summary, data lineage, risk score breakdown, flow context, validation notes, limitations.

## Commands

```bash
python scripts/run_corridor_intelligence.py
npm run model:brief
npm run model:smoke
```

## Limitations

- Starter Banxico-aligned research series until live official feed is integrated.
- CRS reflects remittance-flow structure only — not MXN spot, policy shocks, or settlement outages.
- Research only. Not investment advice.

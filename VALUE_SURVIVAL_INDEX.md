# BR3N Value Survival Index (VSI)

## Core Definition

The **Value Survival Index** measures the share of original economic value that survives cross-border translation into usable purchasing power.

**Formula:**

```
VSI = 100 × Real Usable Value Delivered / Original Value Sent
```

**Research mode:** `RESEARCH_MODE = "credible"` (see `src/config/research_settings.py`)

## Three Specifications (critical for credibility)

| Index | Components | Role |
|-------|------------|------|
| **VSI_CORE** | Fee, FX spread, timing, inflation, payout | Empirically clean baseline |
| **VSI_RISK_ADJUSTED** | VSI_CORE + volatility exposure | **Primary reported index** |
| **VSI_EXTENDED** | VSI_RISK_ADJUSTED + dollar drag + trust discount | Extended specification only |

Dollar dependency and trust discount are **not** included in the baseline index.

## Component Formulas

### 1. Explicit fee loss
Observed from RPW when available: `fee_pct`

### 2. FX spread loss
Observed from RPW when available: `fx_margin_pct`

### 3. Timing risk
```
timing_loss_pct = transfer_speed_days × daily_fx_volatility × timing_risk_weight
```
Weights: conservative 0.10 · baseline 0.25 · severe 0.50

### 4. Volatility exposure (VSI_RISK_ADJUSTED only)
```
volatility_loss_pct = 30d_fx_volatility × (1 - hedge_access_score) × volatility_weight
```
Weights: conservative 0.05 · baseline 0.10 · severe 0.20

### 5. Inflation erosion
```
inflation_erosion_pct = inflation_yoy × days_held / 365
```

### 6. Payout friction
Observed when available; otherwise defaults by payout type:
- Bank account: 0.10%
- Mobile wallet: 0.20%
- Cash pickup: 0.50%
- Unknown: 0.30%

### 7. Dollar dependency drag (VSI_EXTENDED only)
Extended specification — `dollar_dependency_score / 100 × 0.75%`

### 8. Trust discount (VSI_EXTENDED only)
Extended specification — `(100 - currency_trust_score) / 100 × 1%`

## Interpretation (estimated)

| VSI Score | Classification |
|-----------|----------------|
| 95–100 | High value survival (estimated) |
| 90–95 | Moderate value leakage (estimated) |
| 80–90 | High value leakage (estimated) |
| below 80 | Severe value destruction (estimated) |

## What this does NOT claim

- Does not **prove** causal welfare effects
- Does not predict FX rates or provide investment advice
- Does not present extended-spec components as directly observed

See [LITERATURE_MAP.md](LITERATURE_MAP.md) and [REPLICATION.md](REPLICATION.md).

## Run

```bash
python scripts/reproduce_all.py
python scripts/smoke_test.py
streamlit run src/dashboard/app.py
```

## Data

Place real files in `data/raw/` — see [DATA_SOURCES.md](DATA_SOURCES.md).

Mock data is clearly labelled. Do not use mock outputs for research conclusions.

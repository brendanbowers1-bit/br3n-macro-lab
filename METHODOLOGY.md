# BR3N Value Survival Index — Methodology

## Mission

**When value crosses a border, how much of it survives?**

Foreign exchange is the daily auction of global trust. The Value Survival Index (VSI) measures how much economic value survives that auction.

## Master Formula

```
VSI = 100 × Real Usable Value Delivered / Original Value Sent
```

Where:

```
Real Usable Value Delivered = Original Value × (1 - Total Value Loss)
```

## Component Formulas (Stage 1 — transparent placeholders)

### Explicit fee loss
```
explicit_fee_loss_pct = fee_pct
```

### FX spread loss
```
fx_spread_loss_pct = fx_margin_pct
```

### Timing loss
```
timing_loss_pct = transfer_speed_days × fx_daily_volatility × 0.25
```
Conservative placeholder for FX exposure during transfer delay.

### Volatility loss
```
volatility_loss_pct = volatility_30d × (1 - hedge_access_score) × 0.10
```
Households typically cannot hedge (`hedge_access_score ≈ 0`).

### Inflation erosion
```
inflation_erosion_pct = inflation_yoy × days_held / 365
```

### Payout friction
| Method | Default |
|--------|---------|
| Bank account | 0.10% |
| Mobile wallet | 0.20% |
| Cash pickup | 0.50% |
| Unknown | 0.30% |

### Dollar dependency drag
```
drag_pct = dollar_dependency_score / 100 × 0.75%
```

### Trust discount
```
trust_discount_pct = (100 - currency_trust_score) / 100 × 1.00%
```

## Sub-Indices

### Hidden FX Tax (VSI sub-index)
```
fee + FX margin + timing + volatility + payout friction
```
Excludes inflation, trust, and dollar drag.

### Currency Trust Score
Weighted composite: inflation stability (25%), FX stability (20%), reserves (15%), current account (15%), external debt (10%), institutional placeholder (10%), crisis placeholder (5%).

### Dollar Dependency Score
Composite of USD debt share, invoicing, pair share, remittance/import dependence, stablecoin and sanctions placeholders.

## Data Quality

- **Real data:** World Bank RPW, KNOMAD, IMF FX, WB API macro, BIS turnover, manual sovereignty
- **Mock data:** Synthetic corridors with `source=mock_synthetic` and `mock_data_flag=True`

## Limitations

1. Starter formulas require validation against corridor microdata
2. Institutional and crisis components use research placeholders
3. Not causal — panel regressions require instruments
4. Not investment advice or a trading signal

## Code

- Index: `src/indices/value_survival.py`
- Pipeline: `scripts/run_vsi.py`
- Dashboard: `src/dashboard/app.py`

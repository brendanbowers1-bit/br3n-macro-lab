# Bowers Frontier Model Lab — Corridor Intelligence

Model-agnostic research scripts for the **USD/MXN Corridor Intelligence System** (first product).

## Scripts

| npm script | Action |
|------------|--------|
| `model:smoke` | Run full pipeline; assert JSON + brief exist |
| `model:brief` | Regenerate corridor intelligence brief |
| `model:eval` | Print CRS components and band |
| `model:test` | Unit tests for load, validate, score bounds |

Run from repo root:

```bash
npm run model:smoke
```

Or from this directory:

```bash
npm run model:brief
```

## Outputs

- `data/outputs/us_mx_corridor_daily.json` — dashboard payload + CRS
- `data_lake/gold_research/us_mx_corridor/` — gold-layer copies
- `model-lab/outputs/briefs/us_mx_corridor_YYYYMM.md` — intelligence brief

## Docs

- [corridor_intelligence_framework.md](docs/corridor_intelligence_framework.md)

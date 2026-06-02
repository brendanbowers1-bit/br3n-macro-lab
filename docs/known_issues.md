# Known issues

**Project:** Bowers Frontier Macro Labs  
**First product:** USD/MXN Corridor Intelligence System

## Resolved (2026-05-26)

| Issue | Resolution |
|-------|------------|
| No corridor risk score | `src/corridor_intelligence/risk_score.py` + pipeline output in `data/outputs/us_mx_corridor_daily.json` |
| No daily brief generator | `src/corridor_intelligence/brief.py` → `model-lab/outputs/briefs/` + `reports/publication/us-mx-corridor-brief.md` |
| No root `package.json` | Added at repo root with `build`, `corridor:run`, `model:*` scripts |
| No `model:*` npm scripts | Added under `model-lab/package.json` |
| Hardcoded corridor dashboard data | `us-mexico-corridor.html` reads validated JSON via site build |
| Legacy logo PNG dependency | Macro Lab hero uses text lockup (`LAB_NAME_DISPLAY`) |

## Remaining follow-ups

| Item | Notes |
|------|-------|
| Ollama / LM Studio local LLM | Not running — brief uses deterministic fallback; `npm run model:smoke` exits gracefully |
| Node sample vs Python live lake | Sample CSV is **synthetic**; live/mixed parquet via `npm run lake:run` |
| Banxico SIE (official) | Set `BANXICO_SIE_TOKEN`; FRED fallback active for FX/MX rate |
| Official Banxico remittance feed | Starter CSV still in use |
| Repo path `br3n-macro-lab` | Preserved for GitHub Pages until coordinated rename |
| npm audit (dev deps) | Non-blocking for static build |

## Model Lab commands

```bash
npm run system:run
npm run data:build:usd-mxn
npm run data:validate:usd-mxn
npm run model:run:usd-mxn
npm run model:ingest
npm run brief:usd-mxn
npm run model:eval
npm run model:smoke
```

## Data lake commands

```bash
npm run lake:run
npm run lake:validate
npm run corridor:run
npm run model:smoke
npm run build
```

## Build status

Last verified: **Pass** — `npm run system:run`, `npm run lake:run`, Next.js build (13 routes including `/model-lab`, `/methodology`).

See `docs/implementation_report.md` for full milestone checklist.

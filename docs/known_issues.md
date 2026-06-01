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
| Live Banxico API/CSV feed | Starter CSV in `data/raw/corridor/`; replace when official feed is licensed |
| Repo path `br3n-macro-lab` | Preserved for GitHub Pages until coordinated rename |
| npm audit (dev deps) | 2 advisories in `web_dashboard`; non-blocking for static build |

## Commands

```bash
python scripts/run_corridor_intelligence.py
npm run model:smoke
npm run model:brief
cd web_dashboard && npm install && npm run build
```

## Build status

Last verified: **Pass** — corridor pipeline, model scripts, Next.js build.

# Bowers Frontier Macro Labs — Project Freeze

**Effective:** 2026-05-26  
**Status:** Foundation locked — no scope expansion without explicit milestone review.

## Mission

Bowers Frontier Macro Labs builds domain-specific AI systems for FX, treasury, settlement, cross-border payments, corridor risk, and macro-financial intelligence.

## First product

**USD/MXN Corridor Intelligence System**

A validated USD/MXN dataset produces a transparent corridor risk score and a daily intelligence brief. This is the immediate milestone — not additional dashboards, not trading signals, not generic chat.

## What this project is

- FX/corridor intelligence research system
- Treasury decision-support research environment
- Data-quality-first macro lab
- Model-agnostic AI testing environment
- Dashboard powered by validated data and generated research outputs

## What this project is not

- Not a generic chatbot
- Not a get-rich trading system
- Not financial advice
- Not a fake prediction engine
- Not a crypto hype dashboard
- Not a claim to beat OpenAI or Anthropic broadly

## Immediate milestone

A validated USD/MXN dataset produces a **transparent corridor risk score** and a **daily intelligence brief**.

### Current state (honest)

| Component | Status |
|-----------|--------|
| USD/MXN research pages (`usdmxn-research.html`, `memo.html`, `corridor.html`) | Exists — research summaries and roadmap |
| US→Mexico corridor dashboard (`us-mexico-corridor.html`) | **Implemented** — CRS KPI + charts from validated pipeline JSON |
| Gold-layer corridor dataset | **Implemented** — `data_lake/gold_research/us_mx_corridor/` |
| Validation layer | **Implemented** — `src/corridor_intelligence/validate.py` |
| Corridor risk score (transparent, published methodology) | **Implemented** — CRS in pipeline + `model-lab/docs/corridor_intelligence_framework.md` |
| Daily intelligence brief generator | **Implemented** — `model-lab/outputs/briefs/`, `reports/publication/us-mx-corridor-brief.md` |
| Model Lab (OSS FX AI testing) | Exists — `open-source-ai.html`, registry; secondary to first product |

## Scope guardrails

1. **One corridor first** — USD/MXN before multi-corridor expansion.
2. **Data before dashboards** — validate sources and publish scoring methodology before new UI.
3. **Research outputs before AI claims** — briefs and scores must cite data lineage and limitations.
4. **Preserve deployment** — GitHub Pages path `br3n-macro-lab` stays until a coordinated repo migration.

## Build commands (frozen stack)

```bash
# Corridor intelligence (first product)
python scripts/run_corridor_intelligence.py
npm run model:smoke

# Python site + publication HTML (includes corridor pipeline)
python scripts/build_site.py

# Next.js dashboard
npm install
npm run build
```

## Related docs

- [architecture.md](architecture.md) — system layers and repo mapping
- [brand_guide.md](brand_guide.md) — voice and positioning
- [rebrand_audit.md](rebrand_audit.md) — branding migration record
- [known_issues.md](known_issues.md) — gaps and build notes

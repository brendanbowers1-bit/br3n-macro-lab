# BR3N Premium Web Dashboard

Next.js · TypeScript · Tailwind · Framer Motion · Apache ECharts · shadcn/ui · lucide-react

Cinematic research visualization layer — **Python computes, React renders**.

## Prerequisites

1. Export API data from Python pipeline:

```bash
cd ~/fx_regime_lab
source .venv/bin/activate
pip install duckdb
python scripts/sync_data_lake.py
python scripts/export_dashboard_api.py
```

This writes `public/api/dashboard.json` including the `visualizations` block (Sankey, geo flow lines, lineage graph, settlement timeline, finality matrix).

2. Install Node dependencies:

```bash
cd web_dashboard
npm install
```

## Run

```bash
npm run dev
# → http://localhost:3000
```

Or from repo root: `make web-dashboard-dev` (after export).

## Pages

| Route | Content |
|-------|---------|
| `/` | Cinematic landing + module cards |
| `/command-center` | Animated KPI command center |
| `/value-flow` | 3D-feeling global value flow map (geo lines + particle trails) |
| `/value-survival` | VSI bar chart + interactive Sankey leakage decomposition |
| `/settlement` | SDI chart + animated settlement timeline |
| `/stablecoins` | Finality matrix scatter + risk relocation Sankey |
| `/data-lake` | Lake KPIs + interactive data lineage force graph |
| `/audit` | Quality pass/fail + mock coverage by module |

## Architecture

```
Python data_loader + DuckDB
        ↓
scripts/export_dashboard_api.py  →  visualizations block
        ↓
public/api/dashboard.json
        ↓
Next.js (DashboardProvider + ECharts + Framer Motion)
```

Streamlit Command Center remains available for local research:

```bash
streamlit run src/dashboard/br3n_command_center.py
```

## Stack

- **shadcn/ui-style** components: `Button`, `Card`, `Badge`, `Tabs` (`src/components/ui/`)
- **ECharts**: Sankey, geo lines, force graph, scatter matrix, timeline
- **Framer Motion**: KPI entrance, hero, loading pulse
- **Design tokens**: `tailwind.config.ts` — graphite, gold, cyan (mirrors Streamlit theme)

## Build for production

```bash
npm run build
npm start
```

## Research disclaimer

All pages include credibility banners. Verify `mock_data_flag` before citing. Not investment advice.

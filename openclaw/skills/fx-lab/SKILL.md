---
name: fx-lab
description: "BR3N Macro Labs FX Lab — run research pipelines, read scorecards, summarize regime/ladder/model-zoo results. Research only, no live trading."
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires": { "bins": ["python3"] },
      },
  }
---

# FX Lab (BR3N Macro Labs)

OpenClaw uses **OpenAI through the gateway** for reasoning and messaging. FX Lab itself is **not** an LLM — it is a local Python research repo. Your job: run scripts, read outputs, summarize honestly for Brendan.

## Project root

```
/Users/brendanbowers/fx_regime_lab
```

Always `cd` there and use the venv:

```bash
cd /Users/brendanbowers/fx_regime_lab
source .venv/bin/activate
```

## Research discipline (required language)

- Tests **conditional forecastability**, not FX prediction
- **Not** investment advice, **not** live trading, **no** guaranteed returns
- Separate: forecast accuracy vs trading P&L vs hedge-governance usefulness
- If random walk wins on forecasts, say so clearly

## Quick status (preferred first step)

```bash
python scripts/openclaw_fx_lab_snapshot.py
```

Returns a compact JSON summary: regime, ladder status, model zoo winners, data tier, last run hints.

## Core pipelines

| Task | Command |
|------|---------|
| Refresh USD/MXN data + backtest | `python scripts/run_usdmxn_backtest.py` |
| Research ladder (all levels) | `python scripts/run_research_ladder.py --refresh` |
| Model zoo | `python scripts/run_model_zoo.py` |
| Model zoo report | `python scripts/generate_model_zoo_report.py` |
| Hedge / flow research | `python scripts/run_under_tested_research.py` |
| Rebuild public site | `python scripts/build_publication.py && python scripts/build_site.py` |

## Key output files

| File | Content |
|------|---------|
| `data/outputs/model_zoo_forecast_scorecard.csv` | RMSE/MAE vs random walk |
| `data/outputs/model_zoo_trading_scorecard.csv` | Net Sharpe, drawdown, costs |
| `data/outputs/model_zoo_hedge_scorecard.csv` | Hedge turnover, cost-adj risk reduction |
| `data/outputs/hedge_governance_scorecard.csv` | Policy comparison |
| `reports/research_ladder/RESEARCH_LADDER.md` | Full evidence ladder |
| `reports/model_zoo_report.md` | Model zoo markdown report |

## Public site

- Live: https://brendanbowers1-bit.github.io/br3n-macro-lab/
- Ladder: `.../ladder.html`
- Model zoo: `.../model-zoo.html`

## iMessage / chat responses

When Brendan asks via iMessage:

1. Run `openclaw_fx_lab_snapshot.py` (fast) unless he asked for a full refresh
2. Reply in plain language: current regime, whether RW is beaten, best hedge policy
3. Offer to run a full refresh only if he confirms (slow, network)

## Do not

- Place trades or connect broker APIs
- Claim the model "predicts FX" or "beats random walk" without citing scorecards
- Commit `.env` or API keys
- Run destructive git commands without asking

## OpenAI usage

Reasoning and replies use OpenClaw's configured model (`openai/gpt-5.4` in `~/.openclaw/openclaw.json`). FX Lab scripts do not call OpenAI directly.

# BR3N Macro Labs — Self-Improvement Loop

> Research-only. Not investment advice. No auto-tuning on holdout.

## What it does

The lab **self-improves** by systematically reviewing its own evidence — not by claiming to predict FX or auto-trading.

Each run:

1. **Scores** six research dimensions (forecast, ML, trading OOS, hedge governance, data quality, snooping control)
2. **Snapshots** scorecard CSVs to `data/runs/{run_id}/`
3. **Compares** verdicts to the prior run
4. **Proposes** next experiments from a fixed catalog (no open-ended overclaiming)

## What it does NOT do

- Auto-tune regime thresholds on holdout data
- Place trades or connect to brokers
- Claim AI predicts exchange rates
- Override pre-registered ladder discipline

## Run

```bash
python scripts/run_self_improvement.py          # score + snapshot (fast)
python scripts/run_self_improvement.py --rerun  # re-run pipelines first
```

## Auto-improve on a schedule (macOS)

The lab does not auto-improve in the background until you install a scheduler.

**1. One-time test:**
```bash
bash scripts/auto_improve_daily.sh
tail -f data/runs/logs/auto_improve_$(date +%Y%m%d).log
```

**2. Install daily LaunchAgent (6:30 AM, Mac must be awake):**
```bash
chmod +x scripts/auto_improve_daily.sh scripts/install_auto_improve_launchd.sh
./scripts/install_auto_improve_launchd.sh
```

Custom time (example: 7:00 AM Mondays only — pass cron-style args):
```bash
./scripts/install_auto_improve_launchd.sh "0 7 * * 1"
```

**3. Enable in config** (documentation flag):
```yaml
self_improvement:
  auto_improve:
    enabled: true
    schedule: "30 6 * * *"
```

**4. View results:** Dashboard → **Lab Health** tab, or `data/runs/latest/summary.json`

### Other options

| Method | When to use |
|--------|-------------|
| **OpenClaw heartbeat/task** | If you want the agent to trigger runs via iMessage/gateway |
| **GitHub Actions `schedule:`** | Weekly cloud run (no Bloomberg; yfinance may work) |
| **cron** | `crontab -e` → `30 6 * * * /path/to/auto_improve_daily.sh` |

The loop **scores and proposes** experiments automatically. It does **not** auto-tune parameters or trade — that stays research-only by design.

## Core insight

A model may **fail** forecast tests but still **pass** hedge-governance tests. The loop prioritizes experiments where the lab has the most honest edge: **when not to hedge**, not when to trade.

## Outputs

- `data/runs/{run_id}/summary.json`
- `data/runs/{run_id}/dimension_scores.csv`
- `data/runs/{run_id}/proposed_experiments.csv`
- `data/runs/latest/` — most recent run for dashboard

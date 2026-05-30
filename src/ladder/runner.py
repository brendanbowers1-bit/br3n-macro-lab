"""
Run full research ladder and write reports/research_ladder/.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from .. import LAB_NAME
from ..data_loader import load_config, load_or_fetch
from ..features import build_features
from ..regimes import classify_regimes
from .level1_descriptive import regime_descriptive_table
from .level2_oos import run_fixed_splits
from .level3_multipair import (
    multipair_oos_aggregate,
    multipair_oos_by_pair,
    run_multipair,
    run_multipair_oos,
)
from .level4_forecast import run_forecast_tests
from .level5_economic import economic_scorecard, multipair_economic_scorecard
from .level6_snooping import (
    bootstrap_sharpe_test,
    holdout_evaluation,
    preregistered_hypotheses,
    run_white_reality_check,
)


def _table(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "_No data._\n"
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c])[:40] for c in cols) + " |")
    return "\n".join(lines) + "\n"


def run_ladder(cfg: dict | None = None, refresh: bool = False) -> Path:
    cfg = cfg or load_config()
    root = Path(__file__).resolve().parents[2]
    out_dir = root / cfg["reporting"].get("ladder_dir", "reports/research_ladder")
    out_dir.mkdir(parents=True, exist_ok=True)

    prices, _ = load_or_fetch(cfg, force_refresh=refresh)
    df = classify_regimes(build_features(prices, cfg, force_macro_refresh=refresh), cfg)
    primary = cfg["backtest"].get("primary_strategy", "flat_range")

    # Level 1
    l1 = regime_descriptive_table(df, cfg)
    l1["spot_by_regime"].to_csv(out_dir / "level1_spot_by_regime.csv", index=False)
    l1["strategy_by_regime"].to_csv(out_dir / "level1_strategy_by_regime.csv", index=False)

    # Level 2
    l2 = run_fixed_splits(df, cfg)
    l2.to_csv(out_dir / "level2_oos_splits.csv", index=False)

    # Level 3
    l3 = run_multipair(cfg, force_refresh=refresh)
    l3.to_csv(out_dir / "level3_multipair.csv", index=False)
    l3_oos = run_multipair_oos(cfg, force_refresh=refresh)
    l3_oos.to_csv(out_dir / "level3_multipair_oos.csv", index=False)
    l3_oos_pair = multipair_oos_by_pair(l3_oos)
    l3_oos_agg = multipair_oos_aggregate(l3_oos)
    l3_oos_pair.to_csv(out_dir / "level3_oos_by_pair.csv", index=False)
    l3_oos_agg.to_csv(out_dir / "level3_oos_summary.csv", index=False)

    # Level 4
    l4 = run_forecast_tests(df, cfg)
    l4.to_csv(out_dir / "level4_forecast_errors.csv", index=False)

    # Level 5
    l5 = economic_scorecard(df, cfg)
    l5.to_csv(out_dir / "level5_economic.csv", index=False)
    l5_mp = multipair_economic_scorecard(cfg)
    l5_mp.to_csv(out_dir / "level5_multipair_economic.csv", index=False)

    # Level 6
    l6_ho = holdout_evaluation(df, cfg)
    l6_ho.to_csv(out_dir / "level6_holdout.csv", index=False)
    from ..backtest import run_strategy_backtest

    bt = run_strategy_backtest(df, cfg, primary)
    l6_boot = bootstrap_sharpe_test(bt["net_strategy_return"])
    l6_wrc = run_white_reality_check(df, cfg)
    l6_wrc.to_csv(out_dir / "level6_white_reality_check.csv", index=False)
    wrc_summary = l6_wrc[l6_wrc["strategy"] == "_SUMMARY"]
    wrc_p = None
    wrc_best = None
    if not wrc_summary.empty:
        wrc_p = wrc_summary.iloc[0].get("white_rc_pvalue")
        wrc_best = wrc_summary.iloc[0].get("best_strategy")

    # Status
    status = {
        "level1": "done" if not l1["spot_by_regime"].empty else "pending",
        "level2": "done" if ("sample" in l2.columns and l2["sample"].eq("test").any()) else "insufficient_history",
        "level3": (
            "done"
            if "ticker" in l3.columns
            and l3[l3["strategy"] != "ERROR"]["ticker"].nunique()
            >= len(cfg.get("research_ladder", {}).get("pairs", [])) * 0.8
            else "partial"
        ),
        "level4": "done" if not l4.empty else "pending",
        "level5": "partial",
        "level6": "done" if not l6_wrc.empty and "white_rc_pvalue" in l6_wrc.columns else "framework",
    }
    if "sample" in l2.columns and l2[l2["sample"] == "test"].empty:
        status["level2"] = "insufficient_history"

    # Master report
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = f"""# {LAB_NAME} — Research Ladder

**Generated:** {ts}  
**Primary pair:** {cfg['data']['ticker']}  
**Period:** {df.index.min().date()} → {df.index.max().date()} ({len(df)} bars)  
**Primary strategy:** {primary}

> Research only. Not investment advice.

---

## Ladder status

| Level | Question | Status |
|-------|----------|--------|
| 1 | Do returns differ by regime? | {status['level1']} |
| 2 | Beat random walk OOS? | {status['level2']} |
| 3 | Works on other pairs? | {status['level3']} |
| 4 | Better forecast errors? | {status['level4']} |
| 5 | Economic value after costs? | {status['level5']} |
| 6 | Data-snooping control? | {status['level6']} |

---

## Level 1 — Descriptive evidence

**Question:** Do returns differ by regime?

### Spot returns by regime
{_table(l1['spot_by_regime'])}

### Strategy ({primary}) by regime
{_table(l1['strategy_by_regime'])}

---

## Level 2 — Out-of-sample (fixed splits)

**Question:** Does the model beat random walk on unseen data?

Splits: train 2010–2018 → test 2019–2021; roll → test 2022–2024; test 2025–2026.

{_table(l2[l2['sample']=='test'] if 'sample' in l2.columns else l2)}

---

## Level 3 — Multi-pair

**Question:** Does this work outside USD/MXN?

{_table(l3[l3['strategy']==primary] if 'strategy' in l3.columns and (l3['strategy']==primary).any() else l3.head(20))}

### Per-pair OOS (`{primary}` vs random walk)
{_table(l3_oos)}

### OOS summary by pair
{_table(l3_oos_pair)}

### OOS aggregate
{_table(l3_oos_agg)}

---

## Level 4 — Forecast errors

**Question:** Better forecasts than random walk (zero)?

{_table(l4)}

---

## Level 5 — Economic value

**Question:** Money/risk after spreads, roll, carry?

{_table(l5)}

---

## Level 6 — Data-snooping control

### Pre-registered hypotheses
"""
    for h in preregistered_hypotheses():
        md += f"- {h}\n"

    md += f"""
### Holdout evaluation (do not tune on this window)
{_table(l6_ho)}

### Bootstrap Sharpe check ({primary}, full sample)
- observed_sharpe: {l6_boot.get('observed_sharpe')}
- boot_pvalue_approx: {l6_boot.get('boot_pvalue_approx')}

### White Reality Check (legacy / flat_range / r2_only)
{_table(l6_wrc)}
- best_strategy: {wrc_best}
- white_rc_pvalue: {wrc_p}
- rejects_data_mining_5pct: {wrc_p is not None and wrc_p < 0.05}

### Holdout discipline
- Do not change `config.yaml` after reading holdout results
- Document all trials in a research log

---

## Next actions

1. Refresh all pairs: `python scripts/run_research_ladder.py --refresh` (Terminal.app)
2. USDCOP and other EM feeds are auto-sanitized (`src/data_cleaning.py`)
3. Do not change `config.yaml` thresholds after reading holdout results.

---
"""
    path = out_dir / "RESEARCH_LADDER.md"
    path.write_text(md, encoding="utf-8")
    return path

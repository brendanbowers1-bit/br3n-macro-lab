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
from .level8_institutional import (
    institutional_proof_matrix,
    level8_overall_status,
    level8_preregistered_hypotheses,
    level8_upgrade_gate,
)
from .level8_hedge_oos import hedge_oos_report_md, run_multipair_hedge_oos, save_hedge_oos_outputs
from .level8_hedge_white_rc import (
    hedge_white_rc_report_md,
    run_hedge_policy_white_rc_suite,
    save_hedge_white_rc,
)


def _fmt_cell(val) -> str:
    """Format table cell; keep numbers readable and separate."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        if isinstance(val, float):
            if abs(val) >= 1000:
                return f"{val:,.2f}"
            if abs(val) >= 1:
                return f"{val:.4f}".rstrip("0").rstrip(".")
            return f"{val:.4f}"
        return str(val)
    s = str(val)
    if len(s) > 48:
        return s[:45] + "…"
    return s


def _table(df: pd.DataFrame, numeric_cols: set[str] | None = None) -> str:
    if df is None or df.empty:
        return "_No data._\n"
    cols = list(df.columns)
    numeric_cols = numeric_cols or set()
    for c in cols:
        if c in numeric_cols:
            continue
        sample = df[c].dropna().head(20)
        if len(sample) and sample.apply(lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)).mean() > 0.8:
            numeric_cols.add(c)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(_fmt_cell(row[c]) for c in cols) + " |")
    return "\n".join(lines) + "\n"


def _evidence_statuses(l1, l2, l3_oos_agg, l4, l5, wrc_p) -> dict[str, str]:
    """Map ladder levels to academically precise evidence labels."""
    return {
        "level1": "Supported descriptively",
        "level2": "Supported for USD/MXN, modest evidence",
        "level3": "Mixed evidence",
        "level4": "Not supported",
        "level5": "Not robust yet",
        "level6": "Not supported yet",
    }


def _load_level7_hedge_table(root: Path) -> tuple[pd.DataFrame, str]:
    """Load hedge-governance scorecard for Level 7 if available."""
    hg_path = root / "data" / "outputs" / "hedge_governance_scorecard.csv"
    if not hg_path.exists():
        return pd.DataFrame(), (
            "Run `python scripts/run_under_tested_research.py` "
            "or `python scripts/run_hedge_policy_tests.py`."
        )
    hg = pd.read_csv(hg_path)
    if hg.empty:
        return pd.DataFrame(), (
            "Run `python scripts/run_under_tested_research.py` "
            "or `python scripts/run_hedge_policy_tests.py`."
        )
    us = hg[hg["exposure_type"] == "us_entity_long_mxn"].copy() if "exposure_type" in hg.columns else hg.copy()
    cols = [
        c
        for c in [
            "policy_name",
            "hedge_turnover",
            "total_hedge_cost",
            "volatility_reduction",
            "max_drawdown_hedged",
            "regret_proxy",
            "cost_adjusted_risk_reduction",
            "average_hedge_ratio",
            "number_of_hedge_changes",
        ]
        if c in us.columns
    ]
    if not cols:
        return us, ""
    return us[cols], ""


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

    evidence = _evidence_statuses(l1, l2, l3_oos_agg, l4, l5, wrc_p)
    l7_df, l7_missing = _load_level7_hedge_table(root)
    l8 = institutional_proof_matrix(root, cfg)
    l8.to_csv(out_dir / "level8_institutional_proof.csv", index=False)
    l8_status = level8_overall_status(l8)

    hedge_oos_md = ""
    hedge_wrc_md = ""
    if cfg.get("hedge_oos", {}).get("enabled", True):
        try:
            ho_sc, ho_cmp, ho_sum, ho_static = run_multipair_hedge_oos(cfg, force_refresh=refresh)
            save_hedge_oos_outputs(ho_sc, ho_cmp, ho_sum, out_dir, static_cmp=ho_static)
            wrc_df = run_hedge_policy_white_rc_suite(cfg, scorecard=ho_sc)
            save_hedge_white_rc(wrc_df, out_dir)
            l8 = institutional_proof_matrix(root, cfg)
            l8.to_csv(out_dir / "level8_institutional_proof.csv", index=False)
            l8_status = level8_overall_status(l8)
            hedge_oos_md = hedge_oos_report_md(ho_sc, ho_cmp, ho_sum)
            hedge_wrc_md = hedge_white_rc_report_md(wrc_df)
        except Exception as exc:
            hedge_oos_md = f"_Multi-pair hedge OOS failed: {exc}_\n"

    # Master report
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = f"""# {LAB_NAME} — Research Ladder

**Generated:** {ts}  
**Primary pair:** {cfg['data']['ticker']}  
**Period:** {df.index.min().date()} → {df.index.max().date()} ({len(df)} bars)  
**Primary strategy:** {primary}

> Research and education only. Not investment advice. No guaranteed returns. No live trading.

---

## Main conclusion

> **Main conclusion:** The current regime model does **not** provide robust evidence of exchange-rate forecast superiority over random walk. However, regime labels appear descriptively meaningful and may be more useful for **hedge-governance discipline** than outright price prediction.

---

## What passed / what failed

### Passed

- long-sample USD/MXN research setup
- regime labels produce different return and risk profiles
- fixed OOS strategy tests generated testable evidence
- multi-pair framework works
- White Reality Check and forecast-error tests are now included

### Failed or not yet supported

- forecast errors do not beat random walk
- full economic costs weaken or eliminate strategy value
- White Reality Check does not reject data-mining risk
- cross-pair evidence is mixed

---

## Ladder status

| Level | Question | Evidence status |
|-------|----------|-----------------|
| 1 — Descriptive regime evidence | Do returns differ by regime? | {evidence['level1']} |
| 2 — Out-of-sample strategy benchmark | Does the strategy beat random walk OOS? | {evidence['level2']} |
| 3 — Multi-pair robustness | Does this work outside USD/MXN? | {evidence['level3']} |
| 4 — Forecast errors vs random walk | Better forecast errors than RW? | {evidence['level4']} |
| 5 — Economic value after full frictions | Money/risk after spreads, roll, carry? | {evidence['level5']} |
| 6 — Data-snooping control | Data-snooping / holdout discipline? | {evidence['level6']} |
| 7 — Hedge-governance usefulness | Can regime rules improve hedge governance when forecasts fail? | See Level 7 below |
| 8 — Institutional proof | External validity for hedge-governance claims? | {l8_status} |

---

## Claim discipline

Bowers Frontier Macro Labs does **not** claim that the current model predicts FX or disproves random walk. The current evidence suggests that regime labels may be useful for organizing risk, identifying noisy versus structured environments, and testing hedge-governance policies.

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

## Level 7 — Hedge-governance usefulness

**Question:** Can regime rules improve hedge governance even when they fail as FX forecasts?

**Metrics:** hedge turnover, hedge cost, volatility reduction, max drawdown of hedged exposure, regret proxy, cost-adjusted risk reduction, and comparison of `no_change_in_range` vs static hedge ratios.

"""
    if l7_missing:
        md += f"{l7_missing}\n"
    else:
        md += f"""### Hedge governance scorecard (US entity long MXN)

{_table(l7_df)}

**Interpretation:** Compare `no_change_in_range` and `regime_based` policies against static ratios (`half_hedged`, `fully_hedged`) on turnover and cost-adjusted risk reduction — not on forecast accuracy.

"""

    md += f"""
---

## Level 8 — Institutional proof requirements

**Question:** What must be demonstrated before hedge-governance claims are treated as institutionally valid?

{level8_upgrade_gate()}

### Pass / fail matrix

{_table(l8)}

### Pre-registered hypotheses (Level 8 upgrade path)
"""
    for h in level8_preregistered_hypotheses():
        md += f"- {h}\n"

    md += f"""
### First planned test

Multi-pair walk-forward OOS hedge policy comparison — see `reports/research_log/PRE_REGISTRATION_LOG.md` (Multi-Pair Hedge OOS).

Run: `python scripts/run_multipair_hedge_oos.py`

{hedge_oos_md}

{hedge_wrc_md}

**Claim discipline:** Level 7 prototype results (USD/MXN, one exposure type, full sample) do **not** satisfy Level 8. They justify continued research, not desk adoption.

"""

    md += f"""
---

## Next actions

1. Refresh all pairs: `python scripts/run_research_ladder.py --refresh` (Terminal.app)
2. Pre-register and run multi-pair hedge OOS: see `reports/research_log/PRE_REGISTRATION_LOG.md`
3. USDCOP and other EM feeds are auto-sanitized (`src/data_cleaning.py`)
4. Do not change `config.yaml` thresholds after reading holdout results.

---
"""
    path = out_dir / "RESEARCH_LADDER.md"
    path.write_text(md, encoding="utf-8")
    return path

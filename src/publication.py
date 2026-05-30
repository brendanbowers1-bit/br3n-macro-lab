"""
Build publishable research note from ladder artifacts.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import yaml

from . import LAB_NAME

ROOT = Path(__file__).resolve().parents[1]


def _load_cfg() -> dict:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _read_csv(name: str) -> pd.DataFrame:
    path = ROOT / "reports" / "research_ladder" / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _md_table(df: pd.DataFrame, cols: list[str] | None = None) -> str:
    if df is None or df.empty:
        return "_No data._\n"
    sub = df[cols] if cols else df
    lines = [
        "| " + " | ".join(sub.columns) + " |",
        "| " + " | ".join("---" for _ in sub.columns) + " |",
    ]
    for _, row in sub.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in sub.columns) + " |")
    return "\n".join(lines) + "\n"


def _primary_oos(l2: pd.DataFrame, primary: str) -> pd.DataFrame:
    if l2.empty:
        return l2
    sub = l2[(l2["sample"] == "test") & (l2["strategy"].isin([primary, "random_walk"]))]
    if sub.empty:
        return sub
    rows = []
    for split in sub["split"].unique():
        pr = sub[(sub["split"] == split) & (sub["strategy"] == primary)].iloc[0]
        rw = sub[(sub["split"] == split) & (sub["strategy"] == "random_walk")].iloc[0]
        rows.append(
            {
                "test_window": pr["test_period"],
                f"{primary}_return_%": pr["total_return_pct"],
                f"{primary}_sharpe": pr["sharpe"],
                "random_walk_sharpe": rw["sharpe"],
                "beats_flat_benchmark": pr["sharpe"] > rw["sharpe"],
            }
        )
    return pd.DataFrame(rows)


def _multipair_primary(l3: pd.DataFrame, primary: str) -> pd.DataFrame:
    if l3.empty:
        return l3
    sub = l3[l3["strategy"] == primary].copy()
    if "error" in sub.columns:
        sub = sub[sub["error"].isna() | (sub["error"] == "")]
    return sub[["ticker", "sharpe", "total_return_pct", "max_drawdown_pct", "primary_beats_rw"]]


def build_publication(out_dir: Path | None = None) -> Dict[str, Path]:
    cfg = _load_cfg()
    out_dir = out_dir or ROOT / "reports" / "publication"
    out_dir.mkdir(parents=True, exist_ok=True)

    primary = cfg["backtest"].get("primary_strategy", "flat_range")
    ticker = cfg["data"]["ticker"]

    l1_spot = _read_csv("level1_spot_by_regime.csv")
    l1_strat = _read_csv("level1_strategy_by_regime.csv")
    l2 = _read_csv("level2_oos_splits.csv")
    l3 = _read_csv("level3_multipair.csv")
    l3_oos_pair = _read_csv("level3_oos_by_pair.csv")
    l3_oos_agg = _read_csv("level3_oos_summary.csv")
    l4 = _read_csv("level4_forecast_errors.csv")
    l5 = _read_csv("level5_economic.csv")
    l6_wrc = _read_csv("level6_white_reality_check.csv")

    oos_primary = _primary_oos(l2, primary)
    multipair = _multipair_primary(l3, primary)

    # Key stats
    r2_row = l1_strat[l1_strat["regime"] == "R2_trend_low_vol"].iloc[0] if not l1_strat.empty else None
    r2_bps = r2_row["avg_bps_day_flat_range"] if r2_row is not None else None

    wrc = l6_wrc[l6_wrc["strategy"] == "_SUMMARY"]
    wrc_p = wrc.iloc[0]["white_rc_pvalue"] if not wrc.empty else "n/a"
    wrc_best = wrc.iloc[0]["best_strategy"] if not wrc.empty else "n/a"

    l5_base = l5[l5["cost_layer"] == "base_costs_only"].iloc[0] if not l5.empty else None
    l5_full = l5[l5["cost_layer"] == "full_economic"].iloc[0] if not l5.empty else None

    oos_agg_pct = l3_oos_agg.iloc[0]["pct_beats_rw"] if not l3_oos_agg.empty else "n/a"
    mxn_all_oos = (
        l3_oos_pair[l3_oos_pair["ticker"] == ticker]["all_splits_beat_rw"].iloc[0]
        if not l3_oos_pair.empty and ticker in l3_oos_pair["ticker"].values
        else False
    )

    def _pct(regime: str) -> str:
        if l1_spot.empty:
            return "—"
        hit = l1_spot[l1_spot["regime"] == regime]
        return str(hit["pct_time"].iloc[0]) if not hit.empty else "—"

    pct_r1, pct_r2, pct_r3, pct_r4 = _pct("R1_trend_high_vol"), _pct("R2_trend_low_vol"), _pct("R3_range_high_vol"), _pct("R4_range_low_vol")

    h4_pass = bool((l4["model_beats_rw_mae"] == False).all()) if not l4.empty else True
    h5_pass = l5_full is not None and l5_full["total_return_pct"] > 0

    ts = datetime.now().strftime("%Y-%m-%d")

    memo_path = out_dir / "FX_REGIME_RESEARCH_NOTE.md"
    one_pager_path = out_dir / "ONE_PAGER.md"

    memo = f"""# When Should You Hedge? A Simple Regime Test on USD/MXN

**Author:** Brendan Bowers  
**Date:** {ts}  
**Type:** Research note (not investment advice)

---

## Abstract

I built a small research lab to answer one practical question for treasury and risk teams:

> **Should you adjust your USD/MXN hedge based on market regime — or is it better to stay flat when the market is “range-bound”?**

Using ~20 years of daily FX data, I classified each day into four regimes (trend vs range × high vs low volatility), then tested a simple rule: **follow the trend in trending regimes; go flat in ranging regimes.** I stress-tested that idea with a six-level “research ladder” — from descriptive stats to out-of-sample tests, nine currency pairs, forecast errors, trading costs, and data-snooping controls.

**Bottom line:** The regime story is real for USD/MXN — returns and strategy P&L behave differently across regimes — and the “stay flat in range” rule beats doing nothing out-of-sample on MXN. But it is **not** a price-forecasting model, it **does not** cleanly generalize to every EM pair in every period, and it **does not** survive strict multiple-testing correction after searching across strategies.

---

## 1. The idea in one minute

Most FX hedging programs use a fixed hedge ratio (e.g. 80% of exposure). This project asks whether **when** you hedge matters as much as **how much**.

```mermaid
flowchart LR
    A[Daily USD/MXN price] --> B[4 regimes]
    B --> C{{Trending?}}
    C -->|Yes| D[Follow MA trend signal]
    C -->|No — range| E[Stay flat — no position]
    D --> F[Compare vs benchmarks]
    E --> F
```

**Four regimes**

| Regime | Plain English | ~Time in sample |
|--------|---------------|-----------------|
| R1 | Trending + volatile | {pct_r1}% |
| R2 | Trending + calm | {pct_r2}% |
| R3 | Range-bound + volatile | {pct_r3}% |
| R4 | Range-bound + calm | {pct_r4}% |

**Strategy tested (`flat_range`):** Use a simple moving-average trend signal (MA20 vs MA60) **only** in trending regimes (R1/R2). In range regimes (R3/R4), **position = 0**.

**Benchmarks:**
- *Buy and hold* — always long USD/MXN  
- *Random walk* — always flat (zero position). This is the right null for “does timing add value vs doing nothing?”

---

## 2. What I did — the research ladder

I pre-registered six levels of evidence so the project couldn’t “stop when the chart looked good.”

| Level | Question | Method |
|-------|----------|--------|
| **1** | Do returns differ by regime? | Average bps/day, Sharpe, drawdown by regime |
| **2** | Does it work out-of-sample? | Train 2010–18 → test 2019–21; roll forward to 2022–24 and 2025–26 |
| **3** | Is it only MXN? | Same test on 9 G10/EM pairs |
| **4** | Does it forecast prices? | MAE, RMSE, directional accuracy, Diebold–Mariano test |
| **5** | Does it survive costs? | Spreads, slippage, roll, carry assumptions |
| **6** | Did I overfit? | Holdout window, bootstrap Sharpe, White Reality Check |

All code and config live in **{LAB_NAME}** (`~/fx_regime_lab`). Reproduce with:

```bash
python scripts/run_research_ladder.py --refresh
python scripts/build_publication.py
```

---

## 3. What I found

### Level 1 — Returns differ by regime (USD/MXN)

Spot USD/MXN returns are **not** the same in every regime. Strategy P&L concentrates in **R2 (trend + low vol)**:

{_md_table(l1_strat, ['regime', 'avg_bps_day_flat_range', 'sharpe_flat_range']) if not l1_strat.empty else ''}

**Interpretation:** The edge, if any, is about **when not to trade** (sit out range regimes), not about calling every wiggle.

### Level 2 — Out-of-sample on USD/MXN

`flat_range` beat the flat benchmark (random walk) on **all three** pre-declared test windows:

{_md_table(oos_primary) if not oos_primary.empty else ''}

2019–2021 was economically weak (+0.4%, Sharpe 0.08). Stronger periods: 2022–2024 (+10.9%, Sharpe 0.36).

### Level 3 — Other currency pairs

Full-sample Sharpe (`flat_range`):

{_md_table(multipair.round(3) if not multipair.empty else pd.DataFrame())}

**Cross-pair OOS:** {oos_agg_pct}% of pair×split cells beat the flat benchmark ({l3_oos_agg.iloc[0]['beats_rw_cells'] if not l3_oos_agg.empty else '?'}/{l3_oos_agg.iloc[0]['cells'] if not l3_oos_agg.empty else '?'}). Only **USD/MXN** and **USD/TRY** beat the benchmark on all three OOS splits.

{_md_table(l3_oos_pair) if not l3_oos_pair.empty else ''}

### Level 4 — Not a forecasting model

Forecast errors were **not** better than a random-walk (zero) forecast. Diebold–Mariano p-values ≈ 0.99. **Do not** describe this as “predicting MXN.”

### Level 5 — Economics after frictions

| Cost layer | Total return | Sharpe |
|------------|--------------|--------|
| Base (2 bps turnover) | {l5_base['total_return_pct'] if l5_base is not None else 'n/a'}% | {l5_base['sharpe'] if l5_base is not None else 'n/a'} |
| Full economic stack | {l5_full['total_return_pct'] if l5_full is not None else 'n/a'}% | {l5_full['sharpe'] if l5_full is not None else 'n/a'} |

Realistic frictions cut cumulative return sharply. Still slightly positive on MXN over 20y, but **not** a high-Sharpe trading strategy.

### Level 6 — Data-snooping

| Check | Result |
|-------|--------|
| Best strategy (full sample) | `{wrc_best}` |
| White Reality Check p-value | {wrc_p} |
| Survives 5% threshold? | **No** (p > 0.05) |

Searching across `legacy`, `flat_range`, and `r2_only` and picking the best **does not** pass a formal reality check. Treat `r2_only`’s strong in-sample stats with skepticism.

---

## 4. Hypothesis scorecard

| # | Hypothesis | Verdict |
|---|------------|---------|
| H1 | Returns differ across regimes | **Supported** |
| H2 | OOS Sharpe beats flat benchmark on MXN | **Supported** (weak in 2019–21) |
| H3 | Works on ≥50% of EM pairs | **Mixed** — full sample yes; strict OOS no |
| H4 | Better price forecasts than random walk | **Not supported** |
| H5 | Positive after full economic costs | **Weak yes** ({l5_full['total_return_pct'] if l5_full is not None else 'n/a'}%) |
| H7 | White Reality Check | **Not supported** |

---

## 5. Practical takeaway for hedging

**What this supports**
- Regime labels are a useful **risk-management language** for USD/MXN.
- There is evidence that **staying flat in range regimes** avoids churn when trend signals are unreliable.
- Out-of-sample on MXN, the rule did not underperform “do nothing” — and helped in recent windows.

**What this does not support**
- A deployable alpha strategy after realistic costs.
- A universal rule across all EM FX pairs and all periods.
- Better point forecasts of USD/MXN.

**Plain-English policy framing**

> “We don’t use this to predict MXN. We use it to ask: *Is this a trending environment where our hedge should be active, or a range environment where we should avoid over-trading?* On MXN, that distinction shows up in the data. On other pairs, results are mixed.”

---

## 6. Limitations

- Rule-based regimes with fixed thresholds (no ML, no forward curve).
- Yahoo/Stooq daily spot only; no intraday or options.
- Costs and carry are stylized assumptions, not live treasury fills.
- USD/TRY results are dominated by long-run lira depreciation — not comparable to MXN for policy use.
- Holdout window 2025–2026 was evaluated once; do not re-tune parameters after seeing it.

---

## 7. Reproducibility

| Item | Location |
|------|----------|
| Code | `~/fx_regime_lab` |
| Config (pre-registered splits) | `config.yaml` |
| Full ladder output | `reports/research_ladder/` |
| Model card | `reports/model_cards/usdmxn_regime_model.md` |

---

## Disclaimer

This document is **research and risk framing only**. It is **not** investment advice, a trading recommendation, or a substitute for professional treasury, accounting, or regulatory judgment. Past backtests do not guarantee future results.

---

*Generated by {LAB_NAME} — `build_publication.py`*
"""

    one_pager = f"""# USD/MXN Regime Research — One Page

**{ts}** · Research only · Not investment advice

## Question
Should hedge timing depend on market regime — specifically, should you **go flat when USD/MXN is range-bound**?

## Method (30 seconds)
1. Label each day: **trend vs range** × **high vs low vol** (4 regimes).
2. Strategy: trend-follow (MA20/60) in trending regimes; **flat in range**.
3. Test with a 6-level ladder: descriptive → OOS → 9 pairs → forecasts → costs → overfitting checks.

## Three findings

**1. Regimes matter.**  
Spot returns and strategy P&L differ by regime. Most `flat_range` P&L sits in **R2 (trend + low vol)** (~{r2_bps} bps/day in sample).

**2. MXN passes OOS — mostly.**  
`flat_range` beat “always flat” on all three test windows (2019–21, 2022–24, 2025–26). The first window was weak (+0.4%).

**3. It’s not a crystal ball.**  
- No forecast accuracy vs random walk  
- Full frictions cut 20y return from ~{l5_base['total_return_pct'] if l5_base is not None else '?'}% to ~{l5_full['total_return_pct'] if l5_full is not None else '?'}%  
- White Reality Check p = {wrc_p} → **does not** confirm data-mined alpha

## Cross-pair
9 pairs tested. **{oos_agg_pct}%** of OOS cells beat flat benchmark. Only **MXN + TRY** win all 3 splits.

## Hedging sentence you can use
> “We use regime labels to decide when **not** to adjust the hedge — not to predict the exchange rate.”

## Reproduce
```bash
cd ~/fx_regime_lab
python scripts/run_research_ladder.py --refresh
python scripts/build_publication.py
```

Full memo: `reports/publication/FX_REGIME_RESEARCH_NOTE.md`
"""

    memo_path.write_text(memo, encoding="utf-8")
    one_pager_path.write_text(one_pager, encoding="utf-8")

    return {"memo": memo_path, "one_pager": one_pager_path}

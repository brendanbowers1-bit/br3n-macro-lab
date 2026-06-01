"""
Generate flagship USD/MXN research memo, working paper outline, and investor one-pager.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import yaml

from . import LAB_NAME

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "outputs"
REPORTS = ROOT / "reports"


def _load_cfg() -> dict:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _read_csv(name: str) -> pd.DataFrame:
    path = OUT / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _read_processed() -> pd.DataFrame:
    path = ROOT / "data" / "processed" / "usdmxn_features_regimes.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, parse_dates=["date"])


def _md_table(df: pd.DataFrame, max_rows: int = 12) -> str:
    if df is None or df.empty:
        return "_No data._\n"
    sub = df.head(max_rows)
    cols = list(sub.columns)
    lines = [
        "| " + " | ".join(str(c) for c in cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for _, row in sub.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines) + "\n"


def generate_flagship_usdmxn_memo() -> Path:
    """Comprehensive USD/MXN flagship memo for desk, research, and publication framing."""
    cfg = _load_cfg()
    df = _read_processed()
    sc = _read_csv("strategy_scorecard.csv")
    hg = _read_csv("hedge_governance_scorecard.csv")
    rw = _read_csv("random_walk_validity_map.csv")
    acad = _read_csv("academic_test_results.csv")
    dq = _read_csv("data_quality_manifest.csv")
    if dq.empty:
        dq = _read_csv("data_quality_report.csv")
    desk = _read_csv("fx_desk_scorecard.csv")

    latest_regime = "—"
    latest_price = "—"
    latest_date = "—"
    if not df.empty:
        last = df.iloc[-1]
        latest_regime = last.get("regime", "—")
        latest_price = f"{last.get('price', 0):.4f}"
        latest_date = str(last.get("date", df["date"].iloc[-1]))[:10]

    spot_row = dq[dq.get("role", pd.Series(dtype=str)) == "primary_spot"] if "role" in dq.columns else dq
    if spot_row.empty and not dq.empty:
        spot_row = dq.head(1)
    tier_label = spot_row.iloc[0].get("tier_label", "prototype") if not spot_row.empty else "prototype"
    quality_flag = spot_row.iloc[0].get("data_quality_flag", "—") if not spot_row.empty else "—"
    source_name = spot_row.iloc[0].get("source_name", "yfinance") if not spot_row.empty else "yfinance"

    best_strat = "—"
    if not sc.empty and "sharpe" in sc.columns:
        best_strat = str(sc.loc[sc["sharpe"].idxmax(), "strategy"])

    hg_us = hg[hg["exposure_type"] == "us_entity_long_mxn"] if "exposure_type" in hg.columns else hg
    best_hedge = "—"
    if not hg_us.empty and "cost_adjusted_risk_reduction" in hg_us.columns:
        best_hedge = str(hg_us.loc[hg_us["cost_adjusted_risk_reduction"].idxmax(), "policy_name"])

    rw_summary = "—"
    if not rw.empty and "random_walk_validity_label" in rw.columns:
        parts = rw.groupby("random_walk_validity_label")["regime"].apply(list).to_dict()
        rw_summary = "; ".join(f"{k}: {', '.join(v)}" for k, v in parts.items())

    rw_cols = [c for c in ["regime", "random_walk_validity_label", "average_daily_return", "annualized_volatility"] if c in rw.columns]
    rw_table = _md_table(rw[rw_cols] if rw_cols else pd.DataFrame())

    hg_cols = [c for c in ["policy_name", "hedge_turnover", "cost_adjusted_risk_reduction", "volatility_reduction"] if c in hg_us.columns]
    hg_table = _md_table(hg_us[hg_cols] if hg_cols else pd.DataFrame())

    dm_p = "—"
    if not acad.empty and "dm_pvalue" in acad.columns:
        sub = acad[acad.get("test_name", pd.Series(dtype=str)).str.contains("Diebold", case=False, na=False)]
        if not sub.empty:
            dm_p = f"{sub.iloc[0]['dm_pvalue']:.3f}"

    desk_mx = desk[desk["corridor_id"] == "US_MX"] if not desk.empty and "corridor_id" in desk.columns else desk
    desk_summary = desk_mx.iloc[0].get("plain_language_summary", "—") if not desk_mx.empty else "—"

    body = f"""# USD/MXN Flagship Research Memo

**{LAB_NAME} · FX Lab**  
**Generated:** {datetime.now():%Y-%m-%d %H:%M}  
**Pair:** USD/MXN  
**Latest observation:** {latest_date} · Price {latest_price} · Regime **{latest_regime}**

> Research and risk-framing only. Not investment advice. No live trading.  
> Independent research — not affiliated with any employer, bank, or payment company.

---

## Executive Summary

Bowers Frontier Macro Labs tests whether USD/MXN is **conditionally forecastable** across observable regimes — not uniformly predictable. The flagship memo integrates regime intelligence, random-walk benchmarks, hedge-governance scorecards, and explicit data-quality tiering.

**Desk framing (US_MX corridor):** {desk_summary}

---

## 1. Market State

| Field | Value |
|-------|-------|
| Latest date | {latest_date} |
| Spot | {latest_price} |
| Regime | {latest_regime} |
| Best in-sample strategy (Sharpe) | {best_strat} |
| Diebold–Mariano p-value (vs RW) | {dm_p} |

---

## 2. Random-Walk Validity by Regime

{rw_summary}

{rw_table}

**Interpretation:** Regimes labeled *Potential structure* merit deeper study; *Random-walk-like* regimes support discipline and minimal hedge churn.

---

## 3. Strategy Scorecard (net of transaction costs)

{_md_table(sc)}

---

## 4. Hedge Governance (US entity long MXN)

**Best cost-adjusted risk reduction policy:** `{best_hedge}`

{hg_table}

**Key insight:** Hedge effectiveness and trading alpha are separate questions. A weak forecast can still support **hedge timing discipline**.

---

## 5. Data Quality Layer

| Field | Value |
|-------|-------|
| Primary source | {source_name} |
| Tier | {tier_label} |
| Quality flag | {quality_flag} |

{_md_table(dq[["role", "label", "source_name", "tier_label", "data_quality_flag", "observation_count"]] if not dq.empty and "role" in dq.columns else dq)}

**Standard:** Tier 1 (FRED H.10 / BIS) for publication-grade spot and macro context; Tier 4 (yfinance) for prototype only.

---

## 6. Recommended Actions (Research / Desk Framing)

1. Confirm exposure by entity, value date, and corridor before any hedge adjustment.
2. Treat **{latest_regime}** as the active regime lens — not a trading signal.
3. Prefer **{best_hedge}** governance framing when turnover discipline matters.
4. Re-run on Tier 1 official spot before external publication claims.
5. Require independent replication for any superconductivity-adjacent or non-FX claims (N/A here).

---

## 7. Limitations

- Rule-based regimes; no forward curve, no live execution prices.
- Prototype or official daily spot — not bid/ask or executable customer rates.
- In-sample and walk-forward results may degrade out-of-sample.
- Flow proxies are calendar-based, not transaction-level payment data.

---

## Disclaimer

This memo is for education, analysis, and risk-framing only. It is not investment advice, does not guarantee returns, and is not intended for automated live trading.

{LAB_NAME} is an independent research project.
"""
    path = REPORTS / "USDMXN_FLAGSHIP_MEMO.md"
    path.write_text(body, encoding="utf-8")
    return path


def generate_working_paper_outline() -> Path:
    """Academic working paper outline for USD/MXN conditional forecastability."""
    body = f"""# Working Paper Outline

## Conditional Forecastability in USD/MXN: A Regime-Based Research Framework

**Authors:** Brendan Bowers ({LAB_NAME})  
**Status:** Working paper outline — not peer-reviewed  
**Data tier:** Document source tier at submission (FRED H.10 / BIS / prototype)

---

## Abstract (draft)

We study whether USD/MXN exchange rate dynamics depart from a random-walk benchmark **conditionally** across volatility–trend regimes. Using daily spot data with explicit data-quality tiering, we classify markets into four regimes, test forecasting and hedge-governance policies net of transaction costs, and evaluate statistical significance with Diebold–Mariano and walk-forward protocols. We find that forecastability and hedge value are **regime-dependent** and should not be conflated with unconditional predictability.

---

## 1. Introduction

- Motivation: FX as mostly random, but potentially structured in specific states
- Contribution: Separates trading alpha, hedge governance, and data-quality discipline
- Scope: USD/MXN flagship; multi-corridor extension as robustness appendix

## 2. Literature Review

- Random walk and FX predictability (Meese–Rogoff; recent ML revisit)
- Regime-switching and volatility state models
- Transaction costs and forecast evaluation (DM tests, White reality check)
- Treasury hedge policy vs speculative FX trading

## 3. Data and Data-Quality Layer

- Tier stack: FRED H.10 (Tier 1), BIS EER (Tier 1 macro), yfinance (Tier 4 prototype)
- Quality manifest: missing data, suspicious returns, source metadata
- Macro panel: US–MX rate spread, VIX, broad dollar index

## 4. Regime Classification

- Features: moving averages, realized vol percentile, returns
- Regimes R1–R4: trend/range × high/low vol
- Stability and interpretability for desk users

## 5. Empirical Methods

- Benchmarks: buy-and-hold, random walk (flat), legacy MA crossover
- Primary strategy: flat in high-vol range regimes (`flat_range`)
- Walk-forward: 5y train / 1y test
- Academic tests: DM, SPA/White RC where sample allows

## 6. Results

- Strategy scorecard (full sample and OOS)
- Random-walk validity map by regime
- Hedge governance: turnover vs risk reduction tradeoff
- Flow-pressure proxy tests (calendar seasonality)

## 7. Discussion

- When regime logic helps hedging even if forecasts fail
- Data tier implications for publication
- Corridor heterogeneity (US_MX vs US_CO vs US_IN)

## 8. Limitations

- No forward points, carry implementation, or executable spreads
- Calendar flow proxies ≠ proprietary payment flows
- Single-pair depth vs multi-corridor breadth tradeoff

## 9. Conclusion

- Conditional forecastability framing vs oracle claims
- Policy implications for treasury and cross-border payments desks

## Appendix A — Multi-Corridor Roadmap Tables  
## Appendix B — Model Cards and Reproducibility  
## Appendix C — Data Source Registry  

---

## Target Venues (aspirational)

- Central bank / FX workshop
- Financial econometrics seminar
- Industry treasury research forum (non-commercial)

---

## Replication Package

- Repository: Bowers Frontier Macro Labs FX Lab
- Scripts: `run_usdmxn_backtest.py`, `run_under_tested_research.py`, `run_data_quality_layer.py`
- Config: `config.yaml` with tier flags documented

---

*Outline only — fill empirical tables from latest pipeline run before circulation.*
"""
    path = REPORTS / "USDMXN_WORKING_PAPER_OUTLINE.md"
    path.write_text(body, encoding="utf-8")
    return path


def generate_investor_pilot_one_pager() -> Path:
    """Investor / pilot partner one-pager — research platform, not a fund pitch."""
    sc = _read_csv("strategy_scorecard.csv")
    hg = _read_csv("hedge_governance_scorecard.csv")
    corridor = _read_csv("corridor_master_scorecard.csv")

    best_strat = sc.loc[sc["sharpe"].idxmax(), "strategy"] if not sc.empty and "sharpe" in sc.columns else "flat_range"
    hg_us = hg[hg["exposure_type"] == "us_entity_long_mxn"] if "exposure_type" in hg.columns else hg
    best_hedge = (
        hg_us.loc[hg_us["cost_adjusted_risk_reduction"].idxmax(), "policy_name"]
        if not hg_us.empty and "cost_adjusted_risk_reduction" in hg_us.columns
        else "no_change_in_range"
    )

    n_corridors = len(corridor) if not corridor.empty else 5

    body = f"""# Bowers Frontier Macro Labs — FX Regime Intelligence

## Pilot / Research Partnership One-Pager

**Markets. Images. Materials. Systems.**

---

## What It Is

An **independent AI-assisted research platform** that tests when FX markets become conditionally forecastable — and when regime logic improves **hedge governance** even if directional forecasts fail.

**Not a fund. Not investment advice. Not live trading.**

---

## Problem

Cross-border payments and treasury teams face FX exposure across corridors (USD/MXN, USD/INR, USD/PHP, …). Naïve models either over-trade or ignore regime structure. Random-walk benchmarks are hard to beat unconditionally — but **conditional** structure may still matter for risk discipline.

---

## Solution (Prototype)

| Component | Description |
|-----------|-------------|
| Regime engine | R1–R4 trend/vol classification |
| Random-walk lab | Benchmarks every claim |
| Hedge governance | 8 policies; turnover vs risk reduction |
| Corridor roadmap | {n_corridors} corridors scored |
| Data-quality layer | Explicit Tier 1–4 source manifest |
| Desk memos | USD/MXN flagship + corridor scorecards |

---

## Flagship Evidence (USD/MXN)

- **Primary strategy tested:** `{best_strat}`
- **Best hedge governance policy (US long MXN):** `{best_hedge}`
- **Data policy:** Upgrade path from yfinance (Tier 4) → FRED H.10 / BIS (Tier 1)

---

## Pilot Use Cases (Research / Framing Only)

1. **Treasury hedge discipline** — when to avoid over-adjusting hedges in range regimes  
2. **Corridor risk ranking** — which payment corridors show stronger regime effects  
3. **Desk decision memos** — structured questions, not trade instructions  
4. **Data audit** — source tier and quality manifest for model governance  

---

## What We Are Not Claiming

- Unconditional FX predictability  
- Proprietary payment-flow alpha  
- Live execution or guaranteed returns  
- Affiliation with any bank, employer, or vendor  

---

## Ask (Pilot / Research)

- Feedback on regime taxonomy and desk workflow fit  
- Optional: anonymized corridor statistics for validation (subject to compliance)  
- Co-development of publication-grade data tier (FRED / professional feeds)  

---

## Contact

**Brendan Bowers · Bowers Frontier Macro Labs**  
Public site: https://brendanbowers1-bit.github.io/br3n-macro-lab/fx-lab.html

---

*Generated {datetime.now():%Y-%m-%d} · Refresh via `python scripts/generate_flagship_memo.py`*
"""
    path = REPORTS / "USDMXN_INVESTOR_ONE_PAGER.md"
    path.write_text(body, encoding="utf-8")
    return path


def generate_all_flagship_documents() -> Dict[str, Path]:
    return {
        "memo": generate_flagship_usdmxn_memo(),
        "working_paper": generate_working_paper_outline(),
        "investor": generate_investor_pilot_one_pager(),
    }

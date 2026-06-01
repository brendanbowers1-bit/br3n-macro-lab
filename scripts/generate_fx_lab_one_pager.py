#!/usr/bin/env python3
"""Build FX_LAB_ONE_PAGER.md from latest pipeline outputs."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "outputs"
PROC = ROOT / "data" / "processed"


def _read(name: str) -> pd.DataFrame:
    p = OUT / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def main() -> None:
    df = pd.read_csv(PROC / "usdmxn_features_regimes.csv", parse_dates=["date"]) if (
        PROC / "usdmxn_features_regimes.csv"
    ).exists() else pd.DataFrame()
    sc = _read("strategy_scorecard.csv")
    fc = _read("forecast_scorecard.csv")
    hg = _read("hedge_governance_scorecard.csv")
    dq = _read("data_quality_report.csv")
    corridor = _read("corridor_master_scorecard.csv")

    regime = df.iloc[-1]["regime"] if not df.empty and "regime" in df.columns else "—"
    best_strat = sc.loc[sc["sharpe"].idxmax(), "strategy"] if not sc.empty and "sharpe" in sc.columns else "—"
    best_sharpe = sc.loc[sc["sharpe"].idxmax(), "sharpe"] if not sc.empty and "sharpe" in sc.columns else "—"

    hg_us = hg[hg["exposure_type"] == "us_entity_long_mxn"] if "exposure_type" in hg.columns else hg
    best_hg = (
        hg_us.loc[hg_us["cost_adjusted_risk_reduction"].idxmax(), "policy_name"]
        if not hg_us.empty and "cost_adjusted_risk_reduction" in hg_us.columns
        else "—"
    )

    rw_status = "—"
    if not fc.empty and "beats_random_walk" in fc.columns:
        rw_status = "beats RW" if fc.iloc[0].get("beats_random_walk") else "does not beat RW"

    tier = dq.iloc[0].get("tier_label", "prototype") if not dq.empty else "prototype"
    quality = dq.iloc[0].get("data_quality_flag", "—") if not dq.empty else "—"
    n_corridors = len(corridor) if not corridor.empty else 0

    body = f"""# Bowers Frontier Macro Labs — FX Lab One-Pager

**Generated:** {datetime.now():%Y-%m-%d}  
**Flagship pair:** USD/MXN · **Latest regime:** {regime}

> Research and risk-framing only. Not investment advice. No live trading.

---

## 1. Research Question

**When do currency markets become less random?**

FX Lab tests whether exchange rates are mostly random-walk-like but **conditionally structured** when trend, volatility, carry, liquidity stress, and payment-flow pressure align.

---

## 2. Core Thesis

FX may be mostly random-walk-like unconditionally, but **conditionally forecastable** in specific regimes (R1–R4).

We do not claim universal predictability. We test conditional forecastability against honest benchmarks.

---

## 3. Three Scorecards

| Object | Question | Latest anchor |
|--------|----------|---------------|
| **Forecast scorecard** | Does the model beat random walk (RMSE, MAE, DM tests)? | {rw_status} |
| **Trading scorecard** | Does the strategy survive costs, drawdowns, walk-forward? | Best Sharpe: `{best_strat}` ({best_sharpe}) |
| **Hedge-governance scorecard** | Does regime logic improve cost-adjusted risk vs static hedges? | Best policy: `{best_hg}` |

A model may fail forecast tests and still improve hedge discipline.

---

## 4. Flagship Use Case

**USD/MXN** regime and hedge-governance research.

- Regimes: R1 trend+high vol · R2 trend+low vol · R3 range+high vol · R4 range+low vol
- Separation of trading alpha vs treasury hedge effectiveness
- Desk memos and FX Desk Command Center for decision framing

---

## 5. Corridor Roadmap

Expansion to major payment/remittance corridors ({n_corridors} in master scorecard):

- US_MX / USD/MXN
- US_IN / USD/INR
- US_PH / USD/PHP
- US_CO / USD/COP
- US_BR / USD/BRL

Corridor results are exploratory until rerun on official data tiers.

---

## 6. Academic Discipline

- Random-walk benchmark on every claim
- Out-of-sample and walk-forward testing
- Transaction costs on turnover
- Data-snooping awareness (White reality check where applicable)
- No holdout tuning for production claims

---

## 7. Data Standard

| Tier | Label | Current use |
|------|-------|-------------|
| 4 | Prototype | yfinance / Stooq (development) |
| 1 | Academic-grade | FRED, Fed H.10, BIS, central banks (publication target) |
| 2 | Trading-grade | Bloomberg, LSEG, bank quotes (execution research) |

**Current primary spot tier:** {tier} · **Quality flag:** {quality}

Prototype results must be rerun on Tier 1 before publication-grade claims.

---

## 8. Disclaimer

This is research and risk-framing only. It is not investment advice, does not guarantee returns, and is not intended for automated live trading.

Bowers Frontier Macro Labs is an independent research project — not affiliated with any employer, bank, or payment company unless explicitly stated.
"""
    path = ROOT / "reports" / "publication" / "FX_LAB_ONE_PAGER.md"
    path.write_text(body, encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()

#!/usr/bin/env python3
"""Generate reports/LAB_STATUS.md from latest lab outputs and dimension scores."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data_loader import load_config
from src.self_improve.scorer import score_all, overall_health


def _read_csv(name: str) -> pd.DataFrame | None:
    p = ROOT / "data" / "outputs" / name
    if p.exists():
        return pd.read_csv(p)
    return None


def _latest_run_summary() -> dict | None:
    p = ROOT / "data" / "runs" / "latest" / "summary.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def generate_lab_status_md(cfg: dict | None = None) -> str:
    cfg = cfg or load_config()
    scores = score_all(cfg)
    health = overall_health(scores)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    dq = _read_csv("data_quality_report.csv")
    cmp_df = _read_csv("data_source_comparison_usdmxn.csv")
    news_tests = _read_csv("news_feature_test_results.csv")
    carry_tests = _read_csv("carry_regime_test_results.csv")
    carry_hg = _read_csv("carry_hedge_governance_scorecard.csv")
    fc = _read_csv("model_zoo_forecast_scorecard.csv")
    tr = _read_csv("model_zoo_trading_scorecard.csv")
    hg = _read_csv("hedge_governance_scorecard.csv")
    sc = _read_csv("strategy_scorecard.csv")

    lines = [
        "# FX Lab Status",
        "",
        f"_Generated: {now}_",
        "",
        f"**Overall health:** `{health}`",
        "",
        "> Research-only. Not investment advice. No live trading.",
        "",
        "## Dimension scores",
        "",
        "| Dimension | Verdict | Detail |",
        "|-----------|---------|--------|",
    ]

    for s in scores:
        detail = str(s.get("detail", "")).replace("|", "/")[:120]
        lines.append(f"| {s['dimension']} | {s['verdict']} | {detail} |")

    lines.extend(["", "## Data layer", ""])

    if dq is not None and not dq.empty:
        r = dq.iloc[0]
        src = r.get("source", r.get("source_name", "unknown"))
        tier = r.get("tier_label", r.get("data_tier", "?"))
        flag = r.get("quality_flag", r.get("data_quality_flag", "?"))
        lines.append(f"- **Spot source:** {src} ({tier})")
        lines.append(f"- **Quality flag:** {flag}")
        lines.append(f"- **Observations:** {r.get('observation_count', '—')}")
        lines.append(f"- **Range:** {r.get('start_date', '—')} → {r.get('end_date', '—')}")
    else:
        lines.append("- Data quality report missing — run `python scripts/run_data_quality.py`")

    if cmp_df is not None and not cmp_df.empty:
        c = cmp_df.iloc[0]
        agree = c.get("agree_closely", "—")
        corr = c.get("daily_return_correlation", "—")
        lines.append(f"- **FRED vs yfinance correlation:** {corr} (agree closely: {agree})")

    lines.extend(["", "## News layer (regime/risk feature)", ""])
    carry_path = ROOT / "data" / "processed" / "usdmxn_features_regimes_news.csv"
    if carry_path.exists():
        lines.append("- News-enhanced features: **available**")
    else:
        lines.append("- News-enhanced features: **missing** — run `python scripts/run_news_layer.py`")

    if news_tests is not None and not news_tests.empty:
        hi = news_tests[news_tests["test_name"] == "high_vs_normal_news_stress"]
        if not hi.empty:
            h = hi.iloc[0]
            lines.append(
                f"- High-news vol: {h.get('volatility_high_news', '—')}% vs normal "
                f"{h.get('volatility_normal', '—')}%"
            )

    lines.extend(["", "## Carry layer (regime/risk feature)", ""])
    carry_feat = ROOT / "data" / "processed" / "usdmxn_features_regimes_carry.csv"
    if carry_feat.exists():
        cdf = pd.read_csv(carry_feat, parse_dates=["date"])
        latest = cdf.iloc[-1]
        lines.append("- Carry-enhanced features: **available**")
        if pd.notna(latest.get("carry_proxy")):
            lines.append(f"- Latest carry proxy: **{float(latest['carry_proxy']):.3f}**")
        lines.append(f"- High carry: {bool(latest.get('is_high_carry', False))}")
        lines.append(f"- Carry fragility: {bool(latest.get('carry_fragility_regime', False))}")
        lines.append(f"- Carry-adjusted regime: `{latest.get('carry_adjusted_regime', '—')}`")
        fwd = bool(latest.get("forward_data_available", False))
        lines.append(f"- Forward points: {'**available**' if fwd else '_proxy only (policy rates)_'}")
    else:
        lines.append("- Carry features: **missing** — run `python scripts/run_carry_layer.py`")

    if carry_tests is not None and not carry_tests.empty:
        hi = carry_tests[carry_tests["test_name"] == "high_carry_vs_low_carry"]
        if not hi.empty:
            h = hi.iloc[0]
            lines.append(
                f"- High-carry vol: {h.get('volatility_high_carry', '—')}% vs low-carry "
                f"{h.get('volatility_low_carry', '—')}%"
            )

    lines.extend(["", "## Model zoo", ""])
    if fc is not None and not fc.empty:
        beats = int(fc["model_beats_rw_rmse"].sum()) if "model_beats_rw_rmse" in fc.columns else 0
        lines.append(f"- Models beating random walk (RMSE): **{beats}** / {len(fc)}")
        if "source" in fc.columns and fc["source"].notna().any():
            lines.append(f"- Scorecard data source: `{fc['source'].iloc[0]}`")
    if tr is not None and not tr.empty and "sharpe_net" in tr.columns:
        best = tr.sort_values("sharpe_net", ascending=False).iloc[0]
        lines.append(f"- Best trading Sharpe (net): `{best['model_name']}` ({best['sharpe_net']})")

    lines.extend(["", "## Hedge governance", ""])
    if hg is not None and not hg.empty:
        us = hg[hg["exposure_type"] == "us_entity_long_mxn"] if "exposure_type" in hg.columns else hg
        if not us.empty and "cost_adjusted_risk_reduction" in us.columns:
            best = us.loc[us["cost_adjusted_risk_reduction"].idxmax()]
            lines.append(
                f"- Best policy (US entity long MXN): `{best.get('policy_name', '—')}` "
                f"(cost-adj risk reduction: {best.get('cost_adjusted_risk_reduction', '—')})"
            )

    if carry_hg is not None and not carry_hg.empty and "cost_adjusted_risk_reduction" in carry_hg.columns:
        ok = carry_hg[carry_hg.get("status", "ok") != "error"] if "status" in carry_hg.columns else carry_hg
        if not ok.empty:
            best = ok.loc[ok["cost_adjusted_risk_reduction"].idxmax()]
            lines.append(
                f"- Best carry-aware hedge policy: `{best.get('policy_name', '—')}` "
                f"({best.get('cost_adjusted_risk_reduction', '—')})"
            )

    lines.extend(["", "## Provenance (USD/MXN scorecard)", ""])
    if sc is not None and not sc.empty:
        row = sc.iloc[0]
        for col in ("source", "data_tier", "sample_start", "sample_end", "observations", "run_timestamp"):
            if col in sc.columns:
                lines.append(f"- {col}: `{row[col]}`")

    summary = _latest_run_summary()
    if summary and summary.get("proposals"):
        lines.extend(["", "## Proposed next experiments", ""])
        for i, p in enumerate(summary["proposals"][:5], 1):
            lines.append(f"{i}. **{p['dimension']}** — {p['proposed_action']}")
            lines.append(f"   - `{p['suggested_script']}`")

    lines.extend(
        [
            "",
            "## What still limits publication claims",
            "",
            "- Forward points and executable bid/ask not in default pipeline",
            "- Forecast models do not reliably beat random walk",
            "- News/carry layers need out-of-sample validation on holdout window",
            "- Level 8 institutional bar not fully cleared under forward_full costs",
            "",
            "## Commands",
            "",
            "```bash",
            "bash scripts/run_full_lab_pipeline.sh    # full nightly run",
            "python scripts/run_self_improvement.py --rerun",
            "bash scripts/auto_improve_daily.sh       # scheduled daily",
            "```",
            "",
        ]
    )

    return "\n".join(lines)


def write_lab_status(cfg: dict | None = None) -> Path:
    cfg = cfg or load_config()
    md = generate_lab_status_md(cfg)
    out = ROOT / "reports" / "LAB_STATUS.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    return out


def main() -> None:
    path = write_lab_status()
    print(f"Lab status written: {path}")


if __name__ == "__main__":
    main()

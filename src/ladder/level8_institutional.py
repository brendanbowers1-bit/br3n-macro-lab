"""
Level 8: Institutional proof requirements — external validity bar for hedge-governance claims.

Defines what must be demonstrated before upgrading from prototype to institutional-grade claims.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

# (requirement_id, requirement, pass_threshold, notes)
INSTITUTIONAL_REQUIREMENTS: List[tuple[str, str, str, str]] = [
    (
        "pairs",
        "Many currency pairs",
        ">= 10 pairs with hedge scorecards published",
        "Trading ladder covers ~19 pairs; hedge governance is USD/MXN only",
    ),
    (
        "decades",
        "Multiple decades",
        ">= 20 years per pair without survivorship gaps",
        "USD/MXN ~20–25y; not validated across full pair panel",
    ),
    (
        "official_data",
        "Official data",
        "Tier-1 spot (FRED H.10 or licensed feed) for all pairs in results",
        "FRED H.10 for USD/MXN when available; Yahoo fallback still in stack",
    ),
    (
        "forward_costs",
        "Real or realistic forward costs",
        "Forward points + roll in static vs dynamic hedge comparisons",
        "Turnover bps + spread/slippage/roll/carry assumptions only; no forward curve",
    ),
    (
        "static_vs_dynamic",
        "Static vs dynamic hedge policies",
        "Static benchmarks vs dynamic policies on same exposure and cost model",
        "Tested on USD/MXN: never/half/mostly/fully vs regime_based, no_change_in_range",
    ),
    (
        "transaction_costs",
        "Transaction costs",
        "All hedge and trading metrics net of explicit costs",
        "2 bps turnover + Level 5 frictions for trading; simplified hedge turnover charge",
    ),
    (
        "oos",
        "Out-of-sample tests",
        "Walk-forward OOS for hedge policies, not only trading signals",
        "Trading OOS (3 splits) exists; hedge headline result is full-sample USD/MXN",
    ),
    (
        "snooping",
        "Data-snooping controls",
        "Pre-registered hypotheses; White RC / SPA on policy set at p < 0.05",
        "White RC p ≈ 0.61 on trading strategies — does not reject data-mining",
    ),
    (
        "exposures",
        "Multiple corporate exposure types",
        ">= 3 exposure types with published scorecards",
        "Code supports receiver / US-long-MXN / USD-liability; published table is mostly one type",
    ),
]


def _count_multipair(root: Path) -> int:
    path = root / "reports" / "research_ladder" / "level3_multipair_oos.csv"
    if not path.exists():
        return 0
    df = pd.read_csv(path)
    if df.empty or "ticker" not in df.columns:
        return 0
    return int(df["ticker"].nunique())


def _legacy_hedge_pair_count(root: Path) -> int:
    path = root / "data" / "outputs" / "hedge_governance_scorecard.csv"
    if not path.exists():
        return 0
    df = pd.read_csv(path)
    if df.empty:
        return 0
    if "ticker" in df.columns:
        return int(df["ticker"].nunique())
    return 1


def _legacy_exposure_count(root: Path) -> int:
    path = root / "data" / "outputs" / "hedge_governance_scorecard.csv"
    if not path.exists():
        return 0
    df = pd.read_csv(path)
    if df.empty or "exposure_type" not in df.columns:
        return 0
    return int(df["exposure_type"].nunique())


def _hedge_oos_pair_count(root: Path) -> int:
    path = root / "reports" / "research_ladder" / "level8_hedge_oos_scorecard.csv"
    if not path.exists():
        return _legacy_hedge_pair_count(root)
    df = pd.read_csv(path)
    ok = df[df["status"] == "ok"] if "status" in df.columns else df
    if ok.empty or "ticker" not in ok.columns:
        return 0
    return int(ok["ticker"].nunique())


def _hedge_oos_exposure_count(root: Path) -> int:
    path = root / "reports" / "research_ladder" / "level8_hedge_oos_scorecard.csv"
    if not path.exists():
        return _legacy_exposure_count(root)
    df = pd.read_csv(path)
    ok = df[df["status"] == "ok"] if "status" in df.columns else df
    if ok.empty or "exposure_type" not in ok.columns:
        return 0
    return int(ok["exposure_type"].nunique())


def _hedge_oos_summary(root: Path) -> pd.DataFrame:
    path = root / "reports" / "research_ladder" / "level8_hedge_oos_summary.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _trading_white_rc_pvalue(root: Path) -> float | None:
    path = root / "reports" / "research_ladder" / "level6_white_reality_check.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    s = df[df["strategy"] == "_SUMMARY"]
    if s.empty:
        return None
    val = s.iloc[0].get("white_rc_pvalue")
    return float(val) if val is not None and not pd.isna(val) else None


def _hedge_white_rc_pvalue(root: Path, cost_layer: str = "forward_full") -> float | None:
    path = root / "reports" / "research_ladder" / "level8_hedge_white_rc.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if df.empty:
        return None
    panel = df[
        (df.get("test", "") == "panel_oos_metric_bootstrap")
        & (df.get("cost_layer", "") == cost_layer)
        & (df.get("policy_name", df.get("strategy", "")) == "_SUMMARY")
    ]
    if panel.empty and "strategy" in df.columns:
        panel = df[
            (df.get("test", "") == "flagship_daily_sharpe")
            & (df.get("cost_layer", "") == cost_layer)
            & (df["strategy"] == "_SUMMARY")
        ]
    if panel.empty:
        summaries = df[df.get("policy_name", pd.Series()) == "_SUMMARY"] if "policy_name" in df.columns else df[df["strategy"] == "_SUMMARY"]
        layer_sum = summaries[summaries.get("cost_layer", "") == cost_layer] if "cost_layer" in summaries.columns else summaries
        if layer_sum.empty:
            return None
        panel = layer_sum.iloc[[0]]
    val = panel.iloc[0].get("white_rc_pvalue")
    return float(val) if val is not None and not pd.isna(val) else None


def _assess_status(req_id: str, root: Path, cfg: dict) -> tuple[str, str]:
    """Return (evidence_status, current_state) for one requirement."""
    multipair = _count_multipair(root)
    hedge_pairs = _hedge_oos_pair_count(root)
    exposures = _hedge_oos_exposure_count(root)
    oos_summary = _hedge_oos_summary(root)
    wrc_p = _trading_white_rc_pvalue(root)
    hedge_wrc_p = _hedge_white_rc_pvalue(root, "forward_full")
    prefer_tier1 = bool(cfg.get("data", {}).get("prefer_tier1_spot", False))
    history_years = int(cfg.get("data", {}).get("history_years", 20))
    min_pairs = int(cfg.get("hedge_oos", {}).get("min_pairs", 10))

    if req_id == "pairs":
        if hedge_pairs >= min_pairs:
            return "Partial", f"{hedge_pairs} pairs with hedge OOS scorecards (target {min_pairs})"
        if hedge_pairs >= 1:
            return "Not met", f"Hedge OOS: {hedge_pairs} pair(s); target ≥ {min_pairs}"
        return "Not met", f"No hedge OOS scorecard; trading ladder: ~{multipair} pairs"

    if req_id == "decades":
        if history_years >= 20 and hedge_pairs >= 5:
            return "Partial", f"{history_years}y configured; multi-pair decades not validated"
        if history_years >= 20:
            return "Partial", f"~{history_years} years on flagship pair only"

    if req_id == "official_data":
        if prefer_tier1 and hedge_pairs >= 5:
            return "Partial", "Tier-1 preferred; not enforced across full hedge panel"
        if prefer_tier1:
            return "Partial", "FRED H.10 for USD/MXN; prototype fallback still possible"

    if req_id == "forward_costs":
        summary_path = root / "reports" / "research_ladder" / "level8_hedge_oos_summary.csv"
        if summary_path.exists():
            s = pd.read_csv(summary_path)
            ff = s[s["cost_layer"] == "forward_full"] if "cost_layer" in s.columns else s
            if not ff.empty and bool(ff.iloc[0].get("h8d_pass", False)):
                return "Partial", "Forward roll + carry layer run; H8d pass on OOS panel"
            if not ff.empty:
                h8d = ff.iloc[0].get("h8d_pass", False)
                return "Partial", f"Forward roll + carry layer run; H8d {'pass' if h8d else 'fail'}"
        return "Not met", "No forward cost layer in hedge OOS results"

    if req_id == "static_vs_dynamic":
        if hedge_pairs >= min_pairs:
            return "Partial", f"Static vs dynamic tested OOS on {hedge_pairs} pairs"
        if hedge_pairs >= 1:
            return "Partial", f"Static vs dynamic tested OOS on {hedge_pairs} pair(s)"
        return "Not met", "No hedge OOS scorecard on disk"

    if req_id == "transaction_costs":
        return "Partial", "Costs included but simplified (bps on hedge turnover)"

    if req_id == "oos":
        if not oos_summary.empty:
            ff = oos_summary[oos_summary["cost_layer"] == "forward_full"] if "cost_layer" in oos_summary.columns else pd.DataFrame()
            s = ff.iloc[0] if not ff.empty else oos_summary.iloc[0]
            pairs = int(s.get("pairs_tested", 0))
            h8a = bool(s.get("h8a_pass", False))
            h8d = bool(s.get("h8d_pass", False))
            layer = s.get("cost_layer", "base")
            if pairs >= min_pairs and h8a and h8d:
                return "Met", f"Hedge OOS ({layer}) on {pairs} pairs; H8a+H8d pass"
            if pairs >= min_pairs and h8a:
                return "Partial", (
                    f"Hedge OOS ({layer}) on {pairs} pairs; H8a pass ({s.get('pct_pairs_h8a')}%) "
                    f"but H8d {'pass' if h8d else 'fail'}"
                )
            if pairs >= min_pairs:
                return "Partial", (
                    f"Hedge OOS ({layer}) on {pairs} pairs; H8a "
                    f"{'pass' if h8a else 'fail'} ({s.get('pct_pairs_h8a')}%)"
                )
            if pairs >= 1:
                return "Partial", f"Hedge OOS started ({pairs} pairs); need ≥ {min_pairs}"
        return "Not met", "Hedge policies not yet run multi-pair OOS"

    if req_id == "snooping":
        if hedge_wrc_p is not None and hedge_wrc_p < 0.05:
            return "Partial", f"Hedge policy White RC p = {hedge_wrc_p:.4f} (forward_full)"
        if hedge_wrc_p is not None:
            return "Not met", f"Hedge policy White RC p = {hedge_wrc_p:.4f} — does not reject snooping"
        if wrc_p is not None and wrc_p < 0.05:
            return "Partial", f"Trading White RC p = {wrc_p:.4f} only (not hedge policy set)"
        if wrc_p is not None:
            return "Not met", f"Trading White RC p = {wrc_p:.4f}; hedge policy RC not run"
        return "Not met", "White Reality Check not run or missing"

    if req_id == "exposures":
        if exposures >= 3 and hedge_pairs >= min_pairs:
            return "Partial", f"{exposures} exposure types in hedge OOS panel ({hedge_pairs} pairs)"
        if exposures >= 3:
            return "Partial", f"{exposures} exposure types in hedge OOS; need ≥ {min_pairs} pairs"
        if exposures >= 1:
            return "Partial", f"{exposures} exposure type(s) in hedge OOS; need ≥ 3"
        return "Not met", "No exposure-type diversity in hedge OOS scorecards"

    return "Not met", "Not assessed"


def institutional_proof_matrix(root: Path | None = None, cfg: dict | None = None) -> pd.DataFrame:
    """Pass/fail matrix for Level 8 institutional proof requirements."""
    root = root or Path(__file__).resolve().parents[2]
    if cfg is None:
        from ..data_loader import load_config

        cfg = load_config()

    rows = []
    for req_id, requirement, pass_threshold, notes in INSTITUTIONAL_REQUIREMENTS:
        status, current = _assess_status(req_id, root, cfg)
        rows.append(
            {
                "requirement": requirement,
                "pass_threshold": pass_threshold,
                "evidence_status": status,
                "current_state": current,
                "design_notes": notes,
            }
        )
    return pd.DataFrame(rows)


def level8_overall_status(matrix: pd.DataFrame) -> str:
    """Single-line summary for ladder status table."""
    if matrix.empty:
        return "Not started"
    met = (matrix["evidence_status"] == "Met").sum()
    partial = (matrix["evidence_status"] == "Partial").sum()
    if met == len(matrix):
        return "Met — institutional bar cleared"
    if met == 0 and partial == 0:
        return "Not met — prototype only"
    return f"Not met — {met} met, {partial} partial, {len(matrix) - met - partial} failed"


def level8_preregistered_hypotheses() -> List[str]:
    """Pre-registered hypotheses for Level 8 upgrade path."""
    return [
        "H8a: `no_change_in_range` beats `regime_based` on cost-adjusted risk reduction OOS on >= 50% of pairs tested.",
        "H8b: Turnover reduction (no_change vs regime_based) >= 40% median across pairs without worse max drawdown hedged.",
        "H8c: Results replicate on Tier-1 spot only (no prototype fallback in published scorecards).",
        "H8d: Forward-point-adjusted hedge costs do not reverse the ranking of no_change vs static 50% / 75%.",
        "H8e: Best hedge policy survives White Reality Check on the pre-registered policy set (p < 0.05).",
        "H8f: At least three exposure types show consistent turnover discipline vs reactive regime hedging.",
    ]


def level8_upgrade_gate() -> str:
    """Plain-language gate before claim upgrade."""
    return (
        "Do **not** upgrade hedge-governance claims from prototype to institutional until **all nine** "
        "Level 8 requirements are **Met** (not Partial). Partial results may inform the research agenda only."
    )

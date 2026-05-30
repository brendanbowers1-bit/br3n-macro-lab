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


def _hedge_pair_count(root: Path) -> int:
    path = root / "data" / "outputs" / "hedge_governance_scorecard.csv"
    if not path.exists():
        return 0
    df = pd.read_csv(path)
    if df.empty:
        return 0
    if "ticker" in df.columns:
        return int(df["ticker"].nunique())
    return 1 if len(df) else 0


def _exposure_type_count(root: Path) -> int:
    path = root / "data" / "outputs" / "hedge_governance_scorecard.csv"
    if not path.exists():
        return 0
    df = pd.read_csv(path)
    if df.empty or "exposure_type" not in df.columns:
        return 0
    return int(df["exposure_type"].nunique())


def _white_rc_pvalue(root: Path) -> float | None:
    path = root / "reports" / "research_ladder" / "level6_white_reality_check.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    s = df[df["strategy"] == "_SUMMARY"]
    if s.empty:
        return None
    val = s.iloc[0].get("white_rc_pvalue")
    return float(val) if val is not None and not pd.isna(val) else None


def _assess_status(req_id: str, root: Path, cfg: dict) -> tuple[str, str]:
    """Return (evidence_status, current_state) for one requirement."""
    multipair = _count_multipair(root)
    hedge_pairs = _hedge_pair_count(root)
    exposures = _exposure_type_count(root)
    wrc_p = _white_rc_pvalue(root)
    prefer_tier1 = bool(cfg.get("data", {}).get("prefer_tier1_spot", False))
    history_years = int(cfg.get("data", {}).get("history_years", 20))

    if req_id == "pairs":
        if hedge_pairs >= 10:
            return "Met", f"{hedge_pairs} pairs with hedge scorecards"
        return "Not met", f"Hedge: {hedge_pairs} pair(s); trading ladder: ~{multipair} pairs"

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
        return "Not met", "No forward curve or bid/ask history in hedge scorecards"

    if req_id == "static_vs_dynamic":
        if hedge_pairs >= 1:
            return "Partial", f"Static vs dynamic tested on {max(hedge_pairs, 1)} pair(s), mostly full sample"
        return "Not met", "No hedge policy scorecard on disk"

    if req_id == "transaction_costs":
        return "Partial", "Costs included but simplified (bps on hedge turnover)"

    if req_id == "oos":
        return "Not met", "Hedge policies not yet walk-forward OOS; trading OOS exists"

    if req_id == "snooping":
        if wrc_p is not None and wrc_p < 0.05:
            return "Met", f"White RC p = {wrc_p:.4f}"
        if wrc_p is not None:
            return "Not met", f"White RC p = {wrc_p:.4f} — does not reject data-mining at 5%"
        return "Not met", "White Reality Check not run or missing"

    if req_id == "exposures":
        if exposures >= 3:
            return "Met", f"{exposures} exposure types in scorecard"
        if exposures >= 1:
            return "Partial", f"{exposures} exposure type(s) published; need >= 3"
        return "Not met", "No exposure-type diversity in published scorecards"

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

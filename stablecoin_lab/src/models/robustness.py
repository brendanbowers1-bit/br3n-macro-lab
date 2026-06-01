"""Robustness checks for Stablecoin Settlement Window Lab rankings."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _rank(df: pd.DataFrame, col: str, ascending: bool = False) -> pd.Series:
    if df.empty or col not in df.columns:
        return pd.Series(dtype=float)
    agg = df.groupby("entity", as_index=False)[col].mean().sort_values(col, ascending=ascending)
    agg["rank"] = range(1, len(agg) + 1)
    return agg.set_index("entity")["rank"]


def _spearman(r1: pd.Series, r2: pd.Series) -> float:
    common = r1.index.intersection(r2.index)
    if len(common) < 3:
        return float("nan")
    return float(r1.reindex(common).corr(r2.reindex(common), method="spearman"))


def _check(check_id: str, base: pd.Series, alt: pd.Series, notes: str = "") -> dict:
    sp = _spearman(base, alt)
    return {
        "check_id": check_id,
        "rank_stability_spearman": round(sp, 3) if not np.isnan(sp) else None,
        "robust": sp >= 0.85 if not np.isnan(sp) else False,
        "notes": notes or "Robust if Spearman rank correlation ≥ 0.85.",
    }


def run_robustness_checks(
    sfqi: pd.DataFrame,
    svsi: pd.DataFrame | None = None,
    csd: pd.DataFrame | None = None,
    swc: pd.DataFrame | None = None,
    dollarization: pd.DataFrame | None = None,
) -> pd.DataFrame:
    checks = []
    if sfqi.empty:
        return pd.DataFrame()

    base_rank = _rank(sfqi, "stablecoin_finality_quality_index")
    if base_rank.empty:
        return pd.DataFrame()

    observed = sfqi[sfqi.get("observed_vs_estimated_flag", "observed") != "estimated"] if "observed_vs_estimated_flag" in sfqi.columns else sfqi
    observed = observed[~observed.get("mock_data_flag", False)] if "mock_data_flag" in observed.columns else observed
    if len(observed) >= 3:
        checks.append(_check(
            "observed_official_data_only",
            base_rank,
            _rank(observed, "stablecoin_finality_quality_index"),
            "Restrict to non-mock, observed rows.",
        ))

    if "official_vs_manual_flag" in sfqi.columns:
        no_manual = sfqi[sfqi["official_vs_manual_flag"].astype(str).str.lower() != "manual"]
    else:
        no_manual = sfqi
    if len(no_manual) >= 3:
        checks.append(_check(
            "exclude_manual_assumptions",
            base_rank,
            _rank(no_manual, "stablecoin_finality_quality_index"),
            "Exclude manual assumption rows.",
        ))

    if dollarization is not None and not dollarization.empty and "entity" in sfqi.columns:
        sfqi_only = sfqi[~sfqi["entity"].isin(dollarization.get("entity", []))]
        if len(sfqi_only) >= 3:
            checks.append(_check(
                "exclude_dollarization_model",
                base_rank,
                _rank(sfqi_only, "stablecoin_finality_quality_index"),
                "SFQI ranking without dollarization entities.",
            ))

    no_trust = sfqi.copy()
    if "legal_enforceability_score" in no_trust.columns:
        no_trust["stablecoin_finality_quality_index"] = (
            no_trust["chain_finality_score"] * 0.15
            + no_trust.get("reserve_liquidity_score", 50) * 0.20
            + no_trust.get("redemption_reliability_score", 50) * 0.20
            + no_trust.get("off_ramp_reliability_score", 50) * 0.15
            + no_trust.get("compliance_finality_score", 50) * 0.15
            + no_trust.get("peg_stability_score", 50) * 0.15
        )
        checks.append(_check(
            "exclude_trust_legal_components",
            base_rank,
            _rank(no_trust, "stablecoin_finality_quality_index"),
            "Drop legal/freeze/interoperability weights.",
        ))

    if "ledger_finality_score" in sfqi.columns and "economic_finality_score" in sfqi.columns:
        checks.append(_check(
            "ledger_vs_economic_finality",
            _rank(sfqi, "ledger_finality_score"),
            _rank(sfqi, "economic_finality_score"),
            "Compare ledger vs economic finality rankings.",
        ))

    if svsi is not None and not svsi.empty and "stablecoin_vsi" in svsi.columns and "traditional_vsi" in svsi.columns:
        checks.append(_check(
            "stablecoin_vsi_vs_traditional_vsi",
            _rank(svsi, "stablecoin_vsi"),
            _rank(svsi, "traditional_vsi"),
            "Compare stablecoin vs traditional VSI corridor rankings.",
        ))

    hq = sfqi[sfqi["data_quality_score"] >= 70] if "data_quality_score" in sfqi.columns else sfqi
    if len(hq) >= 3:
        checks.append(_check(
            "high_quality_rows_only",
            base_rank,
            _rank(hq, "stablecoin_finality_quality_index"),
            "data_quality_score ≥ 70.",
        ))

    tier12 = sfqi[sfqi.get("credibility_tier", sfqi.get("data_quality_score", 99)) <= 2] if "credibility_tier" in sfqi.columns else sfqi
    if "source_id" in sfqi.columns:
        tier12 = sfqi[~sfqi["source_id"].astype(str).str.contains("MOCK|manual", case=False, na=False)]
    if len(tier12) >= 3:
        checks.append(_check(
            "tier1_tier2_sources_only",
            base_rank,
            _rank(tier12, "stablecoin_finality_quality_index"),
            "Exclude mock and manual source IDs.",
        ))

    wins = sfqi.copy()
    if "peg_deviation_bps" in wins.columns:
        cap = wins["peg_deviation_bps"].quantile(0.95)
        wins["peg_stability_score"] = 100 - wins["peg_deviation_bps"].clip(upper=cap) * 0.5
        wins["stablecoin_finality_quality_index"] = wins[[
            "chain_finality_score", "reserve_liquidity_score", "redemption_reliability_score",
            "legal_enforceability_score", "off_ramp_reliability_score", "compliance_finality_score",
            "peg_stability_score", "freeze_censorship_risk_score", "interoperability_score",
        ]].mean(axis=1)
        checks.append(_check(
            "winsorized_extreme_depeg_events",
            base_rank,
            _rank(wins, "stablecoin_finality_quality_index"),
            "Winsorize peg deviation at 95th percentile.",
        ))

    if "blockchain_network" in sfqi.columns:
        networks = sfqi["blockchain_network"].dropna().unique()
        for net in networks[:3]:
            sub = sfqi[sfqi["blockchain_network"] == net]
            if len(sub) >= 3:
                checks.append(_check(
                    f"separate_by_chain_{net.lower()}",
                    base_rank,
                    _rank(sub, "stablecoin_finality_quality_index"),
                    f"Ranking within {net} network only.",
                ))
                break

    if csd is not None and not csd.empty and "compliance_drag_index" in csd.columns:
        checks.append(_check(
            "compliance_drag_rank_stability",
            _rank(csd, "compliance_drag_index"),
            _rank(csd[csd.get("mock_data_flag", True) == False] if "mock_data_flag" in csd.columns else csd, "compliance_drag_index"),
            "Compliance drag index on non-mock subset.",
        ))

    if swc is not None and not swc.empty and "swc_extended" in swc.columns and "swc_core" in swc.columns:
        checks.append(_check(
            "swc_core_vs_extended",
            _rank(swc, "swc_core"),
            _rank(swc, "swc_extended"),
            "Compare SWC core vs extended specifications.",
        ))

    return pd.DataFrame(checks)

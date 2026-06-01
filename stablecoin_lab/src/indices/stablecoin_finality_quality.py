"""
Stablecoin Finality Quality Index (SFQI) — ledger vs economic finality.

Distinguishes chain confirmation from legal, redemption, compliance, and off-ramp finality.
Research-only. Not investment advice.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION

SFQI_WEIGHTS = {
    "chain_finality_score": 0.10,
    "reserve_liquidity_score": 0.15,
    "redemption_reliability_score": 0.15,
    "legal_enforceability_score": 0.15,
    "off_ramp_reliability_score": 0.10,
    "compliance_finality_score": 0.10,
    "peg_stability_score": 0.15,
    "freeze_censorship_risk_score": 0.05,
    "interoperability_score": 0.05,
}

SFQI_LIMITATIONS = (
    "SFQI separates ledger confirmation from economic finality. "
    "Blockchain confirmation does not imply legally or operationally final value. "
    + LAB_LIMITATIONS
)


def _clamp(score: float) -> float:
    return max(0.0, min(100.0, float(score)))


def _chain_score(confirmation_seconds: float, congestion: float = 0.0) -> float:
    secs = max(float(confirmation_seconds or 60), 0.1)
    base = 100 - min(40, secs / 60 * 10)
    return _clamp(base - float(congestion or 0) * 0.3)


def _peg_score(deviation_bps: float, volatility_bps: float = 0.0) -> float:
    dev = abs(float(deviation_bps or 0))
    vol = float(volatility_bps or 0)
    return _clamp(100 - dev * 0.5 - vol * 0.1)


def _risk_as_quality(risk_score: float) -> float:
    return _clamp(100 - float(risk_score or 30))


def calculate_stablecoin_finality_quality_row(row: pd.Series) -> dict:
    chain = _chain_score(
        row.get("average_confirmation_time_seconds", row.get("ledger_finality_seconds", 12)),
        row.get("congestion_score", 0),
    )
    reserve = _clamp(float(row.get("reserve_liquidity_score", 50) or 50))
    redemption_hours = float(row.get("estimated_redemption_time_hours", 24) or 24)
    redemption = _clamp(100 - min(50, redemption_hours / 24 * 20))
    if row.get("redemption_gate_flag"):
        redemption = _clamp(redemption - 25)
    legal = _clamp(float(row.get("legal_enforceability_score", row.get("legal_finality_score", 50)) or 50))
    off_ramp_hours = float(row.get("estimated_off_ramp_time_hours", 6) or 6)
    off_ramp = _clamp(100 - min(40, off_ramp_hours / 24 * 15))
    compliance_hours = float(row.get("compliance_delay_hours", 4) or 4)
    compliance = _clamp(100 - min(50, compliance_hours / 24 * 20))
    peg = _peg_score(
        row.get("peg_deviation_bps", row.get("max_intraday_deviation_bps", 5)),
        row.get("daily_volatility_bps", 0),
    )
    freeze_risk = float(row.get("freeze_censorship_risk_score", 20) or 20)
    if row.get("freeze_authority_flag"):
        freeze_risk = max(freeze_risk, 35)
    freeze = _risk_as_quality(freeze_risk)
    interoperability = _clamp(float(row.get("interoperability_score", 60) or 60))

    components = {
        "chain_finality_score": chain,
        "reserve_liquidity_score": reserve,
        "redemption_reliability_score": redemption,
        "legal_enforceability_score": legal,
        "off_ramp_reliability_score": off_ramp,
        "compliance_finality_score": compliance,
        "peg_stability_score": peg,
        "freeze_censorship_risk_score": freeze,
        "interoperability_score": interoperability,
    }
    sfqi = sum(components[k] * SFQI_WEIGHTS[k] for k in SFQI_WEIGHTS)

    ledger_secs = float(row.get("average_confirmation_time_seconds", row.get("ledger_finality_seconds", 12)) or 12)
    economic_hours = (
        ledger_secs / 3600
        + compliance_hours
        + off_ramp_hours
        + redemption_hours
        + float(row.get("legal_finality_hours", 0) or 0)
    )
    ledger_finality_score = chain
    economic_finality_score = _clamp(
        sfqi * 0.4
        + off_ramp * 0.2
        + redemption * 0.2
        + compliance * 0.1
        + legal * 0.1
    )

    if sfqi >= 85 and economic_finality_score >= 80:
        interp = "High economic finality (estimated)"
    elif sfqi >= 70 and ledger_finality_score >= 75:
        interp = "Ledger-final but institutionally dependent (estimated)"
    elif sfqi >= 55:
        interp = "Fragile finality (estimated)"
    else:
        interp = "Not final for economic purposes (estimated)"

    return {
        "stablecoin_finality_quality_index": _clamp(sfqi),
        "ledger_finality_score": _clamp(ledger_finality_score),
        "economic_finality_score": _clamp(economic_finality_score),
        "ledger_finality_seconds": ledger_secs,
        "effective_economic_finality_hours": economic_hours,
        **components,
        "interpretation": interp,
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": SFQI_LIMITATIONS,
        "data_quality_score": row.get("data_quality_score"),
        "mock_data_flag": row.get("mock_data_flag", False),
    }


def calculate_stablecoin_finality_quality_table(
    chain: pd.DataFrame,
    reserves: pd.DataFrame | None = None,
    redemption: pd.DataFrame | None = None,
    off_ramp: pd.DataFrame | None = None,
    peg: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if chain.empty and (peg is None or peg.empty):
        return pd.DataFrame()

    base = peg.copy() if peg is not None and not peg.empty else chain.copy()
    if base.empty:
        return pd.DataFrame()

    reserve_map = {}
    if reserves is not None and not reserves.empty:
        reserve_map = reserves.groupby("stablecoin")["reserve_liquidity_score"].mean().to_dict()

    redemption_map = {}
    if redemption is not None and not redemption.empty:
        redemption_agg = {
            k: v for k, v in {
                "estimated_redemption_time_hours": ("estimated_redemption_time_hours", "mean"),
                "redemption_gate_flag": ("redemption_gate_flag", "max"),
                "freeze_authority_flag": ("freeze_authority_flag", "max"),
                "legal_enforceability_score": ("legal_enforceability_score", "mean"),
            }.items() if v[0] in redemption.columns
        }
        if redemption_agg:
            redemption_map = redemption.groupby("stablecoin").agg(**redemption_agg).to_dict("index")

    off_ramp_map = {}
    if off_ramp is not None and not off_ramp.empty:
        off_ramp_agg = {
            k: v for k, v in {
                "estimated_off_ramp_time_hours": ("estimated_off_ramp_time_hours", "mean"),
                "compliance_delay_hours": ("compliance_delay_hours", "mean"),
                "off_ramp_reliability_score": ("off_ramp_reliability_score", "mean"),
            }.items() if v[0] in off_ramp.columns
        }
        if off_ramp_agg:
            off_ramp_map = off_ramp.groupby("stablecoin").agg(**off_ramp_agg).to_dict("index")

    chain_map = {}
    if not chain.empty:
        chain_map = chain.groupby("blockchain_network").agg(
            average_confirmation_time_seconds=("average_confirmation_time_seconds", "mean"),
            congestion_score=("congestion_score", "mean"),
        ).to_dict("index")

    rows = []
    for _, row in base.iterrows():
        stablecoin = row.get("stablecoin", "unknown")
        network = row.get("blockchain_network", "Ethereum")
        merged = row.to_dict()
        merged.update(reserve_map.get(stablecoin, {}) if isinstance(reserve_map.get(stablecoin), dict) else {
            "reserve_liquidity_score": reserve_map.get(stablecoin, merged.get("reserve_liquidity_score", 50)),
        })
        if stablecoin in redemption_map:
            merged.update(redemption_map[stablecoin])
        if stablecoin in off_ramp_map:
            merged.update(off_ramp_map[stablecoin])
        if network in chain_map:
            merged.update(chain_map[network])

        calc = calculate_stablecoin_finality_quality_row(pd.Series(merged))
        calc["entity"] = f"{stablecoin} | {network}"
        calc["entity_type"] = "stablecoin"
        calc["stablecoin"] = stablecoin
        calc["blockchain_network"] = network
        calc["source_id"] = row.get("source_id")
        rows.append({**merged, **calc})
    return pd.DataFrame(rows)

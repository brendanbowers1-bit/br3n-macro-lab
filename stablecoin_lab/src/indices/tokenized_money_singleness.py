"""
Tokenized Money Singleness Index — parity across private tokenized dollars.

Research-only. Not investment advice.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION

SINGLENESS_WEIGHTS = {
    "price_parity_score": 0.20,
    "redemption_parity_score": 0.15,
    "reserve_quality_score": 0.15,
    "legal_claim_score": 0.15,
    "liquidity_depth_score": 0.10,
    "interoperability_score": 0.10,
    "cb_money_convertibility_score": 0.10,
    "freeze_risk_score": 0.05,
}

SINGLENESS_LIMITATIONS = (
    "Singleness index compares tokenized dollar instruments under stated stress assumptions. "
    "Does not prove parity holds in live market stress without observed depeg events. "
    + LAB_LIMITATIONS
)


def _clamp(score: float) -> float:
    return max(0.0, min(100.0, float(score)))


def calculate_singleness_row(row: pd.Series) -> dict:
    peg_dev = abs(float(row.get("peg_deviation_bps", row.get("max_intraday_deviation_bps", 5)) or 5))
    price_parity = _clamp(100 - peg_dev * 0.8)
    redemption_hours = float(row.get("estimated_redemption_time_hours", 24) or 24)
    redemption_parity = _clamp(100 - min(40, redemption_hours / 24 * 15))
    reserve = _clamp(float(row.get("reserve_liquidity_score", row.get("reserve_quality_score", 50)) or 50))
    legal = _clamp(float(row.get("legal_claim_quality_score", row.get("legal_enforceability_score", 50)) or 50))
    depth = _clamp(float(row.get("liquidity_depth_score", row.get("exchange_liquidity_score", 60)) or 60))
    interoperability = _clamp(float(row.get("interoperability_score", 60) or 60))
    cb_convert = _clamp(float(row.get("central_bank_money_convertibility_score", 45) or 45))
    freeze_risk = float(row.get("freeze_censorship_risk_score", 20) or 20)
    freeze = _clamp(100 - freeze_risk)

    components = {
        "price_parity_score": price_parity,
        "redemption_parity_score": redemption_parity,
        "reserve_quality_score": reserve,
        "legal_claim_score": legal,
        "liquidity_depth_score": depth,
        "interoperability_score": interoperability,
        "cb_money_convertibility_score": cb_convert,
        "freeze_risk_score": freeze,
    }
    singleness = sum(components[k] * SINGLENESS_WEIGHTS[k] for k in SINGLENESS_WEIGHTS)
    singleness = _clamp(singleness)

    if singleness >= 85:
        interp = "Strong singleness (estimated)"
    elif singleness >= 70:
        interp = "Minor fragmentation (estimated)"
    elif singleness >= 55:
        interp = "Stressed singleness (estimated)"
    else:
        interp = "Fragmented token money (estimated)"

    return {
        "singleness_index": singleness,
        **components,
        "interpretation": interp,
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": SINGLENESS_LIMITATIONS,
        "data_quality_score": row.get("data_quality_score"),
        "mock_data_flag": row.get("mock_data_flag", False),
    }


def calculate_singleness_table(
    peg: pd.DataFrame,
    reserves: pd.DataFrame | None = None,
    redemption: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if peg.empty:
        return pd.DataFrame()

    reserve_map = {}
    if reserves is not None and not reserves.empty:
        reserve_map = reserves.groupby("stablecoin")["reserve_liquidity_score"].mean().to_dict()

    redemption_map = {}
    if redemption is not None and not redemption.empty:
        redemption_agg = {
            k: v for k, v in {
                "estimated_redemption_time_hours": ("estimated_redemption_time_hours", "mean"),
                "legal_enforceability_score": ("legal_enforceability_score", "mean"),
                "freeze_censorship_risk_score": ("freeze_censorship_risk_score", "mean"),
            }.items() if v[0] in redemption.columns
        }
        if redemption_agg:
            redemption_map = redemption.groupby("stablecoin").agg(**redemption_agg).to_dict("index")

    rows = []
    agg = peg.groupby("stablecoin", as_index=False).agg(
        peg_deviation_bps=("peg_deviation_bps", "mean"),
        max_intraday_deviation_bps=("max_intraday_deviation_bps", "mean"),
        daily_volatility_bps=("daily_volatility_bps", "mean"),
        data_quality_score=("data_quality_score", "mean"),
        data_quality_grade=("data_quality_grade", "first"),
        mock_data_flag=("mock_data_flag", "first"),
        source_id=("source_id", "first"),
    )
    for _, row in agg.iterrows():
        stablecoin = row["stablecoin"]
        merged = row.to_dict()
        merged["reserve_liquidity_score"] = reserve_map.get(stablecoin, 50)
        if stablecoin in redemption_map:
            merged.update(redemption_map[stablecoin])
        calc = calculate_singleness_row(pd.Series(merged))
        calc["entity"] = stablecoin
        calc["entity_type"] = "stablecoin"
        calc["stablecoin"] = stablecoin
        rows.append({**merged, **calc})
    return pd.DataFrame(rows)

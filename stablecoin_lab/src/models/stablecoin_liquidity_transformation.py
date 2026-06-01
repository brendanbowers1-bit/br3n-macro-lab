"""
Stablecoin Liquidity Transformation Model — user benefit vs issuer reserve burden.

Research-only. Not investment advice.
"""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import LAB_LIMITATIONS, METHODOLOGY_VERSION, RESERVE_LIQUIDITY_WEIGHT

SLT_LIMITATIONS = (
    "Liquidity transformation scores estimate how stablecoin transfer speed shifts "
    "liquidity needs from users to issuers and reserve markets. "
    + LAB_LIMITATIONS
)


def _clamp(score: float) -> float:
    return max(0.0, min(100.0, float(score)))


def calculate_liquidity_transformation_row(
    row: pd.Series,
    sensitivity_case: str = "baseline",
) -> dict:
    supply = float(row.get("stablecoin_supply_usd", row.get("supply_usd", 1e9)) or 1e9)
    reserve_liq = float(row.get("reserve_liquidity_score", 60) or 60)
    t_bill = float(row.get("treasury_bill_share", row.get("treasury_bills_usd", 0)) or 0)
    if t_bill > 1:
        total_res = float(row.get("total_reserves_usd", supply) or supply)
        t_bill = t_bill / max(total_res, 1)
    bank_dep = float(row.get("bank_deposit_share", 0.3) or 0.3)
    cash = float(row.get("cash_share", 0.1) or 0.1)
    repo = float(row.get("repo_share", 0.05) or 0.05)
    redemption_hours = float(row.get("estimated_redemption_time_hours", 24) or 24)
    concentration = float(row.get("redemption_concentration_risk", 0.3) or 0.3)
    rate_env = float(row.get("interest_rate_environment", 0.05) or 0.05)
    displacement = float(row.get("bank_deposit_displacement_proxy", 0.1) or 0.1)

    w = RESERVE_LIQUIDITY_WEIGHT[sensitivity_case]
    user_benefit = _clamp(85 - redemption_hours / 24 * 10 + (1 - displacement) * 10)
    issuer_burden = _clamp(
        (1 - reserve_liq / 100) * 50 * w
        + t_bill * 20
        + bank_dep * 15
        + concentration * 25
        + rate_env * 100 * 0.1
    )
    run_exposure = _clamp(concentration * 60 + (100 - reserve_liq) * 0.4 + redemption_hours / 24 * 5)
    reserve_concentration = _clamp(t_bill * 40 + repo * 20 + bank_dep * 15)
    transformation = _clamp(user_benefit - issuer_burden * 0.35 - run_exposure * 0.15 + 35)

    if transformation >= 70:
        interp = "User liquidity benefit dominates issuer burden (estimated)"
    elif transformation >= 50:
        interp = "Balanced liquidity transformation (estimated)"
    elif transformation >= 35:
        interp = "Issuer reserve burden elevated (estimated)"
    else:
        interp = "Liquidity risk relocated to issuer/reserve markets (estimated)"

    return {
        "user_liquidity_benefit_score": user_benefit,
        "issuer_reserve_burden_score": issuer_burden,
        "redemption_run_exposure_score": run_exposure,
        "reserve_market_concentration_score": reserve_concentration,
        "stablecoin_liquidity_transformation_score": transformation,
        "stablecoin_supply_usd": supply,
        "treasury_bill_share": t_bill,
        "bank_deposit_share": bank_dep,
        "cash_share": cash,
        "repo_share": repo,
        "interpretation": interp,
        "sensitivity_case": sensitivity_case,
        "methodology_version": METHODOLOGY_VERSION,
        "limitations": SLT_LIMITATIONS,
        "data_quality_score": row.get("data_quality_score"),
        "mock_data_flag": row.get("mock_data_flag", False),
    }


def calculate_liquidity_transformation_table(
    supply: pd.DataFrame,
    reserves: pd.DataFrame | None = None,
    redemption: pd.DataFrame | None = None,
    sensitivity_case: str = "baseline",
) -> pd.DataFrame:
    if supply.empty:
        return pd.DataFrame()

    reserve_map = {}
    if reserves is not None and not reserves.empty:
        reserve_map = reserves.groupby("stablecoin").agg(
            total_reserves_usd=("total_reserves_usd", "mean"),
            treasury_bills_usd=("treasury_bills_usd", "mean"),
            bank_deposits_usd=("bank_deposits_usd", "mean"),
            cash_usd=("cash_usd", "mean"),
            repo_usd=("repo_usd", "mean"),
            reserve_liquidity_score=("reserve_liquidity_score", "mean"),
        ).to_dict("index")

    redemption_map = {}
    if redemption is not None and not redemption.empty:
        redemption_map = redemption.groupby("stablecoin")["estimated_redemption_time_hours"].mean().to_dict()

    rows = []
    agg = supply.groupby("stablecoin", as_index=False).agg(
        supply_usd=("supply_usd", "sum"),
        data_quality_score=("data_quality_score", "mean"),
        data_quality_grade=("data_quality_grade", "first"),
        mock_data_flag=("mock_data_flag", "first"),
        source_id=("source_id", "first"),
    )
    for _, row in agg.iterrows():
        stablecoin = row["stablecoin"]
        merged = row.to_dict()
        if stablecoin in reserve_map:
            r = reserve_map[stablecoin]
            merged.update(r)
            total = r.get("total_reserves_usd", merged["supply_usd"]) or merged["supply_usd"]
            merged["treasury_bill_share"] = r.get("treasury_bills_usd", 0) / max(total, 1)
            merged["bank_deposit_share"] = r.get("bank_deposits_usd", 0) / max(total, 1)
            merged["cash_share"] = r.get("cash_usd", 0) / max(total, 1)
            merged["repo_share"] = r.get("repo_usd", 0) / max(total, 1)
        if stablecoin in redemption_map:
            merged["estimated_redemption_time_hours"] = redemption_map[stablecoin]
        calc = calculate_liquidity_transformation_row(pd.Series(merged), sensitivity_case)
        calc["entity"] = stablecoin
        calc["entity_type"] = "stablecoin"
        calc["stablecoin"] = stablecoin
        rows.append({**merged, **calc})
    return pd.DataFrame(rows)

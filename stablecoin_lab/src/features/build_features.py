"""Stablecoin Settlement Window Lab feature engineering."""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import METHODOLOGY_VERSION, MOCK_SOURCE_ID


def build_all_features(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    supply = tables.get("stablecoin_supply", pd.DataFrame())
    peg = tables.get("stablecoin_price_peg", pd.DataFrame())
    reserves = tables.get("stablecoin_reserves", pd.DataFrame())
    chain = tables.get("blockchain_settlement_characteristics", pd.DataFrame())
    redemption = tables.get("stablecoin_redemption_characteristics", pd.DataFrame())
    off_ramp = tables.get("off_ramp_characteristics", pd.DataFrame())
    remittance = tables.get("remittance_comparison", pd.DataFrame())
    macro = tables.get("macro", pd.DataFrame())
    regulatory = tables.get("regulatory_events", pd.DataFrame())

    if supply.empty and remittance.empty:
        return pd.DataFrame()

    frames = []

    if not supply.empty:
        s = supply.groupby(["stablecoin", "blockchain_network"], as_index=False).agg(
            supply_usd=("supply_usd", "sum"),
            market_cap_usd=("market_cap_usd", "mean"),
            mock_data_flag=("mock_data_flag", "first"),
            data_quality_score=("data_quality_score", "mean"),
            source_id=("source_id", "first"),
        )
        s["entity_type"] = "stablecoin_network"
        s["entity"] = s["stablecoin"] + " | " + s["blockchain_network"]
        frames.append(s)

    if not remittance.empty:
        r = remittance.copy()
        r["entity_type"] = "corridor"
        r["entity"] = r.get("corridor", r["sender_country"].astype(str) + "→" + r["receiver_country"].astype(str))
        r["traditional_settlement_window_hours"] = r.get("traditional_transfer_speed_days", 2) * 24
        frames.append(r)

    if not frames:
        return pd.DataFrame()

    f = pd.concat(frames, ignore_index=True, sort=False)

    if not peg.empty and "stablecoin" in peg.columns:
        peg_agg_cols = {
            k: v for k, v in {
                "peg_deviation_bps": ("peg_deviation_bps", "mean"),
                "max_intraday_deviation_bps": ("max_intraday_deviation_bps", "mean"),
                "daily_volatility_bps": ("daily_volatility_bps", "mean"),
                "depeg_event_flag": ("depeg_event_flag", "max"),
            }.items() if v[0] in peg.columns
        }
        if peg_agg_cols:
            peg_agg = peg.groupby("stablecoin", as_index=False).agg(**peg_agg_cols)
            f = f.merge(peg_agg, on="stablecoin", how="left")

    if not reserves.empty and "stablecoin" in reserves.columns:
        res_agg_cols = {
            k: v for k, v in {
                "total_reserves_usd": ("total_reserves_usd", "mean"),
                "reserve_liquidity_score": ("reserve_liquidity_score", "mean"),
                "treasury_bills_usd": ("treasury_bills_usd", "mean"),
                "bank_deposits_usd": ("bank_deposits_usd", "mean"),
            }.items() if v[0] in reserves.columns
        }
        if res_agg_cols:
            res_agg = reserves.groupby("stablecoin", as_index=False).agg(**res_agg_cols)
            f = f.merge(res_agg, on="stablecoin", how="left")

    if not chain.empty and "blockchain_network" in chain.columns:
        chain_agg_cols = {
            k: v for k, v in {
                "average_confirmation_time_seconds": ("average_confirmation_time_seconds", "mean"),
                "ledger_finality_seconds": ("average_confirmation_time_seconds", "mean"),
                "median_transaction_fee_usd": ("median_transaction_fee_usd", "mean"),
                "congestion_score": ("congestion_score", "mean"),
                "outage_flag": ("outage_flag", "max"),
            }.items() if v[0] in chain.columns
        }
        if chain_agg_cols and "blockchain_network" in f.columns:
            chain_agg = chain.groupby("blockchain_network", as_index=False).agg(**chain_agg_cols)
            f = f.merge(chain_agg, on="blockchain_network", how="left")

    if not redemption.empty and "stablecoin" in redemption.columns:
        red_agg_cols = {
            k: v for k, v in {
                "estimated_redemption_time_hours": ("estimated_redemption_time_hours", "mean"),
                "redemption_gate_flag": ("redemption_gate_flag", "max"),
                "freeze_authority_flag": ("freeze_authority_flag", "max"),
                "legal_enforceability_score": ("legal_enforceability_score", "mean"),
            }.items() if v[0] in redemption.columns
        }
        if red_agg_cols:
            red_agg = redemption.groupby("stablecoin", as_index=False).agg(**red_agg_cols)
            f = f.merge(red_agg, on="stablecoin", how="left", suffixes=("", "_red"))

    if not off_ramp.empty:
        off_group = [k for k in ["corridor", "stablecoin"] if k in off_ramp.columns]
        off_agg_cols = {
            k: v for k, v in {
                "estimated_off_ramp_time_hours": ("estimated_off_ramp_time_hours", "mean"),
                "compliance_delay_hours": ("compliance_delay_hours", "mean"),
                "off_ramp_fee_pct": ("off_ramp_fee_pct", "mean"),
                "kyc_required_flag": ("kyc_required_flag", "max"),
            }.items() if v[0] in off_ramp.columns
        }
        if off_group and off_agg_cols:
            off_agg = off_ramp.groupby(off_group, as_index=False).agg(**off_agg_cols)
            merge_keys = [k for k in off_group if k in f.columns]
            if merge_keys:
                f = f.merge(off_agg, on=merge_keys, how="left", suffixes=("", "_off"))

    if not macro.empty:
        macro_latest = macro.sort_values("date").groupby("country", as_index=False).tail(1)
        macro_cols = [c for c in ["country", "local_inflation_yoy", "inflation_yoy", "local_fx_volatility_30d",
                                   "fx_volatility_30d", "bank_account_access_pct", "account_ownership_pct"] if c in macro_latest.columns]
        if macro_cols:
            country_col = "receiver_country" if "receiver_country" in f.columns else "country"
            if country_col in f.columns:
                f = f.merge(
                    macro_latest.rename(columns={"country": country_col}),
                    on=country_col,
                    how="left",
                    suffixes=("", "_macro"),
                )

    if not regulatory.empty and "stablecoin" in regulatory.columns:
        reg_agg_cols = {}
        if "severity_score" in regulatory.columns:
            reg_agg_cols["regulatory_severity_score"] = ("severity_score", "mean")
        if "event_id" in regulatory.columns:
            reg_agg_cols["regulatory_event_count"] = ("event_id", "count")
        if reg_agg_cols:
            reg_agg = regulatory.groupby("stablecoin", as_index=False).agg(**reg_agg_cols)
            f = f.merge(reg_agg, on="stablecoin", how="left")

    if "stablecoin_effective_finality_hours" in f.columns:
        f["effective_economic_finality_hours"] = f["stablecoin_effective_finality_hours"]
    elif "compliance_delay_hours" in f.columns:
        ledger = f.get("average_confirmation_time_seconds", pd.Series(12, index=f.index)) / 3600
        f["effective_economic_finality_hours"] = (
            ledger
            + f.get("compliance_delay_hours", 0).fillna(0)
            + f.get("estimated_off_ramp_time_hours", 0).fillna(0)
            + f.get("estimated_redemption_time_hours", 0).fillna(0)
        )

    if "traditional_fee_pct" in f.columns and "stablecoin_offramp_fee_pct" in f.columns:
        trad_loss = f["traditional_fee_pct"].fillna(0) + f.get("traditional_fx_margin_pct", 0).fillna(0)
        sc_loss = (
            f.get("stablecoin_onramp_fee_pct", 0).fillna(0)
            + f.get("stablecoin_chain_fee_pct", 0).fillna(0)
            + f.get("stablecoin_offramp_fee_pct", 0).fillna(0)
            + f.get("stablecoin_fx_spread_pct", 0).fillna(0)
        )
        f["traditional_vsi"] = (100 * (1 - trad_loss.clip(upper=0.5))).clip(0, 100)
        f["stablecoin_vsi"] = (100 * (1 - sc_loss.clip(upper=0.5))).clip(0, 100)
        f["stablecoin_advantage_score"] = (f["stablecoin_vsi"] - f["traditional_vsi"] + 50).clip(0, 100)

    f["methodology_version"] = METHODOLOGY_VERSION
    f["source_id"] = f.get("source_id", MOCK_SOURCE_ID)
    if "mock_data_flag" not in f.columns:
        f["mock_data_flag"] = True
    if "data_quality_grade" not in f.columns:
        f["data_quality_grade"] = "Demo only"
    return f

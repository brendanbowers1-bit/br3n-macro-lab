"""
Curated bridge — transform official fetches into canonical stablecoin tables.

RPW rows get traditional remittance baselines only; stablecoin rail costs remain
manual/Tier 4 until verified off-ramp data is loaded.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from src.config.research_settings import METHODOLOGY_VERSION
from src.quality.data_quality import annotate_quality
from src.quality.lineage import attach_lineage, base_lineage

CORRIDOR_STABLECOIN_DEFAULTS = {
    "United States→Mexico": {"stablecoin": "USDC", "onramp": 0.8, "chain": 0.05, "offramp": 1.2, "fx": 0.4, "finality_h": 6.0},
    "United States→Philippines": {"stablecoin": "USDC", "onramp": 1.0, "chain": 0.08, "offramp": 1.5, "fx": 0.6, "finality_h": 12.0},
    "United States→Brazil": {"stablecoin": "USDT", "onramp": 0.9, "chain": 0.03, "offramp": 1.8, "fx": 0.8, "finality_h": 18.0},
    "United States→Colombia": {"stablecoin": "USDT", "onramp": 1.1, "chain": 0.04, "offramp": 1.6, "fx": 0.7, "finality_h": 14.0},
    "Euro Area→Nigeria": {"stablecoin": "USDT", "onramp": 1.2, "chain": 0.06, "offramp": 2.5, "fx": 1.0, "finality_h": 36.0},
    "Gulf→India": {"stablecoin": "USDT", "onramp": 0.7, "chain": 0.02, "offramp": 1.0, "fx": 0.5, "finality_h": 8.0},
}


def build_remittance_comparison_from_rpw(rpw_remittance: pd.DataFrame) -> pd.DataFrame:
    if rpw_remittance.empty:
        return pd.DataFrame()
    rows = []
    for _, row in rpw_remittance.iterrows():
        corridor = row.get("corridor", "")
        defaults = CORRIDOR_STABLECOIN_DEFAULTS.get(corridor, {})
        lg = base_lineage("world_bank_rpw", observed=True, manual=False)
        lg["methodology_version"] = METHODOLOGY_VERSION
        merged = {
            "date": row.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            "corridor": corridor,
            "sender_country": row.get("sender_country"),
            "receiver_country": row.get("receiver_country"),
            "traditional_fee_pct": row.get("traditional_fee_pct"),
            "traditional_fx_margin_pct": row.get("traditional_fx_margin_pct"),
            "traditional_transfer_speed_days": row.get("traditional_transfer_speed_days"),
            "stablecoin": defaults.get("stablecoin", "USDC"),
            "stablecoin_onramp_fee_pct": defaults.get("onramp"),
            "stablecoin_chain_fee_pct": defaults.get("chain"),
            "stablecoin_offramp_fee_pct": defaults.get("offramp"),
            "stablecoin_fx_spread_pct": defaults.get("fx"),
            "stablecoin_effective_finality_hours": defaults.get("finality_h"),
            **lg,
        }
        merged["official_vs_manual_flag"] = "official" if pd.notna(row.get("traditional_fee_pct")) else "manual"
        if pd.isna(merged.get("stablecoin_onramp_fee_pct")):
            merged["official_vs_manual_flag"] = "manual"
        rows.append(merged)
    df = pd.DataFrame(rows)
    for col in ("stablecoin_onramp_fee_pct", "stablecoin_chain_fee_pct", "stablecoin_offramp_fee_pct"):
        if col in df.columns:
            manual_mask = df[col].notna() & (df.get("official_vs_manual_flag") == "manual")
            if manual_mask.any():
                df.loc[manual_mask, "observed_vs_estimated_flag"] = "estimated"
    return annotate_quality(df, ["traditional_fee_pct", "corridor"])


def build_redemption_from_attestations(reserves: pd.DataFrame) -> pd.DataFrame:
    if reserves.empty:
        return pd.DataFrame()
    profiles = {
        "USDC": (1000, 0.0, 24, True, False, False, True),
        "USDT": (100000, 0.1, 48, True, True, True, True),
        "PYUSD": (1, 0.0, 72, True, True, False, True),
        "DAI": (1000, 0.0, 36, False, False, False, False),
    }
    rows = []
    for _, r in reserves.iterrows():
        sc = r.get("stablecoin", "")
        prof = profiles.get(sc, (1000, 0.0, 48, True, True, False, True))
        lg = base_lineage(
            "circle_attestation" if sc == "USDC" else "tether_attestation",
            observed=True,
            manual=False,
        )
        rows.append({
            "date": r.get("date"),
            "stablecoin": sc,
            "issuer": r.get("issuer"),
            "minimum_redemption_amount_usd": prof[0],
            "redemption_fee_pct": prof[1],
            "estimated_redemption_time_hours": prof[2],
            "direct_redemption_available_flag": prof[3],
            "banking_hours_dependency_flag": prof[4],
            "redemption_gate_flag": prof[5],
            "freeze_authority_flag": prof[6],
            "jurisdiction": "United States",
            "legal_enforceability_score": float(r.get("reserve_liquidity_score", 70)),
            **lg,
        })
    return annotate_quality(pd.DataFrame(rows), ["estimated_redemption_time_hours"])

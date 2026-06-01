"""Strictly labeled synthetic demo data for Stablecoin Settlement Window Lab."""

from __future__ import annotations

import warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from src.config.research_settings import MOCK_MAX_QUALITY_SCORE, MOCK_SOURCE_ID
from src.quality.data_quality import annotate_quality
from src.quality.lineage import base_lineage

STABLECOINS = [
    ("USDC", "USDC", "Circle"),
    ("USDT", "USDT", "Tether"),
    ("PYUSD", "PYUSD", "PayPal"),
    ("DAI", "DAI", "MakerDAO"),
    ("tokenized_bank_deposit_placeholder", "TBD", "Placeholder Bank"),
]

NETWORKS = [
    ("Ethereum", 2.5, 12, 900, 0.02),
    ("Solana", 0.002, 0.4, 30, 0.05),
    ("Tron", 0.001, 3, 60, 0.03),
    ("Base", 0.05, 2, 120, 0.04),
    ("Polygon", 0.02, 2, 180, 0.06),
    ("Arbitrum", 0.08, 1, 150, 0.05),
]

CORRIDORS = [
    ("US → Mexico", "United States", "Mexico"),
    ("US → Philippines", "United States", "Philippines"),
    ("US → Brazil", "United States", "Brazil"),
    ("US → Colombia", "United States", "Colombia"),
    ("Euro Area → Nigeria", "Euro Area", "Nigeria"),
    ("Gulf → India", "United Arab Emirates", "India"),
]

MOCK_WARNING = (
    "⚠️ DEMO MODE: Synthetic stablecoin data only. "
    "Do not use for research conclusions, investment decisions, or operational treasury guidance."
)


def _mock_lineage(blockchain_network: str = "", jurisdiction: str = "") -> dict:
    lg = base_lineage(
        MOCK_SOURCE_ID,
        mock_data_flag=True,
        observed=False,
        blockchain_network=blockchain_network,
        jurisdiction=jurisdiction,
    )
    lg["data_quality_score"] = MOCK_MAX_QUALITY_SCORE
    lg["data_quality_grade"] = "Demo only"
    lg["missing_data_pct"] = 0.0
    lg["imputation_flag"] = False
    lg["outlier_flag"] = False
    lg["unit_of_measure"] = "USD"
    lg["currency"] = "USD"
    lg["time_zone"] = "UTC"
    lg["date_granularity"] = "daily"
    return lg


def create_stablecoin_supply(n_days: int = 60) -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    rows = []
    base = datetime(2024, 10, 1)
    for stablecoin, ticker, issuer in STABLECOINS:
        base_supply = {
            "USDC": 35e9,
            "USDT": 110e9,
            "PYUSD": 0.8e9,
            "DAI": 5e9,
            "tokenized_bank_deposit_placeholder": 2e9,
        }[stablecoin]
        for network_name, *_ in NETWORKS:
            share = {"Ethereum": 0.35, "Solana": 0.12, "Tron": 0.28, "Base": 0.08,
                     "Polygon": 0.09, "Arbitrum": 0.08}.get(network_name, 0.1)
            for i in range(n_days):
                dt = base + timedelta(days=i)
                drift = 1 + np.random.normal(0, 0.002)
                supply = base_supply * share * drift
                rows.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "stablecoin": stablecoin,
                    "ticker": ticker,
                    "issuer": issuer,
                    "blockchain_network": network_name,
                    "supply_usd": supply,
                    "market_cap_usd": supply * np.random.uniform(0.998, 1.002),
                    "circulating_supply": supply,
                    **_mock_lineage(network_name),
                })
    return annotate_quality(pd.DataFrame(rows), ["supply_usd", "stablecoin"])


def create_stablecoin_price_peg(n_days: int = 60) -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    rows = []
    base = datetime(2024, 10, 1)
    for stablecoin, ticker, _ in STABLECOINS:
        peg_noise = 3 if stablecoin == "DAI" else 1.5 if stablecoin == "USDT" else 0.8
        for i in range(n_days):
            dt = base + timedelta(days=i)
            dev = np.random.normal(0, peg_noise)
            price = 1.0 + dev / 10000
            rows.append({
                "timestamp": dt.isoformat(),
                "date": dt.strftime("%Y-%m-%d"),
                "stablecoin": stablecoin,
                "ticker": ticker,
                "price_usd": price,
                "peg_deviation_bps": dev,
                "max_intraday_deviation_bps": abs(dev) + np.random.uniform(0, 5),
                "daily_volatility_bps": np.random.uniform(2, 15) + abs(dev),
                "depeg_event_flag": abs(dev) > 50,
                **_mock_lineage(),
            })
    return annotate_quality(pd.DataFrame(rows), ["price_usd", "peg_deviation_bps"])


def create_stablecoin_reserves() -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    rows = []
    profiles = {
        "USDC": (40e9, 0.08, 0.12, 0.72, 0.05, 0.0, 0.03, 92),
        "USDT": (115e9, 0.05, 0.10, 0.55, 0.20, 0.05, 0.05, 78),
        "PYUSD": (0.9e9, 0.15, 0.25, 0.55, 0.0, 0.0, 0.05, 85),
        "DAI": (5.2e9, 0.02, 0.05, 0.35, 0.15, 0.10, 0.33, 70),
        "tokenized_bank_deposit_placeholder": (2.1e9, 0.20, 0.65, 0.10, 0.0, 0.0, 0.05, 88),
    }
    for stablecoin, ticker, issuer in STABLECOINS:
        total, cash, bank, tbill, repo, cp, other, liq = profiles[stablecoin]
        rows.append({
            "date": "2024-12-01",
            "stablecoin": stablecoin,
            "issuer": issuer,
            "total_reserves_usd": total,
            "cash_usd": total * cash,
            "bank_deposits_usd": total * bank,
            "treasury_bills_usd": total * tbill,
            "repo_usd": total * repo,
            "commercial_paper_usd": total * cp,
            "other_assets_usd": total * other,
            "reserve_liquidity_score": liq,
            "attestation_provider": "Synthetic Auditor LLC",
            "attestation_date": "2024-11-30",
            **_mock_lineage(jurisdiction="United States"),
        })
    return annotate_quality(pd.DataFrame(rows), ["total_reserves_usd"])


def create_blockchain_settlement_characteristics(n_days: int = 30) -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    rows = []
    base = datetime(2024, 10, 1)
    for network_name, fee, conf, econ, congestion in NETWORKS:
        for i in range(n_days):
            dt = base + timedelta(days=i)
            noise = np.random.uniform(0.85, 1.15)
            rows.append({
                "date": dt.strftime("%Y-%m-%d"),
                "blockchain_network": network_name,
                "average_transaction_fee_usd": fee * noise,
                "median_transaction_fee_usd": fee * noise * 0.9,
                "average_confirmation_time_seconds": conf * noise,
                "probabilistic_finality_seconds": conf * 32 if network_name == "Ethereum" else conf * 5,
                "economic_finality_assumption_seconds": econ,
                "outage_flag": np.random.random() < 0.01,
                "congestion_score": min(congestion * 100 * noise, 100),
                **_mock_lineage(network_name),
            })
    return annotate_quality(pd.DataFrame(rows), ["average_transaction_fee_usd"])


def create_stablecoin_redemption_characteristics() -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    rows = []
    redemption_profiles = {
        "USDC": (1000, 0.0, 24, True, False, False, True),
        "USDT": (100000, 0.1, 48, True, True, True, True),
        "PYUSD": (1, 0.0, 72, True, True, False, True),
        "DAI": (1000, 0.0, 36, False, False, False, False),
        "tokenized_bank_deposit_placeholder": (1, 0.0, 4, True, True, False, True),
    }
    for stablecoin, ticker, issuer in STABLECOINS:
        min_amt, fee, hours, direct, bank_hrs, gate, freeze = redemption_profiles[stablecoin]
        rows.append({
            "date": "2024-12-01",
            "stablecoin": stablecoin,
            "issuer": issuer,
            "minimum_redemption_amount_usd": min_amt,
            "redemption_fee_pct": fee,
            "estimated_redemption_time_hours": hours,
            "direct_redemption_available_flag": direct,
            "banking_hours_dependency_flag": bank_hrs,
            "redemption_gate_flag": gate,
            "freeze_authority_flag": freeze,
            "jurisdiction": "United States",
            **_mock_lineage(jurisdiction="United States"),
        })
    return annotate_quality(pd.DataFrame(rows), ["estimated_redemption_time_hours"])


def create_off_ramp_characteristics() -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    rows = []
    providers = ["Demo Exchange", "Local OTC", "Mobile Wallet Partner"]
    for corridor, sender, receiver in CORRIDORS:
        country = receiver
        for stablecoin, _, _ in STABLECOINS[:3]:
            for prov in providers:
                rows.append({
                    "date": "2024-12-01",
                    "corridor": corridor,
                    "country": country,
                    "stablecoin": stablecoin,
                    "exchange_or_provider": prov,
                    "off_ramp_fee_pct": np.random.uniform(0.3, 1.5),
                    "fiat_withdrawal_fee_pct": np.random.uniform(0.1, 0.8),
                    "estimated_off_ramp_time_hours": np.random.uniform(1, 24),
                    "kyc_required_flag": True,
                    "compliance_delay_hours": np.random.uniform(2, 48),
                    "local_bank_dependency_flag": country not in ("India", "Philippines"),
                    **_mock_lineage(jurisdiction=country),
                })
    return annotate_quality(pd.DataFrame(rows), ["off_ramp_fee_pct"])


def create_remittance_comparison() -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    rows = []
    for corridor, sender, receiver in CORRIDORS:
        trad_fee = np.random.uniform(3.0, 7.5)
        trad_fx = np.random.uniform(0.5, 3.0)
        onramp = np.random.uniform(0.5, 2.0)
        chain = np.random.uniform(0.01, 0.5)
        offramp = np.random.uniform(0.5, 2.5)
        fx_spread = np.random.uniform(0.2, 1.5)
        finality_h = np.random.uniform(2, 72)
        rows.append({
            "date": "2024-12-01",
            "corridor": corridor,
            "sender_country": sender,
            "receiver_country": receiver,
            "traditional_fee_pct": trad_fee,
            "traditional_fx_margin_pct": trad_fx,
            "traditional_transfer_speed_days": np.random.choice([0.5, 1, 2, 3]),
            "stablecoin_onramp_fee_pct": onramp,
            "stablecoin_chain_fee_pct": chain,
            "stablecoin_offramp_fee_pct": offramp,
            "stablecoin_fx_spread_pct": fx_spread,
            "stablecoin_effective_finality_hours": finality_h,
            **_mock_lineage(jurisdiction=receiver),
        })
    return annotate_quality(pd.DataFrame(rows), ["traditional_fee_pct"])


def create_regulatory_events() -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    events = [
        ("REG_001", "2024-03-15", "United States", "US federal", "USDT", "Tether",
         "enforcement", "Synthetic CFTC settlement reference for demo.", 0.6, "issuer"),
        ("REG_002", "2024-06-01", "European Union", "EU MiCA", "USDC", "Circle",
         "licensing", "Synthetic stablecoin licensing pathway note.", 0.4, "compliance"),
        ("REG_003", "2024-08-20", "Nigeria", "CBN", "USDT", "Tether",
         "restriction", "Synthetic P2P stablecoin restriction placeholder.", 0.7, "off_ramp"),
        ("REG_004", "2024-11-01", "India", "RBI", "USDC", "Circle",
         "KYC", "Synthetic off-ramp KYC tightening placeholder.", 0.5, "off_ramp"),
    ]
    rows = []
    for ev in events:
        rows.append({
            "event_id": ev[0],
            "date": ev[1],
            "country": ev[2],
            "jurisdiction": ev[3],
            "stablecoin": ev[4],
            "issuer": ev[5],
            "event_type": ev[6],
            "event_description": ev[7],
            "severity_score": ev[8],
            "affected_component": ev[9],
            **_mock_lineage(jurisdiction=ev[2]),
        })
    return annotate_quality(pd.DataFrame(rows), ["event_id"])


def create_mock_dataset() -> dict[str, pd.DataFrame]:
    return {
        "stablecoin_supply": create_stablecoin_supply(),
        "stablecoin_price_peg": create_stablecoin_price_peg(),
        "stablecoin_reserves": create_stablecoin_reserves(),
        "blockchain_settlement_characteristics": create_blockchain_settlement_characteristics(),
        "stablecoin_redemption_characteristics": create_stablecoin_redemption_characteristics(),
        "off_ramp_characteristics": create_off_ramp_characteristics(),
        "remittance_comparison": create_remittance_comparison(),
        "regulatory_events": create_regulatory_events(),
    }

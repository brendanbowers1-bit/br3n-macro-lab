"""Strictly labeled synthetic demo data for Settlement Economics Lab."""

from __future__ import annotations

import warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from src.config.research_settings import MOCK_SOURCE_ID, MOCK_MAX_QUALITY_SCORE
from src.quality.lineage import attach_lineage, base_lineage
from src.quality.data_quality import annotate_quality

COUNTRIES = [
    "United States", "Mexico", "India", "Philippines", "Brazil",
    "United Kingdom", "Euro Area", "Nigeria", "Saudi Arabia", "Colombia",
]

RAILS = [
    ("card network", "card", 1.0, 0.002, 0.001),
    ("ACH/batch payment", "ach", 2.0, 0.001, 0.0005),
    ("RTGS/wire", "rtgs", 0.04, 0.0003, 0.0001),
    ("remittance operator", "remittance", 3.0, 0.015, 0.008),
    ("mobile money", "mobile", 0.5, 0.005, 0.003),
    ("tokenized settlement placeholder", "tokenized", 0.02, 0.003, 0.002),
]

MOCK_WARNING = (
    "⚠️ DEMO MODE: Synthetic settlement data only. "
    "Do not use for research conclusions or operational decisions."
)


def _mock_lineage() -> dict:
    lg = base_lineage(MOCK_SOURCE_ID, mock_data_flag=True, observed=False)
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


def create_payment_flow_observations(n_days: int = 90) -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    rows = []
    base = datetime(2024, 1, 1)
    lg = _mock_lineage()
    for country in COUNTRIES:
        for ps, rail, lag_days, fail, charge in RAILS:
            for i in range(n_days):
                dt = base + timedelta(days=i)
                vol = np.random.lognormal(16, 0.5)
                rows.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "period": dt.strftime("%Y-%m"),
                    "country": country,
                    "region": "Americas" if country in ("United States", "Mexico", "Brazil", "Colombia") else "Other",
                    "payment_system": ps,
                    "rail_type": rail,
                    "payment_type": "retail",
                    "currency": "USD",
                    "transaction_count": int(vol / 50),
                    "transaction_value_usd": vol,
                    "average_transaction_value_usd": 50.0,
                    "settlement_lag_hours": lag_days * 24,
                    "settlement_lag_days": lag_days,
                    "availability_lag_hours": lag_days * 24 + 2,
                    "finality_lag_hours": lag_days * 24 + 4,
                    "reversal_window_hours": 72 if rail == "card" else 24,
                    "failure_rate": fail,
                    "return_rate": fail * 0.5,
                    "chargeback_rate": charge,
                    **lg,
                })
    df = pd.DataFrame(rows)
    return annotate_quality(df, ["transaction_value_usd", "settlement_lag_days"])


def create_settlement_liquidity_table() -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    rows = []
    lg = _mock_lineage()
    for country in COUNTRIES:
        for ps, rail, lag, _, _ in RAILS:
            adv = np.random.lognormal(17, 0.4)
            prefund = adv * np.random.uniform(0.05, 0.25)
            rows.append({
                "date": "2024-06-01",
                "institution_type": "settlement_bank",
                "payment_system": ps,
                "currency": "USD",
                "average_daily_settlement_value_usd": adv,
                "peak_daily_settlement_value_usd": adv * 1.4,
                "prefunding_required_usd": prefund,
                "collateral_required_usd": prefund * 0.3,
                "settlement_account_balance_usd": prefund * 0.5,
                "intraday_credit_used_usd": adv * 0.1,
                "liquidity_buffer_usd": prefund * 0.2,
                "cost_of_capital_pct": 0.05,
                "interest_rate_pct": 0.045,
                "opportunity_cost_usd": prefund * 0.05 / 365,
                **lg,
            })
    return annotate_quality(pd.DataFrame(rows))


def create_fx_settlement_exposure() -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    pairs = ["USD/MXN", "USD/INR", "USD/PHP", "USD/BRL", "USD/NGN", "EUR/USD"]
    rows = []
    lg = _mock_lineage()
    for pair in pairs:
        for i in range(60):
            dt = datetime(2024, 1, 1) + timedelta(days=i)
            notional = np.random.lognormal(15, 0.3)
            vol30 = np.random.uniform(0.08, 0.18)
            rows.append({
                "date": dt.strftime("%Y-%m-%d"),
                "currency_pair": pair,
                "settlement_window_days": np.random.choice([1, 2, 3]),
                "notional_value_usd": notional,
                "fx_volatility_1d": vol30 / np.sqrt(252),
                "fx_volatility_5d": vol30 / np.sqrt(52),
                "fx_volatility_30d": vol30,
                "expected_fx_exposure_usd": notional * vol30 * 0.1,
                "realized_fx_move_pct": np.random.normal(0, vol30 / np.sqrt(252)),
                **lg,
            })
    return annotate_quality(pd.DataFrame(rows))


def create_finality_characteristics() -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    rows = []
    lg = _mock_lineage()
    lg["manual_assumption_flag"] = True
    for country in COUNTRIES:
        for ps, rail, lag, _, charge in RAILS:
            base_f = 95 if rail == "rtgs" else 70 if rail == "ach" else 60
            rows.append({
                "country": country,
                "payment_system": ps,
                "rail_type": rail,
                "legal_finality_score": min(base_f + np.random.uniform(-5, 5), 100),
                "operational_finality_score": min(base_f + np.random.uniform(-10, 5), 100),
                "funds_availability_score": min(100 - lag * 10, 100),
                "reversibility_risk_score": min(charge * 1000 + 20, 100),
                "reconciliation_quality_score": np.random.uniform(60, 95),
                "settlement_failure_risk_score": np.random.uniform(5, 30),
                "finality_lag_hours": lag * 24,
                **lg,
            })
    return annotate_quality(pd.DataFrame(rows))


def create_payment_access() -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    lg = _mock_lineage()
    rows = []
    for country in COUNTRIES:
        rows.append({
            "country": country,
            "year": 2024,
            "account_ownership_pct": np.random.uniform(0.4, 0.95),
            "digital_payment_usage_pct": np.random.uniform(0.2, 0.8),
            "mobile_money_usage_pct": np.random.uniform(0.05, 0.6),
            "card_ownership_pct": np.random.uniform(0.2, 0.85),
            "formal_savings_pct": np.random.uniform(0.2, 0.7),
            "remittance_received_pct": np.random.uniform(0.05, 0.35),
            "cash_dependency_proxy": np.random.uniform(0.1, 0.7),
            **lg,
        })
    return annotate_quality(pd.DataFrame(rows))


def create_stress_events() -> pd.DataFrame:
    warnings.warn(MOCK_WARNING, stacklevel=2)
    lg = _mock_lineage()
    events = [
        ("FX volatility shock", "United States", 0.6, 0.2, 0.001, -0.05, -0.1),
        ("Settlement bank outage", "India", 0.8, 0.5, 0.005, -0.15, 0.05),
        ("Liquidity buffer reduction", "Euro Area", 0.5, 0.1, 0.0005, -0.2, 0.0),
        ("Cross-border corridor disruption", "Nigeria", 0.7, 0.8, 0.008, -0.1, -0.2),
    ]
    rows = []
    for i, (etype, country, sev, delay, fail, liq, vol) in enumerate(events):
        rows.append({
            "event_id": f"EVT_{i+1}",
            "date_start": "2024-03-01",
            "date_end": "2024-03-15",
            "country": country,
            "region": "Global",
            "payment_system": "multi-rail",
            "event_type": etype,
            "severity_score": sev,
            "settlement_delay_change": delay,
            "failure_rate_change": fail,
            "liquidity_buffer_change": liq,
            "volume_shock_pct": vol,
            "public_description": f"Synthetic {etype} for demo pipeline.",
            **lg,
        })
    return annotate_quality(pd.DataFrame(rows))


def create_mock_dataset() -> dict[str, pd.DataFrame]:
    return {
        "payment_flow_observations": create_payment_flow_observations(),
        "settlement_liquidity_table": create_settlement_liquidity_table(),
        "fx_settlement_exposure": create_fx_settlement_exposure(),
        "finality_characteristics": create_finality_characteristics(),
        "payment_access_and_inclusion": create_payment_access(),
        "payment_network_stress_events": create_stress_events(),
    }

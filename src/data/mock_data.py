"""
Synthetic datasets for the Global FX & Remittance Research Lab.

⚠️  MOCK DATA — for development and dashboard demos only.
Replace with real World Bank / IMF / BIS files in data/raw/.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

MOCK_CORRIDORS = [
    ("United States", "Mexico", "USD", "MXN"),
    ("United States", "India", "USD", "INR"),
    ("United States", "Philippines", "USD", "PHP"),
    ("United States", "Colombia", "USD", "COP"),
    ("United States", "Brazil", "USD", "BRL"),
    ("United States", "Guatemala", "USD", "GTQ"),
    ("United States", "El Salvador", "USD", "USD"),
    ("United States", "Dominican Republic", "USD", "DOP"),
    ("Germany", "Nigeria", "EUR", "NGN"),
    ("Saudi Arabia", "India", "SAR", "INR"),
    ("United Arab Emirates", "Pakistan", "AED", "PKR"),
]

MOCK_COUNTRIES = [
    ("Mexico", "MXN"),
    ("India", "INR"),
    ("Philippines", "PHP"),
    ("Colombia", "COP"),
    ("Brazil", "BRL"),
    ("Guatemala", "GTQ"),
    ("Nigeria", "NGN"),
    ("Pakistan", "PKR"),
    ("United States", "USD"),
    ("Germany", "EUR"),
    ("Saudi Arabia", "SAR"),
    ("United Arab Emirates", "AED"),
    ("El Salvador", "USD"),
    ("Dominican Republic", "DOP"),
]


def is_using_mock_data(tables: dict) -> bool:
    """Return True if any table is labelled mock/synthetic."""
    for name, df in tables.items():
        if name.startswith("_") or not hasattr(df, "columns"):
            continue
        if "mock_data_flag" in df.columns and df["mock_data_flag"].any():
            return True
        if "source" in df.columns and df["source"].notna().any():
            if "mock" in str(df["source"].dropna().iloc[0]).lower():
                return True
    return False


def create_mock_dataset(seed: int = 42) -> dict[str, pd.DataFrame]:
    """Return all five canonical tables with realistic synthetic values."""
    warnings.warn(
        "Using MOCK DATA for Global FX Research Lab. "
        "Place real files in data/raw/world_bank_rpw/, imf/, bis/, etc.",
        stacklevel=2,
    )
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2022-01-01", "2025-01-01", freq="QS")
    providers = ["Bank A", "MoneyGram", "Wise", "Western Union", "Mobile Wallet"]

    # corridor_prices
    cp_rows = []
    for d in dates:
        q = f"{d.year}Q{(d.month - 1) // 3 + 1}"
        for sender, receiver, sc, rc in MOCK_CORRIDORS:
            corridor = f"{sender}→{receiver}"
            for prov in providers[:3]:
                fee = rng.uniform(0.005, 0.025)
                margin = rng.uniform(0.01, 0.045)
                speed = int(rng.integers(0, 5))
                cp_rows.append(
                    {
                        "date": d,
                        "quarter": q,
                        "sender_country": sender,
                        "receiver_country": receiver,
                        "sender_currency": sc,
                        "receiver_currency": rc,
                        "corridor": corridor,
                        "provider": prov,
                        "provider_type": "bank" if "Bank" in prov else "mto",
                        "send_amount_usd": 200.0,
                        "total_cost_pct": fee + margin + rng.uniform(0.005, 0.02),
                        "fee_pct": fee,
                        "fx_margin_pct": margin,
                        "transfer_speed_days": speed,
                        "payout_method": "bank" if rng.random() > 0.3 else "cash",
                        "transparency_flag": rng.random() > 0.25,
                        "source": "mock_synthetic",
                    }
                )
    corridor_prices = pd.DataFrame(cp_rows)

    # fx_rates — daily for receiver currencies
    fx_rows = []
    daily = pd.bdate_range("2022-01-01", "2025-01-01")
    rates_base = {"MXN": 18.0, "INR": 83.0, "PHP": 56.0, "COP": 4000.0, "BRL": 5.0,
                  "NGN": 800.0, "PKR": 280.0, "EUR": 0.92, "AED": 3.67, "SAR": 3.75,
                  "GTQ": 7.8, "DOP": 58.0, "USD": 1.0}
    for country, ccy in MOCK_COUNTRIES:
        if ccy == "USD":
            continue
        base = rates_base.get(ccy, 10.0)
        rets = rng.normal(0, 0.008, len(daily))
        prices = base * np.exp(np.cumsum(rets))
        for i, dt in enumerate(daily):
            fx_rows.append(
                {
                    "date": dt,
                    "currency": ccy,
                    "country": country,
                    "usd_fx_rate": float(prices[i]),
                    "daily_return": float(rets[i]),
                    "monthly_return": np.nan,
                    "quarterly_return": np.nan,
                    "volatility_30d": float(np.std(rets[max(0, i - 30): i + 1]) * np.sqrt(252)) if i > 5 else np.nan,
                    "volatility_90d": float(np.std(rets[max(0, i - 90): i + 1]) * np.sqrt(252)) if i > 10 else np.nan,
                    "drawdown_1y": np.nan,
                }
            )
    fx_rates = pd.DataFrame(fx_rows)
    fx_rates["monthly_return"] = fx_rates.groupby("currency")["usd_fx_rate"].pct_change(21)
    fx_rates["drawdown_1y"] = fx_rates.groupby("currency")["usd_fx_rate"].transform(
        lambda s: s / s.rolling(252, min_periods=60).max() - 1
    )

    # macro_country_panel — quarterly
    macro_rows = []
    for d in dates:
        for country, ccy in MOCK_COUNTRIES:
            macro_rows.append(
                {
                    "date": d,
                    "year": d.year,
                    "quarter": f"{d.year}Q{(d.month - 1) // 3 + 1}",
                    "country": country,
                    "currency": ccy,
                    "inflation_yoy": float(rng.uniform(0.02, 0.12) if country not in ("United States", "Germany") else rng.uniform(0.02, 0.05)),
                    "policy_rate": float(rng.uniform(0.04, 0.14)),
                    "gdp_growth": float(rng.uniform(-0.01, 0.06)),
                    "current_account_gdp": float(rng.uniform(-0.06, 0.02)),
                    "reserves_months_imports": float(rng.uniform(2, 12)),
                    "external_debt_gdp": float(rng.uniform(0.2, 0.8)),
                    "remittances_gdp": float(rng.uniform(0.01, 0.15) if country != "United States" else 0.0),
                    "imports_gdp": float(rng.uniform(0.15, 0.45)),
                    "trade_openness": float(rng.uniform(0.3, 0.9)),
                    "unemployment": float(rng.uniform(0.04, 0.12)),
                    "source": "mock_synthetic",
                }
            )
    macro_country_panel = pd.DataFrame(macro_rows)

    # remittance_flows
    flow_rows = []
    for year in range(2022, 2025):
        total = 0
        for sender, receiver, _, _ in MOCK_CORRIDORS:
            usd = float(rng.uniform(5e9, 40e9))
            total += usd
            flow_rows.append(
                {
                    "year": year,
                    "sender_country": sender,
                    "receiver_country": receiver,
                    "corridor": f"{sender}→{receiver}",
                    "remittance_usd": usd,
                    "receiver_gdp": float(rng.uniform(200e9, 1500e9)),
                    "remittance_share_gdp": usd / float(rng.uniform(200e9, 1500e9)),
                    "corridor_weight": np.nan,
                }
            )
        for r in flow_rows:
            if r["year"] == year:
                r["corridor_weight"] = r["remittance_usd"] / total
    remittance_flows = pd.DataFrame(flow_rows)

    # currency_market_structure
    cms_rows = []
    for year in [2022, 2025]:
        total_turn = 7.5e12
        shares = {"USD": 0.44, "EUR": 0.16, "JPY": 0.08, "GBP": 0.06, "MXN": 0.012,
                  "INR": 0.011, "BRL": 0.009, "PHP": 0.004, "COP": 0.003, "NGN": 0.002, "PKR": 0.002}
        for ccy, share in shares.items():
            cms_rows.append(
                {
                    "year": year,
                    "currency": ccy,
                    "fx_turnover_usd": total_turn * share,
                    "global_turnover_share": share,
                    "liquidity_score": min(100, share * 200),
                    "dollar_pair_share": 0.88 if ccy != "USD" else 1.0,
                }
            )
    currency_market_structure = pd.DataFrame(cms_rows)

    return {
        "corridor_prices": corridor_prices,
        "fx_rates": fx_rates,
        "macro_country_panel": macro_country_panel,
        "remittance_flows": remittance_flows,
        "currency_market_structure": currency_market_structure,
        "_meta": pd.DataFrame([{"source": "mock", "warning": "Replace with real data"}]),
    }

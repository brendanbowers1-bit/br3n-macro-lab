"""
Remittance / payment corridor registry for multi-corridor FX research.

Research-only. Public flow proxies are not actual payment-flow data.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

CORRIDOR_REGISTRY: Dict[str, Dict[str, Any]] = {
    "US_MX": {
        "corridor_id": "US_MX",
        "sender_country": "United States",
        "receiver_country": "Mexico",
        "sender_currency": "USD",
        "receiver_currency": "MXN",
        "model_pair": "USDMXN=X",
        "official_pair_label": "USD/MXN",
        "priority": 1,
        "corridor_theme": "remittance_heavy",
        "data_warning": None,
        "flow_proxies": [
            "US payday windows",
            "month-end",
            "Mother's Day",
            "Christmas",
            "Semana Santa",
            "Mexico holidays",
            "Banxico remittance seasonality later",
        ],
    },
    "US_IN": {
        "corridor_id": "US_IN",
        "sender_country": "United States",
        "receiver_country": "India",
        "sender_currency": "USD",
        "receiver_currency": "INR",
        "model_pair": "USDINR=X",
        "official_pair_label": "USD/INR",
        "priority": 1,
        "corridor_theme": "remittance_heavy_policy_sensitive",
        "data_warning": "INR may require NDF/official data validation for serious research.",
        "flow_proxies": [
            "US payday windows",
            "month-end",
            "Diwali proxy",
            "school-fee season",
            "India holidays",
            "RBI/remittance data later",
        ],
    },
    "US_PH": {
        "corridor_id": "US_PH",
        "sender_country": "United States",
        "receiver_country": "Philippines",
        "sender_currency": "USD",
        "receiver_currency": "PHP",
        "model_pair": "USDPHP=X",
        "official_pair_label": "USD/PHP",
        "priority": 1,
        "corridor_theme": "remittance_heavy",
        "data_warning": "Validate against BSP or official data for publication.",
        "flow_proxies": [
            "US payday windows",
            "month-end",
            "Christmas",
            "school-fee season",
            "Philippines holidays",
            "BSP remittance data later",
        ],
    },
    "US_CO": {
        "corridor_id": "US_CO",
        "sender_country": "United States",
        "receiver_country": "Colombia",
        "sender_currency": "USD",
        "receiver_currency": "COP",
        "model_pair": "USDCOP=X",
        "official_pair_label": "USD/COP",
        "priority": 1,
        "corridor_theme": "latam_remittance_oil_risk",
        "data_warning": "COP can be volatile and oil/risk sensitive.",
        "flow_proxies": [
            "US payday windows",
            "month-end",
            "Christmas",
            "Colombia holidays",
            "oil sensitivity later",
        ],
    },
    "US_BR": {
        "corridor_id": "US_BR",
        "sender_country": "United States",
        "receiver_country": "Brazil",
        "sender_currency": "USD",
        "receiver_currency": "BRL",
        "model_pair": "USDBRL=X",
        "official_pair_label": "USD/BRL",
        "priority": 1,
        "corridor_theme": "latam_macro_risk",
        "data_warning": "BRL can be volatile and sensitive to global risk/commodities.",
        "flow_proxies": [
            "US payday windows",
            "month-end",
            "Christmas",
            "Brazil holidays",
            "commodity/risk proxy later",
        ],
    },
    "US_GT": {
        "corridor_id": "US_GT",
        "sender_country": "United States",
        "receiver_country": "Guatemala",
        "sender_currency": "USD",
        "receiver_currency": "GTQ",
        "model_pair": "USDGTQ=X",
        "official_pair_label": "USD/GTQ",
        "priority": 2,
        "corridor_theme": "central_america_remittance_heavy",
        "data_warning": "Yahoo data may be limited or unreliable. Official or bank data may be needed.",
        "flow_proxies": [
            "US payday windows",
            "month-end",
            "Christmas",
            "Guatemala holidays",
        ],
    },
    "GULF_IN_PROXY": {
        "corridor_id": "GULF_IN_PROXY",
        "sender_country": "UAE/Saudi Arabia proxy",
        "receiver_country": "India",
        "sender_currency": "AED/SAR proxy",
        "receiver_currency": "INR",
        "model_pair": "USDINR=X",
        "official_pair_label": "USD/INR proxy for Gulf pegs",
        "priority": 2,
        "corridor_theme": "gulf_to_india_proxy",
        "data_warning": "AED and SAR are USD-pegged, so USD/INR is a proxy, not a direct corridor pair.",
        "flow_proxies": [
            "Gulf payroll proxy",
            "India holidays",
            "Diwali proxy",
            "Ramadan/Eid proxy",
        ],
    },
}


def get_corridor(corridor_id: str) -> Dict[str, Any]:
    """Return metadata for one corridor."""
    if corridor_id not in CORRIDOR_REGISTRY:
        raise KeyError(f"Unknown corridor: {corridor_id}")
    return CORRIDOR_REGISTRY[corridor_id].copy()


def list_corridors(priority: Optional[int] = None) -> List[Dict[str, Any]]:
    """Return corridor metadata list, optionally filtered by priority."""
    items = list(CORRIDOR_REGISTRY.values())
    if priority is not None:
        items = [c for c in items if c["priority"] == priority]
    return items


def get_model_pairs(priority: Optional[int] = None) -> List[str]:
    """Return unique model_pair tickers."""
    corridors = list_corridors(priority)
    return sorted({c["model_pair"] for c in corridors})


def corridor_summary_dataframe() -> pd.DataFrame:
    """Registry summary as DataFrame."""
    rows = []
    for c in CORRIDOR_REGISTRY.values():
        rows.append(
            {
                "corridor_id": c["corridor_id"],
                "sender_country": c["sender_country"],
                "receiver_country": c["receiver_country"],
                "model_pair": c["model_pair"],
                "official_pair_label": c["official_pair_label"],
                "priority": c["priority"],
                "corridor_theme": c["corridor_theme"],
                "data_warning": c["data_warning"],
            }
        )
    return pd.DataFrame(rows)

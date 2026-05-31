"""
Core FX pairs and remittance corridors for the research terminal.

Reuses corridor metadata from src.corridors where available; extends with
additional corridors requested for the terminal.
"""

from __future__ import annotations

from typing import Any

# Yahoo-style tickers — aligned with config.yaml research_ladder.pairs where possible
CORE_FX_PAIRS: list[str] = [
    "EURUSD=X",
    "GBPUSD=X",
    "USDJPY=X",
    "USDCAD=X",
    "USDMXN=X",
    "USDBRL=X",
    "USDINR=X",
    "USDPHP=X",
    "USDCOP=X",
]

DXY_TICKERS: list[str] = ["DX-Y.NYB", "DTWEXBGS"]

PAIR_LABELS: dict[str, str] = {
    "EURUSD=X": "EUR/USD",
    "GBPUSD=X": "GBP/USD",
    "USDJPY=X": "USD/JPY",
    "USDCAD=X": "USD/CAD",
    "USDMXN=X": "USD/MXN",
    "USDBRL=X": "USD/BRL",
    "USDINR=X": "USD/INR",
    "USDPHP=X": "USD/PHP",
    "USDCOP=X": "USD/COP",
}

# Approximate carry in bps (annual) for mock / fallback when rates unavailable
DEFAULT_CARRY_BPS: dict[str, float] = {
    "EURUSD=X": 0,
    "GBPUSD=X": 50,
    "USDJPY=X": -450,
    "USDCAD=X": -100,
    "USDMXN=X": 350,
    "USDBRL=X": 800,
    "USDINR=X": 250,
    "USDPHP=X": 200,
    "USDCOP=X": 600,
}

TERMINAL_CORRIDORS: dict[str, dict[str, Any]] = {
    "US_MX": {
        "corridor_id": "US_MX",
        "label": "US → Mexico",
        "model_pair": "USDMXN=X",
        "receiver_currency": "MXN",
        "priority": 1,
    },
    "US_IN": {
        "corridor_id": "US_IN",
        "label": "US → India",
        "model_pair": "USDINR=X",
        "receiver_currency": "INR",
        "priority": 1,
    },
    "US_PH": {
        "corridor_id": "US_PH",
        "label": "US → Philippines",
        "model_pair": "USDPHP=X",
        "receiver_currency": "PHP",
        "priority": 1,
    },
    "US_CO": {
        "corridor_id": "US_CO",
        "label": "US → Colombia",
        "model_pair": "USDCOP=X",
        "receiver_currency": "COP",
        "priority": 1,
    },
    "US_BR": {
        "corridor_id": "US_BR",
        "label": "US → Brazil",
        "model_pair": "USDBRL=X",
        "receiver_currency": "BRL",
        "priority": 1,
    },
    "US_GT": {
        "corridor_id": "US_GT",
        "label": "US → Guatemala",
        "model_pair": "USDGTQ=X",
        "receiver_currency": "GTQ",
        "priority": 2,
        "data_warning": "Limited public data; may use proxy or mock.",
    },
    "US_SV": {
        "corridor_id": "US_SV",
        "label": "US → El Salvador",
        "model_pair": "USDMXN=X",
        "receiver_currency": "USD",
        "priority": 2,
        "data_warning": "USD legal tender; USD/MXN used as LatAm remittance proxy.",
    },
    "US_DO": {
        "corridor_id": "US_DO",
        "label": "US → Dominican Republic",
        "model_pair": "USDMXN=X",
        "receiver_currency": "DOP",
        "priority": 2,
        "data_warning": "USDDOP=X may be unavailable; proxy pair used.",
    },
    "EU_AFRICA": {
        "corridor_id": "EU_AFRICA",
        "label": "Europe → Africa",
        "model_pair": "USDZAR=X",
        "receiver_currency": "multi",
        "priority": 2,
        "data_warning": "USD/ZAR proxy for EM/Africa remittance research.",
    },
    "GULF_SA": {
        "corridor_id": "GULF_SA",
        "label": "Gulf → South Asia",
        "model_pair": "USDINR=X",
        "receiver_currency": "INR",
        "priority": 2,
        "data_warning": "Gulf pegs to USD; USD/INR is corridor proxy.",
    },
}


def pair_label(ticker: str) -> str:
    return PAIR_LABELS.get(ticker, ticker.replace("=X", "").replace("USD", "USD/"))

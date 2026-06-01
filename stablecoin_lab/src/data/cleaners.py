"""Standardize dates, stablecoin names, and blockchain networks."""

from __future__ import annotations

import pandas as pd

STABLECOIN_ALIASES = {
    "USDC": "USDC",
    "USD COIN": "USDC",
    "USDT": "USDT",
    "TETHER": "USDT",
    "PYUSD": "PYUSD",
    "PAYPAL USD": "PYUSD",
    "DAI": "DAI",
    "TOKENIZED_BANK_DEPOSIT": "tokenized_bank_deposit_placeholder",
    "TOKENIZED BANK DEPOSIT": "tokenized_bank_deposit_placeholder",
    "TOKENIZED_BANK_DEPOSIT_PLACEHOLDER": "tokenized_bank_deposit_placeholder",
}

NETWORK_ALIASES = {
    "ETH": "Ethereum",
    "ETHEREUM": "Ethereum",
    "SOL": "Solana",
    "SOLANA": "Solana",
    "TRX": "Tron",
    "TRON": "Tron",
    "BASE": "Base",
    "POLYGON": "Polygon",
    "MATIC": "Polygon",
    "ARBITRUM": "Arbitrum",
    "ARB": "Arbitrum",
}


def standardize_dates(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    out = df.copy()
    if col in out.columns:
        out[col] = pd.to_datetime(out[col], errors="coerce")
    if "timestamp" in out.columns:
        out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    return out


def standardize_stablecoin_names(df: pd.DataFrame, col: str = "stablecoin") -> pd.DataFrame:
    out = df.copy()
    if col not in out.columns:
        return out
    normalized = (
        out[col]
        .astype(str)
        .str.upper()
        .str.strip()
        .replace(STABLECOIN_ALIASES)
    )
    out[col] = normalized
    if "ticker" in out.columns:
        out["ticker"] = out["ticker"].astype(str).str.upper().str.strip()
        out.loc[out["ticker"].isin(["", "NAN"]), "ticker"] = out[col]
    return out


def standardize_network_names(df: pd.DataFrame, col: str = "blockchain_network") -> pd.DataFrame:
    out = df.copy()
    if col not in out.columns:
        return out
    out[col] = (
        out[col]
        .astype(str)
        .str.upper()
        .str.strip()
        .replace(NETWORK_ALIASES)
    )
    return out

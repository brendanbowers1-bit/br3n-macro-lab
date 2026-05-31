"""Schema validation for VSI canonical tables."""

from __future__ import annotations

import pandas as pd

from .schema import SCHEMAS


def _missing_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
    return [c for c in required if c not in df.columns]


def validate_corridor_prices(df: pd.DataFrame) -> dict:
    required = ["sender_country", "receiver_country", "corridor", "fee_pct", "fx_margin_pct"]
    missing = _missing_columns(df, required)
    return {"valid": len(missing) == 0 and len(df) > 0, "missing": missing, "rows": len(df)}


def validate_fx_rates(df: pd.DataFrame) -> dict:
    required = ["date", "currency", "usd_fx_rate"]
    missing = _missing_columns(df, required)
    return {"valid": len(missing) == 0 and len(df) > 0, "missing": missing, "rows": len(df)}


def validate_macro_panel(df: pd.DataFrame) -> dict:
    required = ["country", "currency", "inflation_yoy"]
    missing = _missing_columns(df, required)
    return {"valid": len(missing) == 0 and len(df) > 0, "missing": missing, "rows": len(df)}


def validate_remittance_flows(df: pd.DataFrame) -> dict:
    required = ["corridor", "remittance_usd", "year"]
    missing = _missing_columns(df, required)
    return {"valid": len(missing) == 0 and len(df) > 0, "missing": missing, "rows": len(df)}


def validate_value_survival_outputs(df: pd.DataFrame) -> dict:
    required = [
        "corridor",
        "value_survival_index",
        "total_value_loss_pct",
        "real_usable_value_delivered_pct",
    ]
    missing = _missing_columns(df, required)
    neg_vsi = int((df["value_survival_index"] < 0).sum()) if "value_survival_index" in df.columns else 0
    return {
        "valid": len(missing) == 0 and len(df) > 0 and neg_vsi == 0,
        "missing": missing,
        "rows": len(df),
        "negative_vsi_count": neg_vsi,
    }


def validate_all_tables(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    checks = {
        "corridor_prices": validate_corridor_prices,
        "fx_rates": validate_fx_rates,
        "macro_country_panel": validate_macro_panel,
        "remittance_flows": validate_remittance_flows,
        "value_survival_outputs": validate_value_survival_outputs,
    }
    rows = []
    for name, fn in checks.items():
        if name not in tables:
            continue
        r = fn(tables[name])
        rows.append({"table": name, **r})
    return pd.DataFrame(rows)

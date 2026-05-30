"""
Forward points placeholders for future trading-grade carry/hedge economics.

Policy-rate carry is a proxy only. Forward points required for realistic hedge economics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

FORWARD_COLUMNS = [
    "forward_1m",
    "forward_3m",
    "forward_points_1m",
    "forward_points_3m",
    "annualized_forward_carry_1m",
    "annualized_forward_carry_3m",
    "forward_data_available",
]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FORWARD_CSV_PATHS = [
    ROOT / "data" / "raw" / "forwards_usdmxn.csv",
    ROOT / "data" / "raw" / "USDMXN_forwards.csv",
]


def add_forward_point_placeholders(df: pd.DataFrame) -> pd.DataFrame:
    """Add forward columns as NaN/False when no forward data exists."""
    out = df.copy()
    for col in FORWARD_COLUMNS:
        if col in out.columns:
            continue
        if col == "forward_data_available":
            out[col] = False
        else:
            out[col] = np.nan
    return out


def compute_forward_carry(
    df: pd.DataFrame,
    spot_col: str = "price",
    forward_col: str = "forward_1m",
    tenor_months: int = 1,
) -> pd.DataFrame:
    """
    annualized_forward_carry = ((forward / spot) - 1) * (12 / tenor_months)

    WARNING: Forward points are required for realistic hedge economics.
    Policy-rate carry is only a proxy.
    """
    out = df.copy()
    if forward_col not in out.columns or spot_col not in out.columns:
        return out
    valid = out[forward_col].notna() & out[spot_col].notna() & (out[spot_col] != 0)
    out.loc[valid, f"annualized_forward_carry_{tenor_months}m"] = (
        (out.loc[valid, forward_col] / out.loc[valid, spot_col] - 1.0) * (12.0 / tenor_months)
    )
    out["forward_data_available"] = valid.any()
    return out


def load_forward_points_csv(path: Path | str) -> pd.DataFrame:
    """
    Load user-provided forward points CSV.

    Expected columns: date, currency_pair, spot, forward_1m, forward_3m, bid, ask
    """
    path = Path(path)
    raw = pd.read_csv(path)
    raw.columns = [str(c).lower() for c in raw.columns]
    required = {"date", "spot"}
    if not required.issubset(raw.columns):
        raise ValueError(f"Forward CSV must include {required}; got {list(raw.columns)}")

    raw["date"] = pd.to_datetime(raw["date"])
    out = raw.sort_values("date").drop_duplicates("date", keep="last")

    if "forward_1m" in out.columns and "spot" in out.columns:
        out["forward_points_1m"] = out["forward_1m"] - out["spot"]
    if "forward_3m" in out.columns and "spot" in out.columns:
        out["forward_points_3m"] = out["forward_3m"] - out["spot"]

    out = compute_forward_carry(out.rename(columns={"spot": "price"}), spot_col="price", forward_col="forward_1m", tenor_months=1)
    if "forward_3m" in out.columns:
        out = compute_forward_carry(out, spot_col="price", forward_col="forward_3m", tenor_months=3)
    return out


def discover_forward_csv(config: dict | None = None) -> Path | None:
    """Return first existing forward-points CSV from config or default paths."""
    config = config or {}
    carry_cfg = config.get("carry", {})
    candidates: list[Path] = []
    if carry_cfg.get("forward_csv"):
        p = Path(carry_cfg["forward_csv"])
        candidates.append(p if p.is_absolute() else ROOT / p)
    candidates.extend(DEFAULT_FORWARD_CSV_PATHS)
    seen: set[Path] = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        if path.exists():
            return path
    return None


def merge_forward_points(
    market_df: pd.DataFrame,
    config: dict | None = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Merge user forward-points CSV onto market data if available.

    Drop file at data/raw/forwards_usdmxn.csv (see forwards_usdmxn.csv.example).
    """
    config = config or {}
    status: dict = {"forward_loaded": False, "forward_path": None, "forward_rows": 0, "error": None}
    out = add_forward_point_placeholders(market_df)

    path = discover_forward_csv(config)
    if path is None:
        status["forward_csv_hint"] = (
            "No forward CSV found. Copy data/raw/forwards_usdmxn.csv.example → data/raw/forwards_usdmxn.csv"
        )
        return out, status

    try:
        fwd = load_forward_points_csv(path)
        if "date" not in out.columns:
            out = out.reset_index()
        out["date"] = pd.to_datetime(out["date"])
        fwd["date"] = pd.to_datetime(fwd["date"])

        merge_cols = [c for c in FORWARD_COLUMNS if c in fwd.columns]
        extra = [c for c in ("bid", "ask", "currency_pair") if c in fwd.columns]
        cols = ["date"] + merge_cols + extra
        drop_cols = [c for c in FORWARD_COLUMNS + ["bid", "ask", "currency_pair"] if c in out.columns]
        merged = out.drop(columns=drop_cols, errors="ignore").merge(fwd[cols], on="date", how="left")

        if "forward_1m" in merged.columns:
            merged = compute_forward_carry(merged, spot_col="price", forward_col="forward_1m", tenor_months=1)
        if "forward_3m" in merged.columns:
            merged = compute_forward_carry(merged, spot_col="price", forward_col="forward_3m", tenor_months=3)

        if merged["forward_1m"].notna().any() or merged.get("forward_3m", pd.Series()).notna().any():
            merged["forward_data_available"] = merged["forward_1m"].notna() | merged.get("forward_3m", pd.Series()).notna()

        status.update({"forward_loaded": True, "forward_path": str(path), "forward_rows": int(fwd["date"].nunique())})
        return merged, status
    except Exception as exc:
        status["error"] = str(exc)[:200]
        return out, status

"""
CSV/Excel loaders for World Bank, IMF, BIS, and macro research files.

Drop real files in data/raw/<source>/ — loaders fall back to mock with warnings.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

from src.utils.paths import RAW_DIR

from .cleaners import clean_percent_columns, dedupe_corridor_prices, enforce_schema, parse_dates, standardize_columns
from .mock_data import create_mock_dataset

ROOT_RAW = RAW_DIR


def _find_file(folder: str, extensions: tuple[str, ...] = (".csv", ".xlsx", ".xls")) -> Path | None:
    d = ROOT_RAW / folder
    if not d.exists():
        return None
    for ext in extensions:
        files = sorted(d.glob(f"*{ext}"))
        if files:
            return files[0]
    return None


def _find_named(folder: str, names: list[str]) -> Path | None:
    d = ROOT_RAW / folder
    if not d.exists():
        return None
    for name in names:
        p = d / name
        if p.exists():
            return p
    return None


def _read_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path)
    return pd.read_csv(path)


def _resolve_rpw_path() -> Path | None:
    """Prefer bulk parsed panel, then historical multi-quarter, then curated snapshot."""
    d = ROOT_RAW / "world_bank_rpw"
    if not d.exists():
        return None
    for name in (
        "rpw_parsed.csv",
        "rpw_historical_panel.csv",
        "rpw_corridors_curated.csv",
    ):
        p = d / name
        if p.exists():
            return p
    from .rpw_parser import find_rpw_bulk_file

    bulk = find_rpw_bulk_file()
    if bulk is not None and bulk.stat().st_size > 100_000:
        return bulk
    return _find_file("world_bank_rpw")


def load_world_bank_rpw(path: Path | str | None = None) -> pd.DataFrame:
    """Load Remittance Prices Worldwide corridor pricing table."""
    p = Path(path) if path else _resolve_rpw_path()
    if p is None or not p.exists():
        warnings.warn("World Bank RPW file not found — using mock corridor_prices.", stacklevel=2)
        return create_mock_dataset()["corridor_prices"]
    if p.suffix.lower() in (".xlsx", ".xls") and p.stat().st_size > 100_000:
        from .rpw_parser import parse_rpw_bulk

        return parse_rpw_bulk(p)
    df = _read_any(p)
    df = standardize_columns(
        df,
        {
            "sending_country": "sender_country",
            "receiving_country": "receiver_country",
            "total_cost": "total_cost_pct",
            "fee": "fee_pct",
            "fx_rate_margin": "fx_margin_pct",
            "speed_days": "transfer_speed_days",
        },
    )
    df = clean_percent_columns(df, ["total_cost_pct", "fee_pct", "fx_margin_pct"])
    if "corridor" not in df.columns and {"sender_country", "receiver_country"}.issubset(df.columns):
        df["corridor"] = df["sender_country"].astype(str) + "→" + df["receiver_country"].astype(str)
    df = parse_dates(df)
    df = dedupe_corridor_prices(df)
    return enforce_schema(df, "corridor_prices")


def load_knomad_remittances(path: Path | str | None = None) -> pd.DataFrame:
    """Load bilateral remittance matrix; reshape wide → long if needed."""
    p = Path(path) if path else _find_file("world_bank_knomad")
    if p is None or not p.exists():
        warnings.warn("KNOMAD remittance file not found — using mock remittance_flows.", stacklevel=2)
        return create_mock_dataset()["remittance_flows"]
    df = _read_any(p)
    df = standardize_columns(df)
    if "remittance_usd" not in df.columns and "sender_country" not in df.columns:
        id_cols = [c for c in df.columns if c.lower() in ("country", "sender", "receiver") or c == "year"]
        if not id_cols:
            df = df.melt(id_vars=[df.columns[0]], var_name="receiver_country", value_name="remittance_usd")
            df = df.rename(columns={df.columns[0]: "sender_country"})
        else:
            df = df.melt(id_vars=[c for c in df.columns if c not in df.select_dtypes("number").columns[:1]],
                         var_name="receiver_country", value_name="remittance_usd")
    if "corridor" not in df.columns:
        df["corridor"] = df["sender_country"].astype(str) + "→" + df["receiver_country"].astype(str)
    return enforce_schema(df, "remittance_flows")


def load_imf_exchange_rates(path: Path | str | None = None) -> pd.DataFrame:
    p = Path(path) if path else _find_named("imf", ["fx_rates_from_lab.csv", "fx_rates.csv"])
    if p is None:
        p = _find_file("fx_prices")
    if p is None or not p.exists():
        warnings.warn("IMF FX file not found — using mock fx_rates.", stacklevel=2)
        return create_mock_dataset()["fx_rates"]
    df = _read_any(p)
    df = standardize_columns(df, {"fx_rate": "usd_fx_rate", "rate": "usd_fx_rate"})
    df = parse_dates(df)
    return enforce_schema(df, "fx_rates", fill_missing=True)


def load_country_sovereignty(path: Path | str | None = None) -> pd.DataFrame:
    from .sovereignty import load_country_sovereignty

    p = Path(path) if path else None
    return load_country_sovereignty(p)


def load_macro_indicators(path: Path | str | None = None) -> pd.DataFrame:
    p = Path(path) if path else _find_named("imf", ["macro_indicators.csv", "macro_indicators_wb_api.csv"])
    if p is None:
        p = _find_file("manual")
    if p is None or not p.exists():
        warnings.warn("Macro indicators file not found — using mock macro_country_panel.", stacklevel=2)
        return create_mock_dataset()["macro_country_panel"]
    df = _read_any(p)
    df = standardize_columns(df)
    df = parse_dates(df)
    return enforce_schema(df, "macro_country_panel", fill_missing=True)


def load_bis_fx_turnover(path: Path | str | None = None) -> pd.DataFrame:
    p = Path(path) if path else _find_file("bis")
    if p is None or not p.exists():
        warnings.warn("BIS FX turnover file not found — using mock currency_market_structure.", stacklevel=2)
        return create_mock_dataset()["currency_market_structure"]
    df = _read_any(p)
    df = standardize_columns(df, {"turnover": "fx_turnover_usd"})
    return enforce_schema(df, "currency_market_structure", fill_missing=True)


def load_all_canonical_tables(use_mock_fallback: bool = True) -> dict[str, pd.DataFrame]:
    """Load all five canonical tables."""
    loaders = {
        "corridor_prices": load_world_bank_rpw,
        "remittance_flows": load_knomad_remittances,
        "fx_rates": load_imf_exchange_rates,
        "macro_country_panel": load_macro_indicators,
        "currency_market_structure": load_bis_fx_turnover,
        "country_sovereignty": load_country_sovereignty,
    }
    out = {}
    for name, fn in loaders.items():
        try:
            out[name] = fn()
        except Exception:
            if name == "country_sovereignty":
                out[name] = pd.DataFrame()
            elif use_mock_fallback:
                out[name] = create_mock_dataset()[name]
            else:
                raise
    return out


def data_provenance_summary(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, df in tables.items():
        source = "unknown"
        if "source" in df.columns and df["source"].notna().any():
            source = df["source"].dropna().iloc[0]
        rows.append({"table": name, "rows": len(df), "source": source, "mock": "mock" in str(source).lower()})
    return pd.DataFrame(rows)

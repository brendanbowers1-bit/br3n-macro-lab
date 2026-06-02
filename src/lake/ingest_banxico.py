"""Ingest Banxico SIE series (USD/MXN FIX, policy rate) with FRED fallbacks."""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd

from src.lake.fred_graph import fetch_fred_graph_csv
from src.lake.paths import (
    BANXICO_POLICY_CSV,
    BANXICO_POLICY_META,
    RAW_FX,
    RAW_RATES,
    USD_MXN_SPOT_CSV,
    USD_MXN_SPOT_META,
)

SIE_BASE = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"
FX_SERIES = "SF43718"
POLICY_SERIES = "SF61745"
FRED_FX_SERIES = "DEXMXUS"
FRED_POLICY_SERIES = "IRSTCI01MXM156N"


def _banxico_token() -> str | None:
    token = os.environ.get("BANXICO_SIE_TOKEN", "").strip()
    return token or None


def _parse_banxico_date(value: str) -> pd.Timestamp:
    return pd.to_datetime(value, format="%d/%m/%Y")


def _fetch_sie_series(series_id: str, start: str, end: str, token: str) -> pd.DataFrame:
    path = f"{SIE_BASE}/{series_id}/datos/{start}/{end}"
    url = f"{path}?token={quote(token)}"
    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    rows = payload.get("bmx", {}).get("series", [])
    if not rows:
        return pd.DataFrame(columns=["date", "value"])
    datos = rows[0].get("datos", [])
    out = []
    for row in datos:
        raw = row.get("dato")
        if raw in (None, "", "N/E"):
            continue
        out.append({"date": _parse_banxico_date(row["fecha"]), "value": float(raw)})
    return pd.DataFrame(out).sort_values("date").reset_index(drop=True)


def _write_raw_csv(
    *,
    dated_path: Path,
    pointer_path: Path,
    meta_path: Path,
    content: str,
    meta: dict,
) -> Path:
    dated_path.parent.mkdir(parents=True, exist_ok=True)
    dated_path.write_text(content, encoding="utf-8")
    pointer_path.write_text(content, encoding="utf-8")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return dated_path


def ingest_usd_mxn_spot(*, min_date: str = "2024-01-01") -> Path:
    """Ingest USD/MXN spot to data-lake/raw/fx/. Prefers Banxico FIX; falls back to FRED DEXMXUS."""
    RAW_FX.mkdir(parents=True, exist_ok=True)
    end = date.today().isoformat()
    token = _banxico_token()
    retrieval_method = "fred_public_graph_csv"
    data_mode = "live"
    source_id = "fx_usd_mxn_spot"
    fred_series = FRED_FX_SERIES
    banxico_series = FX_SERIES

    df = pd.DataFrame()
    if token:
        try:
            df = _fetch_sie_series(FX_SERIES, min_date, end, token)
            if not df.empty:
                retrieval_method = "banxico_sie_api"
                fred_series = None
        except (HTTPError, URLError, KeyError, ValueError, json.JSONDecodeError):
            df = pd.DataFrame()

    if df.empty:
        csv_text = fetch_fred_graph_csv(FRED_FX_SERIES, min_date=min_date)
        raw = pd.read_csv(pd.io.common.StringIO(csv_text))
        date_col = raw.columns[0]
        val_col = raw.columns[1]
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(raw[date_col]),
                "value": pd.to_numeric(raw[val_col], errors="coerce"),
            }
        ).dropna()

    out = df.rename(columns={"value": "usd_mxn_spot"})
    lines = ["date,usd_mxn_spot"]
    for _, row in out.iterrows():
        lines.append(f"{row['date'].date()},{row['usd_mxn_spot']:.4f}")
    content = "\n".join(lines) + "\n"

    dated_name = f"usd_mxn_spot_{date.today().strftime('%Y%m%d')}.csv"
    dated_path = RAW_FX / dated_name
    meta = {
        "source_id": source_id,
        "source_name": "USD/MXN spot rate",
        "banxico_series": banxico_series,
        "fred_series": fred_series,
        "retrieval_date": date.today().isoformat(),
        "retrieval_method": retrieval_method,
        "data_mode": data_mode,
        "synthetic_flag": False,
        "license_terms_note": "Banxico SIE or FRED DEXMXUS — research use; verify terms for production.",
        "raw_dated_file": dated_name,
        "min_date_filter": min_date,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }
    return _write_raw_csv(
        dated_path=dated_path,
        pointer_path=USD_MXN_SPOT_CSV,
        meta_path=USD_MXN_SPOT_META,
        content=content,
        meta=meta,
    )


def ingest_banxico_policy_rate(*, min_date: str = "2024-01-01") -> Path:
    """Ingest Banxico policy rate to data-lake/raw/rates/. Prefers SIE SF61745; falls back to FRED monthly proxy."""
    RAW_RATES.mkdir(parents=True, exist_ok=True)
    end = date.today().isoformat()
    token = _banxico_token()
    retrieval_method = "fred_public_graph_csv"
    data_mode = "mixed"
    fred_series = FRED_POLICY_SERIES
    banxico_series = POLICY_SERIES

    df = pd.DataFrame()
    if token:
        try:
            df = _fetch_sie_series(POLICY_SERIES, min_date, end, token)
            if not df.empty:
                retrieval_method = "banxico_sie_api"
                data_mode = "live"
                fred_series = None
        except (HTTPError, URLError, KeyError, ValueError, json.JSONDecodeError):
            df = pd.DataFrame()

    if df.empty:
        csv_text = fetch_fred_graph_csv(FRED_POLICY_SERIES, min_date=min_date)
        raw = pd.read_csv(pd.io.common.StringIO(csv_text))
        date_col = raw.columns[0]
        val_col = raw.columns[1]
        monthly = pd.DataFrame(
            {
                "date": pd.to_datetime(raw[date_col]),
                "value": pd.to_numeric(raw[val_col], errors="coerce"),
            }
        ).dropna()
        # Expand monthly OECD overnight proxy to daily spine with forward-fill.
        start = monthly["date"].min()
        end_ts = monthly["date"].max()
        daily = pd.date_range(start=start, end=end_ts, freq="D")
        series = monthly.set_index("date")["value"].sort_index()
        df = pd.DataFrame({"date": daily, "value": series.reindex(daily, method="ffill").to_numpy()})

    out = df.rename(columns={"value": "mx_policy_rate"})
    lines = ["date,mx_policy_rate"]
    for _, row in out.iterrows():
        lines.append(f"{row['date'].date()},{row['mx_policy_rate']:.4f}")
    content = "\n".join(lines) + "\n"

    dated_name = f"banxico_policy_rate_{date.today().strftime('%Y%m%d')}.csv"
    dated_path = RAW_RATES / dated_name
    meta = {
        "source_id": "rates_banxico_policy",
        "source_name": "Banxico policy rate",
        "banxico_series": banxico_series,
        "fred_series": fred_series,
        "retrieval_date": date.today().isoformat(),
        "retrieval_method": retrieval_method,
        "data_mode": data_mode,
        "synthetic_flag": False,
        "license_terms_note": "Banxico SIE target rate or FRED OECD overnight proxy — research only.",
        "raw_dated_file": dated_name,
        "min_date_filter": min_date,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }
    return _write_raw_csv(
        dated_path=dated_path,
        pointer_path=BANXICO_POLICY_CSV,
        meta_path=BANXICO_POLICY_META,
        content=content,
        meta=meta,
    )

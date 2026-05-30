"""
Tier 2 Bloomberg data loader (professional market data).

Requires a licensed Bloomberg Terminal or B-PIPE account.
This module does NOT provide Bloomberg access — you must have your own subscription.

Setup:
  1. Install Bloomberg Terminal (Mac/Windows) OR B-PIPE server access
  2. pip install xbbg          # easiest if Terminal is on same machine
     OR install blpapi from Bloomberg SDK + pip install pdblp

Common USD/MXN tickers:
  - USDMXN Curncy   (spot)
  - MXN Curncy      (alternate)

Fields for research:
  - PX_LAST, BID, ASK (spot)
  - PX_LAST on forward tickers for forward points (later)
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

from .data_loader import attach_source_metadata, _trim_years

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_USDMXN_TICKER = "USDMXN Curncy"
DEFAULT_FIELDS = ["PX_LAST", "BID", "ASK"]


class BloombergNotAvailableError(RuntimeError):
    """Raised when Bloomberg API is not installed or Terminal is not running."""


def check_bloomberg_available() -> dict:
    """
    Probe for Bloomberg connectivity.

    Returns dict with keys: available, method, message
    """
    # xbbg (Terminal on same machine)
    try:
        from xbbg import blp  # noqa: F401

        return {
            "available": True,
            "method": "xbbg",
            "message": "xbbg installed — ensure Bloomberg Terminal is running and logged in.",
        }
    except ImportError:
        pass

    # blpapi (official SDK)
    try:
        import blpapi  # noqa: F401

        return {
            "available": True,
            "method": "blpapi",
            "message": "blpapi installed — ensure Bloomberg session can connect.",
        }
    except ImportError:
        pass

    return {
        "available": False,
        "method": None,
        "message": (
            "Bloomberg not available. You need:\n"
            "  1. Bloomberg Terminal or B-PIPE subscription (~$2k+/month institutional)\n"
            "  2. pip install xbbg  (Terminal on same machine)\n"
            "     OR Bloomberg blpapi SDK + pip install pdblp\n"
            "  3. Terminal running and logged in before fetching data\n"
            "See docs/BLOOMBERG_SETUP.md for full setup."
        ),
    }


def _fetch_via_xbbg(
    ticker: str,
    fields: List[str],
    years: int,
) -> pd.DataFrame:
    from xbbg import blp

    end = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(years=years)
    raw = blp.bdh(ticker, fields, start_date=start, end_date=end)
    if raw is None or raw.empty:
        raise RuntimeError(f"Bloomberg returned no data for {ticker}")

    raw.index = pd.to_datetime(raw.index)
    raw.index.name = "date"

    # xbbg returns MultiIndex columns (ticker, field) or flat depending on version
    if isinstance(raw.columns, pd.MultiIndex):
        px = raw[(ticker, "PX_LAST")] if (ticker, "PX_LAST") in raw.columns else raw.iloc[:, 0]
        out = pd.DataFrame({"price": px})
        if (ticker, "BID") in raw.columns:
            out["bid"] = raw[(ticker, "BID")]
        if (ticker, "ASK") in raw.columns:
            out["ask"] = raw[(ticker, "ASK")]
    else:
        col = "PX_LAST" if "PX_LAST" in raw.columns else raw.columns[0]
        out = pd.DataFrame({"price": raw[col]})
        for f in ("BID", "ASK"):
            if f in raw.columns:
                out[f.lower()] = raw[f]

    out = out.dropna(subset=["price"]).sort_index()
    if "bid" in out.columns and "ask" in out.columns:
        out["spread_bps"] = (out["ask"] - out["bid"]) / out["price"] * 10_000
    return out


def _fetch_via_blpapi(
    ticker: str,
    fields: List[str],
    years: int,
    host: str = "localhost",
    port: int = 8194,
) -> pd.DataFrame:
    """Minimal blpapi historical fetch (//blp/refdata)."""
    import blpapi

    end = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(years=years)

    session_opts = blpapi.SessionOptions()
    session_opts.setServerHost(host)
    session_opts.setServerPort(port)
    session = blpapi.Session(session_opts)
    if not session.start():
        raise BloombergNotAvailableError("blpapi session failed to start — is Terminal running?")
    if not session.openService("//blp/refdata"):
        raise BloombergNotAvailableError("Could not open //blp/refdata")

    service = session.getService("//blp/refdata")
    request = service.createRequest("HistoricalDataRequest")
    request.getElement("securities").appendValue(ticker)
    for f in fields:
        request.getElement("fields").appendValue(f)
    request.set("startDate", start.strftime("%Y%m%d"))
    request.set("endDate", end.strftime("%Y%m%d"))
    request.set("periodicitySelection", "DAILY")

    session.sendRequest(request)

    rows = []
    while True:
        event = session.nextEvent(5000)
        for msg in event:
            if msg.hasElement("securityData"):
                sec = msg.getElement("securityData")
                fd = sec.getElement("fieldData")
                for i in range(fd.numValues()):
                    bar = fd.getValue(i)
                    dt = bar.getElementAsDatetime("date")
                    row = {"date": pd.Timestamp(dt.year, dt.month, dt.day)}
                    for f in fields:
                        if bar.hasElement(f):
                            row[f.lower() if f != "PX_LAST" else "price"] = bar.getElementAsFloat(f)
                    rows.append(row)
        if event.eventType() == blpapi.Event.RESPONSE:
            break

    session.stop()
    if not rows:
        raise RuntimeError(f"blpapi returned no rows for {ticker}")

    df = pd.DataFrame(rows).set_index("date").sort_index()
    if "px_last" in df.columns and "price" not in df.columns:
        df = df.rename(columns={"px_last": "price"})
    if "bid" in df.columns and "ask" in df.columns:
        df["spread_bps"] = (df["ask"] - df["bid"]) / df["price"] * 10_000
    return df


def fetch_bloomberg_spot(
    ticker: str = DEFAULT_USDMXN_TICKER,
    years: int = 25,
    fields: Optional[List[str]] = None,
    host: str = "localhost",
    port: int = 8194,
) -> pd.DataFrame:
    """
    Fetch historical spot (and optional bid/ask) from Bloomberg.

    Tier 2 — professional market data. Not publishable without Bloomberg license terms.
    """
    fields = fields or DEFAULT_FIELDS
    probe = check_bloomberg_available()
    if not probe["available"]:
        raise BloombergNotAvailableError(probe["message"])

    if probe["method"] == "xbbg":
        df = _fetch_via_xbbg(ticker, fields, years)
    else:
        df = _fetch_via_blpapi(ticker, fields, years, host=host, port=port)

    df = _trim_years(df, years)
    return attach_source_metadata(
        df,
        source="bloomberg",
        tier_number=2,
        price_type="PX_LAST",
        convention=ticker,
    )


def load_or_fetch_bloomberg_usdmxn(
    years: int = 25,
    ticker: str = DEFAULT_USDMXN_TICKER,
    force_refresh: bool = False,
    host: str = "localhost",
    port: int = 8194,
) -> Tuple[pd.DataFrame, Path]:
    """Load cached Tier 2 Bloomberg USD/MXN or fetch live."""
    proc_dir = ROOT / "data" / "processed"
    proc_dir.mkdir(parents=True, exist_ok=True)
    safe = ticker.replace(" ", "_").lower()
    path = proc_dir / f"{safe}_bloomberg_tier2.csv"

    if path.exists() and not force_refresh:
        cached = pd.read_csv(path, parse_dates=[0], index_col=0)
        cached.index.name = "date"
        return cached, path

    df = fetch_bloomberg_spot(ticker=ticker, years=years, host=host, port=port)
    df.to_csv(path)
    print(
        f"Saved Tier 2 Bloomberg {ticker}: {len(df)} rows -> {path} "
        f"({df.index.min().date()} to {df.index.max().date()})"
    )
    return df, path

#!/usr/bin/env python3
"""
Compare FRED H.10 vs yfinance USD/MXN and write upgrade report.

Research only — does not claim trading-grade data.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src.data_loader import fetch_yfinance, load_config
from src.data_sources import export_data_source_registry
from src.official_data_loader import load_usdmxn_fred_h10


def _series_from_df(df: pd.DataFrame, source_label: str) -> pd.Series:
    if "date" in df.columns:
        out = df.set_index("date")
    else:
        out = df.copy()
    out.index = pd.to_datetime(out.index)
    s = pd.to_numeric(out["price"], errors="coerce").dropna()
    s.name = source_label
    return s.sort_index()


def compare_sources(fred: pd.Series, yf: pd.Series) -> dict:
    overlap = fred.index.intersection(yf.index)
    row = {
        "fred_observations": len(fred),
        "yfinance_observations": len(yf),
        "fred_start": str(fred.index.min().date()) if len(fred) else None,
        "fred_end": str(fred.index.max().date()) if len(fred) else None,
        "yfinance_start": str(yf.index.min().date()) if len(yf) else None,
        "yfinance_end": str(yf.index.max().date()) if len(yf) else None,
        "fred_missing": int(fred.isna().sum()),
        "yfinance_missing": int(yf.isna().sum()),
        "fred_latest_price": round(float(fred.iloc[-1]), 6) if len(fred) else None,
        "yfinance_latest_price": round(float(yf.iloc[-1]), 6) if len(yf) else None,
        "overlap_days": len(overlap),
    }

    if len(overlap) >= 10:
        f = fred.reindex(overlap)
        y = yf.reindex(overlap)
        ret_f = f.pct_change().dropna()
        ret_y = y.pct_change().dropna()
        common = ret_f.index.intersection(ret_y.index)
        if len(common) >= 5:
            rf = ret_f.reindex(common)
            ry = ret_y.reindex(common)
            corr = float(rf.corr(ry))
            max_diff = float((rf - ry).abs().max())
            row["daily_return_correlation"] = round(corr, 6)
            row["max_abs_daily_return_diff"] = round(max_diff, 6)
            row["agree_closely"] = corr >= 0.95 and max_diff <= 0.05
        else:
            row["daily_return_correlation"] = None
            row["max_abs_daily_return_diff"] = None
            row["agree_closely"] = False
    else:
        row["daily_return_correlation"] = None
        row["max_abs_daily_return_diff"] = None
        row["agree_closely"] = False

    return row


def write_report_md(
    fred_ok: bool,
    yf_ok: bool,
    cmp_row: dict,
    fred_err: str,
    yf_err: str,
) -> Path:
    path = ROOT / "reports" / "DATA_UPGRADE_REPORT.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    agree = cmp_row.get("agree_closely")
    corr = cmp_row.get("daily_return_correlation")
    source_of_truth = "FRED H.10 (DEXMXUS)" if fred_ok else ("yfinance (prototype fallback)" if yf_ok else "none")

    lines = [
        "# FX Lab Data Upgrade Report",
        "",
        f"_Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')} UTC_",
        "",
        "## Source load status",
        "",
        f"- **FRED H.10 USD/MXN:** {'SUCCESS' if fred_ok else 'FAILED'}",
    ]
    if not fred_ok:
        lines.append(f"  - Error: {fred_err}")
    lines.append(f"- **yfinance USDMXN=X:** {'SUCCESS' if yf_ok else 'FAILED'}")
    if not yf_ok:
        lines.append(f"  - Error: {yf_err}")

    lines.extend([
        "",
        "## Comparison (USD/MXN)",
        "",
        f"| Metric | FRED H.10 | yfinance |",
        f"|--------|-----------|----------|",
        f"| Observations | {cmp_row.get('fred_observations', '—')} | {cmp_row.get('yfinance_observations', '—')} |",
        f"| Start | {cmp_row.get('fred_start', '—')} | {cmp_row.get('yfinance_start', '—')} |",
        f"| End | {cmp_row.get('fred_end', '—')} | {cmp_row.get('yfinance_end', '—')} |",
        f"| Missing values | {cmp_row.get('fred_missing', '—')} | {cmp_row.get('yfinance_missing', '—')} |",
        f"| Latest price | {cmp_row.get('fred_latest_price', '—')} | {cmp_row.get('yfinance_latest_price', '—')} |",
        "",
        f"- **Overlap days:** {cmp_row.get('overlap_days', '—')}",
        f"- **Daily return correlation:** {corr if corr is not None else '—'}",
        f"- **Max |daily return diff|:** {cmp_row.get('max_abs_daily_return_diff', '—')}",
        f"- **Agree closely:** {'Yes' if agree else 'No'}",
        "",
        "## Source of truth",
        "",
        f"**{source_of_truth}**",
        "",
        "FRED/Fed H.10 is academic-grade public data suitable for research memos. "
        "yfinance is prototype data — good for development, not sufficient alone for academic claims.",
        "",
        "## Still missing for academic claims",
        "",
        "- Forward points and cross-currency basis",
        "- Bid/ask spreads and executable close conventions",
        "- Independent validation against Banxico fix (optional cross-check)",
        "- Documented missing-value policy on merged macro panels",
        "",
        "## Still missing for trading / hedging claims",
        "",
        "- Bid/ask and effective spread by tenor",
        "- Forward points, roll, and carry at executable levels",
        "- Transaction cost distributions from real executions",
        "- Options implied volatility surfaces",
        "- Proprietary payment-flow data (requires authorization)",
        "",
        "## Limitations",
        "",
        "This lab does **not** claim trading-ready or publication-grade models until "
        "official data is used consistently and hedge economics include forward costs.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    cfg = load_config()
    years = int(cfg["data"]["history_years"])

    export_data_source_registry()

    fred_ok = False
    yf_ok = False
    fred_err = ""
    yf_err = ""
    fred_s = pd.Series(dtype=float)
    yf_s = pd.Series(dtype=float)

    try:
        fred_df = load_usdmxn_fred_h10(years=years)
        fred_s = _series_from_df(fred_df, "fred_h10")
        fred_ok = len(fred_s) > 0
    except Exception as exc:
        fred_err = str(exc)

    try:
        yf_df = fetch_yfinance("USDMXN=X", years)
        yf_s = _series_from_df(yf_df, "yfinance")
        yf_ok = len(yf_s) > 0
    except Exception as exc:
        yf_err = str(exc)

    cmp_row = compare_sources(fred_s, yf_s) if fred_ok or yf_ok else {}
    cmp_row["fred_loaded"] = fred_ok
    cmp_row["yfinance_loaded"] = yf_ok
    cmp_row["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    out_path = ROOT / "data" / "outputs" / "data_source_comparison_usdmxn.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([cmp_row]).to_csv(out_path, index=False)

    report_path = write_report_md(fred_ok, yf_ok, cmp_row, fred_err, yf_err)

    print("\nBowers Frontier Macro Labs — Data Upgrade Report")
    print("=" * 50)
    print(f"FRED H.10 loaded:     {fred_ok}")
    print(f"yfinance loaded:      {yf_ok}")
    if cmp_row.get("daily_return_correlation") is not None:
        print(f"Return correlation:   {cmp_row['daily_return_correlation']}")
        print(f"Max return diff:      {cmp_row['max_abs_daily_return_diff']}")
        print(f"Agree closely:        {cmp_row.get('agree_closely')}")
    print(f"Comparison CSV:       {out_path}")
    print(f"Report:               {report_path}")


if __name__ == "__main__":
    main()

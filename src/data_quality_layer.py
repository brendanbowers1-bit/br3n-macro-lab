"""
Explicit data-quality layer — manifest of all series used in Bowers Frontier Macro Labs FX research.

Records source, tier, quality flag, and role for each dataset in the stack.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml

from .data_quality import run_data_quality_checks, save_data_quality_report
from .data_sources import export_data_source_registry, tier_number_to_label

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "outputs"


def _load_cfg() -> dict:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _read_price_series(path: Path, price_col: str = "price") -> Optional[pd.DataFrame]:
    if not path.exists():
        return None
    df = pd.read_csv(path, parse_dates=[0], index_col=0)
    df.index.name = "date"
    if price_col not in df.columns and "close" in df.columns:
        df = df.rename(columns={"close": "price"})
    return df


def _infer_source(df: pd.DataFrame, default: str) -> str:
    if "source" in df.columns and df["source"].notna().any():
        return str(df["source"].dropna().iloc[-1])
    return default


def build_data_quality_manifest(cfg: Optional[dict] = None) -> pd.DataFrame:
    """
    Audit all primary datasets and return a manifest dataframe.

    Columns include role, source, tier, quality flag, and observation counts.
    """
    cfg = cfg or _load_cfg()
    rows: List[Dict[str, Any]] = []

    series_specs = [
        {
            "role": "primary_spot",
            "label": "USD/MXN spot (primary pipeline)",
            "path": ROOT / "data" / "processed" / "USDMXN_X.csv",
            "default_source": "yfinance",
        },
        {
            "role": "official_spot",
            "label": "USD/MXN spot (FRED H.10 Tier 1)",
            "path": ROOT / "data" / "processed" / "USDMXN_X_official_tier1.csv",
            "default_source": "fed_h10",
        },
        {
            "role": "features_regimes",
            "label": "USD/MXN features + regimes",
            "path": ROOT / "data" / "processed" / "usdmxn_features_regimes.csv",
            "default_source": "pipeline",
            "date_col": "date",
        },
        {
            "role": "macro_panel",
            "label": "Macro context panel (FRED + Yahoo)",
            "path": ROOT / "data" / "processed" / "macro_panel.csv",
            "default_source": "fred_yahoo_mix",
            "price_col": "dxy",
        },
        {
            "role": "bis_eer",
            "label": "BIS Mexico nominal broad EER",
            "path": ROOT / "data" / "processed" / "bis_eer_mexico.csv",
            "default_source": "bis_eer",
        },
    ]

    for spec in series_specs:
        path = spec["path"]
        if not path.exists():
            rows.append(
                {
                    "role": spec["role"],
                    "label": spec["label"],
                    "path": str(path.relative_to(ROOT)),
                    "source_name": spec["default_source"],
                    "tier_number": None,
                    "tier_label": "missing",
                    "observation_count": 0,
                    "start_date": None,
                    "end_date": None,
                    "data_quality_flag": "MISSING",
                    "missing_price_pct": None,
                    "suspicious_return_count": None,
                    "notes": "File not found — run data fetch pipeline",
                }
            )
            continue

        if spec.get("date_col") == "date":
            raw = pd.read_csv(path, parse_dates=["date"])
            df = raw.set_index("date")
            price_col = "price" if "price" in df.columns else "close"
        else:
            df = _read_price_series(path, spec.get("price_col", "price"))
            price_col = spec.get("price_col", "price")
            if price_col not in df.columns:
                price_col = df.columns[0]

        source = _infer_source(df, spec["default_source"])
        report = run_data_quality_checks(df, source_name=source, price_col=price_col)
        rows.append(
            {
                "role": spec["role"],
                "label": spec["label"],
                "path": str(path.relative_to(ROOT)),
                "source_name": report["source_name"],
                "tier_number": report.get("tier_number"),
                "tier_label": report.get("tier_label", report.get("data_tier")),
                "observation_count": report["observation_count"],
                "start_date": report["start_date"],
                "end_date": report["end_date"],
                "data_quality_flag": report["data_quality_flag"],
                "missing_price_pct": report["missing_price_pct"],
                "suspicious_return_count": report["suspicious_return_count"],
                "notes": "",
            }
        )

    # Corridor download log
    dl_path = OUT / "corridor_download_log.csv"
    if dl_path.exists():
        dl = pd.read_csv(dl_path)
        for _, r in dl.iterrows():
            cid = r.get("corridor_id", "unknown")
            rows.append(
                {
                    "role": "corridor_spot",
                    "label": f"Corridor {cid} spot",
                    "path": str(r.get("processed_path", "")),
                    "source_name": r.get("source", "yfinance"),
                    "tier_number": 4,
                    "tier_label": tier_number_to_label(4),
                    "observation_count": r.get("rows", 0),
                    "start_date": r.get("start_date"),
                    "end_date": r.get("end_date"),
                    "data_quality_flag": r.get("status", "UNKNOWN"),
                    "missing_price_pct": None,
                    "suspicious_return_count": None,
                    "notes": r.get("notes", ""),
                }
            )

    manifest = pd.DataFrame(rows)
    manifest["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return manifest


def save_data_quality_layer(cfg: Optional[dict] = None) -> Dict[str, Path]:
    """Build manifest, save CSV, update primary quality report, export registry."""
    cfg = cfg or _load_cfg()
    OUT.mkdir(parents=True, exist_ok=True)

    manifest = build_data_quality_manifest(cfg)
    manifest_path = OUT / "data_quality_manifest.csv"
    manifest.to_csv(manifest_path, index=False)

    # Primary spot row for backward-compatible single-row report
    primary = manifest[manifest["role"] == "primary_spot"]
    if primary.empty:
        primary = manifest[manifest["role"] == "official_spot"]
    if not primary.empty:
        row = primary.iloc[0]
        save_data_quality_report(
            {
                "source_name": row["source_name"],
                "tier_number": row["tier_number"],
                "tier_label": row["tier_label"],
                "observation_count": row["observation_count"],
                "start_date": row["start_date"],
                "end_date": row["end_date"],
                "missing_price_pct": row["missing_price_pct"],
                "suspicious_return_count": row["suspicious_return_count"],
                "data_quality_flag": row["data_quality_flag"],
            },
            OUT / "data_quality_report.csv",
        )

    registry_path = export_data_source_registry(OUT / "data_source_registry.csv")

    # Layer summary for dashboard
    tier_counts = manifest.groupby("tier_label")["role"].count().to_dict() if not manifest.empty else {}
    flags = manifest["data_quality_flag"].value_counts().to_dict() if not manifest.empty else {}
    prefer_t1 = cfg.get("data", {}).get("prefer_tier1_spot", False)

    summary_lines = [
        "# Data Quality Layer Summary",
        "",
        f"**Generated:** {datetime.now():%Y-%m-%d %H:%M UTC}",
        "",
        "## Stack Policy",
        "",
        f"- **Primary spot tier preference:** {'Tier 1 (FRED H.10)' if prefer_t1 else 'Tier 4 (yfinance/Stooq) with Tier 1 comparison'}",
        "- **Macro:** FRED rates + Yahoo VIX/DXY (FRED broad dollar when configured)",
        "- **Corridor context:** BIS EER where available",
        "",
        "## Quality Flags",
        "",
    ]
    for flag, count in sorted(flags.items()):
        summary_lines.append(f"- **{flag}:** {count} series")
    summary_lines.extend(["", "## Tier Coverage", ""])
    for tier, count in sorted(tier_counts.items()):
        summary_lines.append(f"- **{tier}:** {count} series")
    summary_lines.extend(
        [
            "",
            "## Principle",
            "",
            "Every research claim must record **source**, **tier**, and **quality flag**. "
            "Prototype data (Tier 4) supports development; official data (Tier 1) supports publication.",
            "",
        ]
    )

    summary_path = ROOT / "reports" / "DATA_QUALITY_LAYER.md"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

    return {
        "manifest": manifest_path,
        "report": OUT / "data_quality_report.csv",
        "registry": registry_path,
        "summary": summary_path,
    }

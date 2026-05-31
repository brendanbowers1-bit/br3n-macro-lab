#!/usr/bin/env python3
"""Materialize settlement raw files — official Tier-1 fetch plus curated supplements."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data.curated_bridge import (
    ECB_TARGET_STATS,
    build_documented_stress_events,
    build_finality_from_reference,
    build_payment_flows_from_rpw,
    merge_payment_flows,
)
from src.data.official_fetchers import fetch_all_official
from src.quality.lineage import calculate_file_hash
from src.utils.paths import METADATA_DIR, RAW_DIR

PARENT_RAW = ROOT.parent / "data" / "raw"


def _ensure_dirs() -> None:
    for sub in ("bis_cpmi", "world_bank", "imf", "fred", "ecb", "manual", "federal_reserve"):
        (RAW_DIR / sub).mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_parent(name: str) -> pd.DataFrame:
    p = PARENT_RAW / name
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


def _write(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"  wrote {path.relative_to(ROOT)} ({len(df)} rows)")


def build_checksum_registry() -> pd.DataFrame:
    rows = []
    for p in sorted(RAW_DIR.rglob("*")):
        if p.is_file() and p.suffix in (".csv", ".xlsx"):
            rows.append({
                "file_path": str(p.relative_to(ROOT)),
                "sha256": calculate_file_hash(p),
                "bytes": p.stat().st_size,
            })
    return pd.DataFrame(rows)


def _supplement_rpw_corridors() -> None:
    """Add RPW remittance corridors to official CPMI payment flows."""
    official = RAW_DIR / "bis_cpmi" / "cpmi_payment_systems.csv"
    rpw = _read_parent("world_bank_rpw/rpw_historical_panel.csv")
    if rpw.empty:
        return
    rpw_flows = build_payment_flows_from_rpw(rpw)
    if rpw_flows.empty:
        return
    if official.exists():
        base = pd.read_csv(official)
        combined = merge_payment_flows(base, rpw_flows)
    else:
        combined = rpw_flows
    _write(combined, official if official.exists() else RAW_DIR / "bis_cpmi" / "cpmi_payment_systems.csv")


def main() -> None:
    print("BR3N Settlement Lab — fetch official + curated data")
    _ensure_dirs()

    print("\n▶ Tier-1 official sources (BIS CPMI, FRED, Findex, merchant fees)")
    results = fetch_all_official(RAW_DIR)
    for key, val in results.items():
        if key not in ("errors", "fetched_at"):
            print(f"  {key}: {val}")
    if results.get("errors"):
        print("  warnings:", results["errors"])

    print("\n▶ Supplements (RPW corridors, ECB, finality, stress events)")
    _supplement_rpw_corridors()
    _write(pd.DataFrame(ECB_TARGET_STATS), RAW_DIR / "ecb" / "target_statistics_curated.csv")
    _write(build_finality_from_reference(), RAW_DIR / "manual" / "finality_legal_reference.csv")
    _write(build_documented_stress_events(), RAW_DIR / "bis_cpmi" / "documented_stress_events.csv")

    # Cost-of-capital assumption from live SOFR when available.
    sofr_path = RAW_DIR / "fred" / "sofr.csv"
    coc = 0.05
    if sofr_path.exists():
        sofr = pd.read_csv(sofr_path)
        if "value_pct" in sofr.columns and not sofr.empty:
            coc = float(sofr["value_pct"].iloc[-1])
    assumptions = pd.DataFrame([
        {"assumption_id": "cost_of_capital_baseline", "value": coc, "unit": "annual_pct",
         "source": "fred/SOFR", "notes": "Latest SOFR from FRED; used in SDI/OLB"},
        {"assumption_id": "fx_exposure_haircut", "value": 0.1, "unit": "ratio",
         "source": "manual_assumptions", "notes": "FX exposure scaling for SDI risk-adjusted spec"},
    ])
    _write(assumptions, RAW_DIR / "manual" / "settlement_assumptions.csv")

    checksums = build_checksum_registry()
    checksum_path = METADATA_DIR / "file_checksums.csv"
    checksums.to_csv(checksum_path, index=False)
    print(f"\n  wrote {checksum_path.relative_to(ROOT)} ({len(checksums)} files)")
    print("\nFetch complete. Run reproduce_settlement_lab.py next.")


if __name__ == "__main__":
    main()

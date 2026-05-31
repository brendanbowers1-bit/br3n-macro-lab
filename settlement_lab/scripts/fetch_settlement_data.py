#!/usr/bin/env python3
"""Materialize curated settlement raw files from parent-lab official caches."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data.curated_bridge import (
    ECB_TARGET_STATS,
    build_access_from_macro,
    build_documented_stress_events,
    build_finality_from_reference,
    build_liquidity_from_bis,
    build_liquidity_from_ecb,
    build_payment_flows_from_cpmi,
    build_payment_flows_from_rpw,
    estimate_cost_of_capital,
    merge_payment_flows,
)
from src.quality.lineage import calculate_file_hash
from src.utils.paths import METADATA_DIR, RAW_DIR

PARENT_RAW = ROOT.parent / "data" / "raw"


def _ensure_dirs() -> None:
    for sub in ("bis_cpmi", "world_bank", "imf", "fred", "ecb", "manual"):
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
    for p in sorted(RAW_DIR.rglob("*.csv")):
        rows.append({
            "file_path": str(p.relative_to(ROOT)),
            "sha256": calculate_file_hash(p),
            "bytes": p.stat().st_size,
        })
    return pd.DataFrame(rows)


def main() -> None:
    print("BR3N Settlement Lab — fetch curated data")
    _ensure_dirs()

    rpw = _read_parent("world_bank_rpw/rpw_historical_panel.csv")
    bis = _read_parent("bis/fx_turnover_2022.csv")
    macro = _read_parent("imf/macro_indicators_wb_api.csv")
    dxy = _read_parent("fred/dxy_daily.csv")

    coc = estimate_cost_of_capital(macro, dxy)

    cpmi_flows = build_payment_flows_from_cpmi()
    rpw_flows = build_payment_flows_from_rpw(rpw)
    flows = merge_payment_flows(cpmi_flows, rpw_flows)
    _write(flows, RAW_DIR / "bis_cpmi" / "cpmi_payment_systems_curated.csv")

    liq_bis = build_liquidity_from_bis(bis, cost_of_capital=coc)
    liq_ecb = build_liquidity_from_ecb(cost_of_capital=max(0.03, coc - 0.01))
    liq = pd.concat([liq_bis, liq_ecb], ignore_index=True) if not liq_bis.empty else liq_ecb
    _write(liq, RAW_DIR / "bis_cpmi" / "settlement_liquidity_curated.csv")

    _write(pd.DataFrame(ECB_TARGET_STATS), RAW_DIR / "ecb" / "target_statistics_curated.csv")

    finality = build_finality_from_reference()
    _write(finality, RAW_DIR / "manual" / "finality_legal_reference.csv")

    access = build_access_from_macro(macro)
    _write(access, RAW_DIR / "world_bank" / "findex_indicators_curated.csv")

    stress = build_documented_stress_events()
    _write(stress, RAW_DIR / "bis_cpmi" / "documented_stress_events.csv")

    sofr_rows = pd.DataFrame([{
        "date": pd.Timestamp.today().strftime("%Y-%m-%d"),
        "series": "SOFR_proxy",
        "value_pct": coc,
        "source": "imf_macro_policy_rate_or_dxy_stress_proxy",
    }])
    _write(sofr_rows, RAW_DIR / "fred" / "sofr_curated.csv")

    assumptions = pd.DataFrame([
        {"assumption_id": "cost_of_capital_baseline", "value": coc, "unit": "annual_pct",
         "source": "fred/imf_proxy", "notes": "Used in SDI/OLB capital cost component"},
        {"assumption_id": "fx_exposure_haircut", "value": 0.1, "unit": "ratio",
         "source": "manual_assumptions", "notes": "FX exposure scaling for SDI risk-adjusted spec"},
    ])
    _write(assumptions, RAW_DIR / "manual" / "settlement_assumptions.csv")

    checksums = build_checksum_registry()
    checksum_path = METADATA_DIR / "file_checksums.csv"
    checksums.to_csv(checksum_path, index=False)
    print(f"  wrote {checksum_path.relative_to(ROOT)} ({len(checksums)} files)")

    print("\nFetch complete. Run reproduce_settlement_lab.py next.")


if __name__ == "__main__":
    main()

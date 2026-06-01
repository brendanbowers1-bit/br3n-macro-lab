#!/usr/bin/env python3
"""Fetch Tier 1–3 official stablecoin data into stablecoin_lab/data/raw/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.data.curated_bridge import build_remittance_comparison_from_rpw, build_redemption_from_attestations
from src.data.official_fetchers import fetch_all_official
from src.quality.lineage import calculate_file_hash
from src.utils.paths import METADATA_DIR, RAW_DIR

PARENT_RAW = ROOT.parent / "data" / "raw"


def _ensure_dirs() -> None:
    for sub in (
        "stablecoin_supply", "stablecoin_prices", "stablecoin_reserves",
        "issuer_attestations", "chain_fees", "chain_finality",
        "remittance_costs", "regulatory_events", "manual",
    ):
        (RAW_DIR / sub).mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)


def _write(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        print(f"  skip (empty): {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"  wrote {path.relative_to(ROOT)} ({len(df)} rows)")


def build_checksum_registry() -> pd.DataFrame:
    rows = []
    for fp in sorted(RAW_DIR.rglob("*.csv")):
        rel = str(fp.relative_to(ROOT))
        rows.append({
            "file_path": rel,
            "sha256": calculate_file_hash(fp),
            "size_bytes": fp.stat().st_size,
        })
    return pd.DataFrame(rows)


def main() -> None:
    print("BR3N Stablecoin Lab — fetch official data")
    _ensure_dirs()
    fetched = fetch_all_official(RAW_DIR, PARENT_RAW)

    _write(fetched.get("stablecoin_supply", pd.DataFrame()), RAW_DIR / "stablecoin_supply" / "defillama_supply.csv")
    _write(fetched.get("stablecoin_price_peg", pd.DataFrame()), RAW_DIR / "stablecoin_prices" / "defillama_prices.csv")
    _write(fetched.get("issuer_attestations", pd.DataFrame()), RAW_DIR / "issuer_attestations" / "reserve_attestations.csv")
    _write(fetched.get("stablecoin_reserves", pd.DataFrame()), RAW_DIR / "stablecoin_reserves" / "reserve_attestations.csv")
    _write(fetched.get("chain_fees", pd.DataFrame()), RAW_DIR / "chain_fees" / "chain_settlement_reference.csv")
    _write(fetched.get("chain_finality", pd.DataFrame()), RAW_DIR / "chain_finality" / "chain_settlement_reference.csv")

    remittance = build_remittance_comparison_from_rpw(fetched.get("remittance_costs", pd.DataFrame()))
    _write(remittance, RAW_DIR / "remittance_costs" / "rpw_remittance_comparison.csv")

    redemption = build_redemption_from_attestations(fetched.get("issuer_attestations", pd.DataFrame()))
    _write(redemption, RAW_DIR / "manual" / "redemption_from_attestations.csv")

    _write(fetched.get("regulatory_events", pd.DataFrame()), RAW_DIR / "regulatory_events" / "official_regulatory_events.csv")
    _write(fetched.get("fed_research", pd.DataFrame()), RAW_DIR / "manual" / "fed_stablecoin_research.csv")
    _write(fetched.get("bis_tokenization", pd.DataFrame()), RAW_DIR / "manual" / "bis_tokenization_references.csv")
    _write(fetched.get("bis_cpmi_bridge", pd.DataFrame()), RAW_DIR / "manual" / "bis_cpmi_bridge.csv")

    checksums = build_checksum_registry()
    _write(checksums, METADATA_DIR / "file_checksums.csv")
    print("\nFetch complete.")


if __name__ == "__main__":
    main()

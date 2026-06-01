"""Discover raw data files in stablecoin_lab/data/raw/."""

from __future__ import annotations

from pathlib import Path

from src.utils.paths import RAW_DIR, RAW_SUBDIRS


def discover_files() -> dict[str, list[Path]]:
    found: dict[str, list[Path]] = {d: [] for d in RAW_SUBDIRS}
    if not RAW_DIR.exists():
        return found
    for sub in RAW_SUBDIRS:
        p = RAW_DIR / sub
        if p.exists():
            found[sub] = sorted(
                f for f in p.glob("**/*") if f.is_file() and f.suffix.lower() in (".csv", ".json", ".parquet")
            )[:200]
    return found


def has_real_data() -> bool:
    files = discover_files()
    return any(len(v) > 0 for k, v in files.items() if k != "manual")

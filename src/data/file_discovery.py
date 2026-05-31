"""Discover raw data files in data/raw subfolders."""

from __future__ import annotations

from pathlib import Path

from src.utils.paths import RAW_DIR


def discover_files(
    folder: str | Path,
    extensions: tuple[str, ...] = (".csv", ".xlsx", ".xls"),
) -> list[Path]:
    d = Path(folder) if Path(folder).is_absolute() else RAW_DIR / str(folder)
    if not d.exists():
        return []
    found: list[Path] = []
    for ext in extensions:
        found.extend(sorted(d.glob(f"*{ext}")))
    return found


def discover_all_sources() -> dict[str, list[Path]]:
    subfolders = [
        "world_bank_rpw",
        "world_bank_knomad",
        "imf",
        "world_bank_wdi",
        "bis",
        "fx_prices",
        "manual",
        "fred",
    ]
    return {name: discover_files(name) for name in subfolders}

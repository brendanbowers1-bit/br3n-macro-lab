#!/usr/bin/env python3
"""Apply Bowers Frontier rebrand to user-facing text across the repository."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    ".next",
    "__pycache__",
    "reports/figures",
    "data",
}

SKIP_FILES = {
    "scripts/apply_rebrand.py",
    "docs/rebrand_audit.md",
    "web_dashboard/package.json",
    "web_dashboard/package-lock.json",
    "web_dashboard/src/lib/base-path.ts",
    "web_dashboard/src/lib/theme.ts",
}

# Ordered replacements — longest / most specific first.
REPLACEMENTS: list[tuple[str, str]] = [
    ("BR3N Macro Labs — Corridor Intelligence Brief", "Bowers Frontier Macro Labs — Corridor Intelligence Brief"),
    ("BR3N Macro Labs — Model Lab", "Bowers Frontier Macro Labs — Model Lab"),
    ("BR3N Macro Labs", "Bowers Frontier Macro Labs"),
    ("BR3N MACRO LABS", "BOWERS FRONTIER MACRO LABS"),
    ("BR3N Macro Lab", "Bowers Frontier Macro Labs"),
    ("BR3N FX Lab", "Bowers Frontier FX Lab"),
    ("BR3N Model Lab", "Bowers Frontier Model Lab"),
    ("BR3N Command Center", "Bowers Frontier Command Center"),
    ("BR3N Value Survival Index", "Bowers Frontier Value Survival Index"),
    ("BR3N Settlement Economics Lab", "Bowers Frontier Settlement Economics Lab"),
    ("BR3N Stablecoin Settlement Window Lab", "Bowers Frontier Stablecoin Settlement Window Lab"),
    ("BR3N Stablecoin Settlement Lab", "Bowers Frontier Stablecoin Settlement Lab"),
    ("BR3N improvements:", "Bowers Frontier improvements:"),
    ("BR3N improvement", "Bowers Frontier improvement"),
    ("BR3N models", "Bowers Frontier models"),
    ("BR3N model", "Bowers Frontier model"),
    ("BR3N feature set", "Bowers Frontier feature set"),
    ("BR3N VSI", "Bowers Frontier VSI"),
    ("BR3N FX Lab v1", "Bowers Frontier FX Lab v1"),
    ("BR3N Studio", "Bowers Frontier Studio"),
    ("BR3N style", "Bowers Frontier institutional macro style"),
    ("BR3N luxury", "Bowers Frontier institutional macro aesthetic"),
    ("BR3N brutalist", "Bowers Frontier institutional macro aesthetic"),
    ("BR3N aesthetic", "Bowers Frontier institutional macro aesthetic"),
    ("BRΞN", "Bowers Frontier"),
    ("B|R|3|N", "Bowers Frontier"),
    ("BR3N Macro", "Bowers Frontier Macro"),
    ("BR3N", "Bowers Frontier"),
]

TEXT_EXTENSIONS = {
    ".md",
    ".py",
    ".html",
    ".tsx",
    ".ts",
    ".js",
    ".json",
    ".yml",
    ".yaml",
    ".txt",
    ".sh",
    ".css",
    ".toml",
    ".ini",
    ".skill",
}


def should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel in SKIP_FILES:
        return True
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return True
    return False


def apply_replacements(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def main() -> None:
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or should_skip(path):
            continue
        original = path.read_text(encoding="utf-8", errors="ignore")
        updated = apply_replacements(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(path.relative_to(ROOT).as_posix())
    print(f"Updated {len(changed)} files")
    for f in changed[:40]:
        print(f"  {f}")
    if len(changed) > 40:
        print(f"  ... and {len(changed) - 40} more")


if __name__ == "__main__":
    main()

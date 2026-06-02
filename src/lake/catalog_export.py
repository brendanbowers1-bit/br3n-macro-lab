"""Export data-lake/metadata/data_catalog.json for dashboard consumers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.lake.paths import DATA_CATALOG, DATA_LAKE_ROOT, METADATA_DIR, SOURCE_REGISTRY, VALIDATION_REPORTS


def _count_layer_files(layer: str) -> int:
    layer_dir = DATA_LAKE_ROOT / layer
    if not layer_dir.exists():
        return 0
    return len([p for p in layer_dir.rglob("*") if p.is_file() and p.name != ".gitkeep"])


def load_data_catalog() -> dict[str, Any]:
    if not DATA_CATALOG.exists():
        return {"catalog_version": "0", "datasets": [], "pipelines": []}
    return json.loads(DATA_CATALOG.read_text(encoding="utf-8"))


def load_source_registry_summary() -> dict[str, Any]:
    if not SOURCE_REGISTRY.exists():
        return {"sources": [], "active_count": 0}
    reg = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    sources = reg.get("sources", [])
    active = sum(1 for s in sources if s.get("data_mode") in {"live", "research_starter", "mixed"})
    by_mode: dict[str, int] = {}
    for s in sources:
        mode = str(s.get("data_mode", "unknown"))
        by_mode[mode] = by_mode.get(mode, 0) + 1
    return {
        "registry_version": reg.get("registry_version"),
        "last_updated": reg.get("last_updated"),
        "source_count": len(sources),
        "active_count": active,
        "by_data_mode": by_mode,
    }


def build_canonical_catalog_payload() -> dict[str, Any]:
    catalog = load_data_catalog()
    datasets = catalog.get("datasets", [])
    active = [d for d in datasets if d.get("status") == "active"]
    by_layer: dict[str, int] = {}
    for d in datasets:
        layer = str(d.get("layer", "unknown"))
        by_layer[layer] = by_layer.get(layer, 0) + 1

    reports = sorted(VALIDATION_REPORTS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    latest_report = reports[0].name if reports else None

    return {
        "catalog_version": catalog.get("catalog_version"),
        "product": catalog.get("product"),
        "last_updated": catalog.get("last_updated"),
        "data_lake_root": catalog.get("data_lake_root", "data-lake/"),
        "dataset_count": len(datasets),
        "active_dataset_count": len(active),
        "datasets_by_layer": by_layer,
        "datasets": datasets,
        "pipelines": catalog.get("pipelines", []),
        "source_registry": load_source_registry_summary(),
        "file_counts": {
            "raw": _count_layer_files("raw"),
            "processed": _count_layer_files("processed"),
            "metadata": len(list(METADATA_DIR.glob("*.json"))),
            "validation_reports": len(list(VALIDATION_REPORTS.glob("*.json"))),
        },
        "latest_validation_report": latest_report,
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }


def export_catalog_json(out_path: Path) -> Path:
    payload = build_canonical_catalog_payload()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path

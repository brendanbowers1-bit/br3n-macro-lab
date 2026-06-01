"""Unified data loading for BR3N Command Center dashboard."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

VSI_OUTPUTS = ROOT / "data" / "outputs"
VSI_GOLD = ROOT / "data_lake" / "gold_research" / "value_survival_index"
SETTLEMENT_OUTPUTS = ROOT / "settlement_lab" / "data" / "outputs"
STABLECOIN_OUTPUTS = ROOT / "stablecoin_lab" / "data" / "outputs"
DATA_LAKE = ROOT / "data_lake"
AUDIT_DIR = ROOT / "audit"
SNAPSHOTS = ROOT / "_snapshots"


@dataclass
class LoadResult:
    name: str
    path: str | None
    df: pd.DataFrame
    status: str  # loaded | missing | empty
    message: str = ""


@dataclass
class ModuleAvailability:
    vsi: bool = False
    settlement: bool = False
    stablecoin: bool = False
    data_lake: bool = False
    audit: bool = False


@dataclass
class DashboardData:
    vsi: dict[str, LoadResult] = field(default_factory=dict)
    settlement: dict[str, LoadResult] = field(default_factory=dict)
    stablecoin: dict[str, LoadResult] = field(default_factory=dict)
    audit: dict[str, Any] = field(default_factory=dict)
    data_lake: dict[str, Any] = field(default_factory=dict)
    modules: ModuleAvailability = field(default_factory=ModuleAvailability)
    gallery: list[dict[str, str]] = field(default_factory=list)


def safe_read_csv(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, **kwargs)
    except Exception:
        return pd.DataFrame()


def safe_read_parquet(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path, **kwargs)
    except Exception:
        return pd.DataFrame()


def _load_named(base: Path, name: str, filenames: list[str]) -> LoadResult:
    for fn in filenames:
        path = base / fn
        df = safe_read_csv(path)
        if not df.empty:
            return LoadResult(name, str(path.relative_to(ROOT)), df, "loaded")
        if path.exists():
            return LoadResult(name, str(path.relative_to(ROOT)), df, "empty", "File exists but has no rows.")
    hint = f"Run pipeline to generate: {base / filenames[0]}"
    return LoadResult(name, None, pd.DataFrame(), "missing", hint)


def detect_available_modules() -> ModuleAvailability:
    return ModuleAvailability(
        vsi=(VSI_OUTPUTS / "value_survival_outputs.csv").exists() or any(VSI_GOLD.glob("*.csv")),
        settlement=(SETTLEMENT_OUTPUTS / "settlement_drag_outputs.csv").exists(),
        stablecoin=(STABLECOIN_OUTPUTS / "stablecoin_finality_quality_outputs.csv").exists(),
        data_lake=DATA_LAKE.exists(),
        audit=(AUDIT_DIR / "test_reports" / "full_quality_report.json").exists(),
    )


def load_value_survival_data() -> dict[str, LoadResult]:
    try:
        from src.data_lake.catalog import load_vsi_from_lake
        lake_df = load_vsi_from_lake()
        if not lake_df.empty:
            primary = LoadResult("value_survival", "data_lake/gold_research/value_survival_index", lake_df, "loaded", "DuckDB gold.vsi")
        else:
            primary = _load_named(VSI_GOLD, "value_survival", ["value_survival_outputs.csv", "vsi_outputs.csv"])
            if primary.status == "missing":
                primary = _load_named(VSI_OUTPUTS, "value_survival", ["value_survival_outputs.csv"])
    except Exception:
        primary = _load_named(VSI_OUTPUTS, "value_survival", ["value_survival_outputs.csv"])
    return {
        "value_survival": primary,
        "sensitivity": _load_named(VSI_OUTPUTS, "sensitivity", ["vsi_sensitivity_results.csv", "sensitivity_results.csv"]),
        "robustness": _load_named(VSI_OUTPUTS, "robustness", ["robustness_results.csv", "vsi_rank_stability.csv"]),
        "rank_stability": _load_named(VSI_OUTPUTS, "rank_stability", ["vsi_rank_stability.csv"]),
    }


def load_settlement_data() -> dict[str, LoadResult]:
    return {
        "settlement_drag": _load_named(SETTLEMENT_OUTPUTS, "settlement_drag", ["settlement_drag_outputs.csv"]),
        "finality_quality": _load_named(SETTLEMENT_OUTPUTS, "finality_quality", ["finality_quality_outputs.csv"]),
        "operational_liquidity": _load_named(SETTLEMENT_OUTPUTS, "operational_liquidity", ["operational_liquidity_outputs.csv"]),
        "payment_fragility": _load_named(SETTLEMENT_OUTPUTS, "payment_fragility", ["payment_fragility_outputs.csv"]),
        "friction_incidence": _load_named(SETTLEMENT_OUTPUTS, "friction_incidence", ["friction_incidence_outputs.csv"]),
        "sensitivity": _load_named(SETTLEMENT_OUTPUTS, "sensitivity", ["sensitivity_results.csv"]),
        "robustness": _load_named(SETTLEMENT_OUTPUTS, "robustness", ["robustness_results.csv", "rank_stability.csv"]),
    }


def load_stablecoin_data() -> dict[str, LoadResult]:
    return {
        "finality_quality": _load_named(STABLECOIN_OUTPUTS, "finality_quality", ["stablecoin_finality_quality_outputs.csv"]),
        "swc": _load_named(STABLECOIN_OUTPUTS, "swc", ["settlement_window_compression_outputs.csv"]),
        "liquidity_transformation": _load_named(STABLECOIN_OUTPUTS, "liquidity", ["liquidity_transformation_outputs.csv"]),
        "digital_run_velocity": _load_named(STABLECOIN_OUTPUTS, "drv", ["digital_run_velocity_outputs.csv"]),
        "dollarization": _load_named(STABLECOIN_OUTPUTS, "dollarization", ["stablecoin_dollarization_outputs.csv"]),
        "singleness": _load_named(STABLECOIN_OUTPUTS, "singleness", ["tokenized_money_singleness_outputs.csv"]),
        "compliance_drag": _load_named(STABLECOIN_OUTPUTS, "compliance", ["compliance_settlement_drag_outputs.csv"]),
        "svsi": _load_named(STABLECOIN_OUTPUTS, "svsi", ["stablecoin_value_survival_outputs.csv"]),
        "sensitivity": _load_named(STABLECOIN_OUTPUTS, "sensitivity", ["stablecoin_sensitivity_results.csv", "sensitivity_results.csv"]),
        "robustness": _load_named(STABLECOIN_OUTPUTS, "robustness", ["stablecoin_robustness_results.csv", "robustness_results.csv"]),
    }


def _count_files(folder: Path, pattern: str = "*") -> int:
    if not folder.exists():
        return 0
    return len([p for p in folder.rglob(pattern) if p.is_file() and p.name != ".gitkeep"])


def load_data_lake_catalog() -> dict[str, Any]:
    bronze = DATA_LAKE / "bronze_raw"
    silver = DATA_LAKE / "silver_cleaned"
    gold = DATA_LAKE / "gold_research"
    layers = {
        "bronze_count": _count_files(bronze, "*.csv") + _count_files(bronze, "*.parquet"),
        "silver_count": _count_files(silver, "*.csv") + _count_files(silver, "*.parquet"),
        "gold_count": _count_files(gold, "*.csv") + _count_files(gold, "*.parquet"),
        "bronze_dirs": _count_files(bronze) if bronze.exists() else 0,
        "duckdb_status": "not built",
        "catalog_updated": None,
    }
    try:
        from src.data_lake.catalog import get_lake_status
        status = get_lake_status()
        layers["duckdb_status"] = "online" if status.get("duckdb_exists") else "run scripts/sync_data_lake.py"
        layers["duckdb_path"] = status.get("duckdb_path")
        layers["catalog_views"] = status.get("catalog_views", 0)
        layers["catalog_updated"] = status.get("catalog_updated")
    except Exception:
        pass
    checksum = ROOT / "stablecoin_lab" / "data" / "metadata" / "file_checksums.csv"
    if checksum.exists():
        layers["catalog_updated"] = str(checksum.stat().st_mtime)
    return layers


def load_latest_quality_report() -> dict[str, Any]:
    path = AUDIT_DIR / "test_reports" / "full_quality_report.json"
    if not path.exists():
        return {"status": "missing", "message": "Run: python scripts/run_all_quality_checks.py"}
    try:
        return {"status": "loaded", "data": json.loads(path.read_text(encoding="utf-8"))}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def load_audit_reports() -> dict[str, Any]:
    reports = {
        "quality": load_latest_quality_report(),
        "credibility_md": _read_text(AUDIT_DIR / "research_credibility_report.md"),
        "data_validation_md": _read_text(AUDIT_DIR / "data_quality_reports" / "data_validation_report.md"),
        "model_validation_md": _read_text(AUDIT_DIR / "model_validation_reports" / "model_validation_report.md"),
        "metrics_json": _read_json(AUDIT_DIR / "project_metrics" / "project_metrics.json"),
        "known_failures": _read_text(ROOT / "stablecoin_lab" / "reports" / "known_failures.md"),
        "latest_snapshot": _latest_snapshot(),
    }
    return reports


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _latest_snapshot() -> str | None:
    if not SNAPSHOTS.exists():
        return None
    snaps = sorted(SNAPSHOTS.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    return str(snaps[0].relative_to(ROOT)) if snaps else None


def _discover_gallery() -> list[dict[str, str]]:
    roots = [
        (ROOT / "reports" / "figures", "VSI"),
        (ROOT / "settlement_lab" / "reports" / "figures", "Settlement"),
        (ROOT / "stablecoin_lab" / "reports" / "figures", "Stablecoin"),
        (ROOT / "reports" / "figures" / "dashboard", "Dashboard"),
    ]
    items: list[dict[str, str]] = []
    for folder, module in roots:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*")):
            if path.suffix.lower() in {".png", ".html", ".svg", ".jpg"}:
                items.append({
                    "title": path.stem.replace("_", " ").title(),
                    "path": str(path.relative_to(ROOT)),
                    "module": module,
                    "ext": path.suffix.lower(),
                })
    return items


def load_all_dashboard_data() -> DashboardData:
    modules = detect_available_modules()
    return DashboardData(
        vsi=load_value_survival_data(),
        settlement=load_settlement_data(),
        stablecoin=load_stablecoin_data(),
        audit=load_audit_reports(),
        data_lake=load_data_lake_catalog(),
        modules=modules,
        gallery=_discover_gallery(),
    )


def apply_data_filters(
    df: pd.DataFrame,
    *,
    sensitivity: str | None = None,
    official_only: bool = False,
    include_mock: bool = True,
    min_quality: float = 0,
    corridor: str | None = None,
    sender: str | None = None,
    receiver: str | None = None,
) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if sensitivity and "sensitivity_case" in out.columns:
        out = out[out["sensitivity_case"] == sensitivity]
    if not include_mock and "mock_data_flag" in out.columns:
        out = out[~out["mock_data_flag"].fillna(False).astype(bool)]
    if official_only and "mock_data_flag" in out.columns:
        out = out[~out["mock_data_flag"].fillna(False).astype(bool)]
    if min_quality > 0 and "data_quality_score" in out.columns:
        out = out[out["data_quality_score"].fillna(0) >= min_quality]
    if corridor and "corridor" in out.columns:
        out = out[out["corridor"] == corridor]
    if sender and "sender_country" in out.columns:
        out = out[out["sender_country"] == sender]
    if receiver and "receiver_country" in out.columns:
        out = out[out["receiver_country"] == receiver]
    return out


def mock_coverage_pct(df: pd.DataFrame) -> float | None:
    if df.empty or "mock_data_flag" not in df.columns:
        return None
    mock = df["mock_data_flag"].fillna(False).astype(bool).mean()
    return round(100 * (1 - mock), 1)


def official_coverage_pct(datasets: list[pd.DataFrame]) -> float | None:
    vals = [mock_coverage_pct(d) for d in datasets if not d.empty]
    return round(sum(vals) / len(vals), 1) if vals else None

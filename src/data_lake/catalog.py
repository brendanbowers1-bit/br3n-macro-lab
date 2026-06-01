"""DuckDB medallion catalog for BR3N Macro Lab data lake."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LAKE = ROOT / "data_lake"
DB_PATH = LAKE / "br3n_lake.duckdb"
CATALOG_PATH = LAKE / "catalog.json"

# Module outputs → gold research folders
GOLD_SYNC_MAP: list[tuple[Path, Path, str]] = [
    (ROOT / "data" / "outputs" / "value_survival_outputs.csv", LAKE / "gold_research" / "value_survival_index" / "value_survival_outputs.csv", "vsi"),
    (ROOT / "settlement_lab" / "data" / "outputs" / "settlement_drag_outputs.csv", LAKE / "gold_research" / "settlement_drag" / "settlement_drag_outputs.csv", "settlement"),
    (ROOT / "settlement_lab" / "data" / "outputs" / "finality_quality_outputs.csv", LAKE / "gold_research" / "finality_quality" / "finality_quality_outputs.csv", "settlement"),
    (ROOT / "stablecoin_lab" / "data" / "outputs" / "stablecoin_finality_quality_outputs.csv", LAKE / "gold_research" / "stablecoin_finality_quality" / "stablecoin_finality_quality_outputs.csv", "stablecoin"),
    (ROOT / "stablecoin_lab" / "data" / "outputs" / "settlement_window_compression_outputs.csv", LAKE / "gold_research" / "settlement_window_compression" / "settlement_window_compression_outputs.csv", "stablecoin"),
    (ROOT / "stablecoin_lab" / "data" / "outputs" / "stablecoin_value_survival_outputs.csv", LAKE / "gold_research" / "stablecoin_value_survival" / "stablecoin_value_survival_outputs.csv", "stablecoin"),
]

SILVER_SYNC_MAP: list[tuple[Path, Path, str]] = [
    (ROOT / "stablecoin_lab" / "data" / "raw" / "stablecoin_supply" / "defillama_supply.csv", LAKE / "silver_cleaned" / "stablecoin_supply" / "defillama_supply.csv", "stablecoin"),
    (ROOT / "stablecoin_lab" / "data" / "raw" / "stablecoin_prices" / "defillama_prices.csv", LAKE / "silver_cleaned" / "stablecoin_price_peg" / "defillama_prices.csv", "stablecoin"),
    (ROOT / "data" / "raw" / "world_bank_rpw" / "rpw_historical_panel.csv", LAKE / "silver_cleaned" / "remittance_rpw" / "rpw_historical_panel.csv", "vsi"),
]


def sync_medallion_files() -> dict[str, int]:
    """Copy module CSVs into medallion folders (bronze/silver/gold placeholders → real files)."""
    counts = {"gold": 0, "silver": 0, "skipped": 0}
    for src, dst, _mod in GOLD_SYNC_MAP:
        if not src.exists():
            counts["skipped"] += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        counts["gold"] += 1
    for src, dst, _mod in SILVER_SYNC_MAP:
        if not src.exists():
            counts["skipped"] += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        counts["silver"] += 1
    return counts


def build_duckdb_catalog(force: bool = False) -> Path:
    """Create/update DuckDB database with views over medallion CSVs."""
    import duckdb

    sync_medallion_files()
    LAKE.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_PATH))
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS bronze")
        con.execute("CREATE SCHEMA IF NOT EXISTS silver")
        con.execute("CREATE SCHEMA IF NOT EXISTS gold")

        views_created = []
        for layer, base in [("bronze", LAKE / "bronze_raw"), ("silver", LAKE / "silver_cleaned"), ("gold", LAKE / "gold_research")]:
            if not base.exists():
                continue
            for csv in base.rglob("*.csv"):
                rel = csv.relative_to(base)
                table = rel.stem.replace("-", "_").replace(" ", "_")
                schema_table = f"{layer}.{table}"
                path_sql = str(csv).replace("'", "''")
                con.execute(f"CREATE OR REPLACE VIEW {schema_table} AS SELECT * FROM read_csv_auto('{path_sql}')")
                views_created.append(schema_table)

        # Convenience unified views
        _create_unified_views(con)
        _write_catalog_json(views_created)
    finally:
        con.close()
    return DB_PATH


def _create_unified_views(con) -> None:
    gold_vsi = LAKE / "gold_research" / "value_survival_index" / "value_survival_outputs.csv"
    if gold_vsi.exists():
        p = str(gold_vsi).replace("'", "''")
        con.execute(f"CREATE OR REPLACE VIEW gold.vsi AS SELECT * FROM read_csv_auto('{p}')")

    gold_sdi = LAKE / "gold_research" / "settlement_drag" / "settlement_drag_outputs.csv"
    if gold_sdi.exists():
        p = str(gold_sdi).replace("'", "''")
        con.execute(f"CREATE OR REPLACE VIEW gold.settlement_drag AS SELECT * FROM read_csv_auto('{p}')")

    gold_sfqi = LAKE / "gold_research" / "stablecoin_finality_quality" / "stablecoin_finality_quality_outputs.csv"
    if gold_sfqi.exists():
        p = str(gold_sfqi).replace("'", "''")
        con.execute(f"CREATE OR REPLACE VIEW gold.stablecoin_finality AS SELECT * FROM read_csv_auto('{p}')")


def _write_catalog_json(views: list[str]) -> None:
    import json

    catalog = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "db_path": str(DB_PATH.relative_to(ROOT)),
        "views": views,
        "gold_tables": [v for v in views if v.startswith("gold.")],
        "silver_tables": [v for v in views if v.startswith("silver.")],
    }
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2), encoding="utf-8")


def get_lake_status() -> dict:
    catalog = {}
    if CATALOG_PATH.exists():
        import json
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return {
        "duckdb_path": str(DB_PATH.relative_to(ROOT)) if DB_PATH.exists() else None,
        "duckdb_exists": DB_PATH.exists(),
        "catalog_views": len(catalog.get("views", [])),
        "catalog_updated": catalog.get("updated_at"),
    }


def query_gold(view: str, limit: int = 500) -> pd.DataFrame:
    """Query a gold-layer DuckDB view. view e.g. 'gold.vsi'."""
    if not DB_PATH.exists():
        return pd.DataFrame()
    import duckdb

    if not view.startswith("gold."):
        view = f"gold.{view}"
    schema, table = view.split(".", 1)
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        return con.execute(f'SELECT * FROM "{schema}"."{table}" LIMIT {int(limit)}').df()
    except Exception:
        return pd.DataFrame()
    finally:
        con.close()


def load_vsi_from_lake() -> pd.DataFrame:
    df = query_gold("gold.vsi")
    if not df.empty:
        return df
    path = LAKE / "gold_research" / "value_survival_index" / "value_survival_outputs.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

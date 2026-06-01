#!/usr/bin/env python3
"""Export dashboard data as JSON for Next.js / external consumers."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.dashboard.data_loader import (
    load_all_dashboard_data,
    load_audit_reports,
    load_data_lake_catalog,
    mock_coverage_pct,
    official_coverage_pct,
)
from src.data_lake.catalog import get_lake_status, query_gold
from src.visuals.vsi_charts import corridor_summary

OUT_DIR = ROOT / "web_dashboard" / "public" / "api"
OUT_FILE = OUT_DIR / "dashboard.json"

COUNTRY_COORDS: dict[str, tuple[float, float]] = {
    "United States": [-98.0, 39.5],
    "Mexico": [-102.0, 23.6],
    "India": [78.9, 22.5],
    "Philippines": [122.0, 12.8],
    "Germany": [10.5, 51.2],
    "Nigeria": [8.7, 9.1],
    "Brazil": [-51.9, -14.2],
    "Colombia": [-74.3, 4.6],
    "United Arab Emirates": [54.4, 24.5],
    "Pakistan": [69.3, 30.4],
    "El Salvador": [-88.9, 13.7],
    "Guatemala": [-90.5, 15.8],
    "Dominican Republic": [-70.2, 18.7],
}


def _sankey_from_row(row: pd.Series) -> dict:
    def pct(col: str) -> float:
        v = float(row.get(col, 0) or 0)
        return round(v * 100 if v < 1 else v, 3)

    fees = pct("explicit_fee_loss_pct")
    fx = pct("fx_spread_loss_pct")
    timing = pct("timing_loss_pct")
    vol = pct("volatility_loss_pct")
    infl = pct("inflation_erosion_pct")
    payout = pct("payout_friction_pct")
    usable = max(100 - fees - fx - timing - vol - infl - payout, 0)
    nodes = [
        {"name": "$100 sent"},
        {"name": "Fees"},
        {"name": "FX spread"},
        {"name": "Timing"},
        {"name": "Volatility"},
        {"name": "Inflation"},
        {"name": "Payout friction"},
        {"name": "Usable value"},
    ]
    links = [
        {"source": 0, "target": 1, "value": max(fees, 0.01)},
        {"source": 0, "target": 2, "value": max(fx, 0.01)},
        {"source": 0, "target": 3, "value": max(timing, 0.01)},
        {"source": 0, "target": 4, "value": max(vol, 0.01)},
        {"source": 0, "target": 5, "value": max(infl, 0.01)},
        {"source": 0, "target": 6, "value": max(payout, 0.01)},
        {"source": 0, "target": 7, "value": max(usable, 0.01)},
    ]
    return {
        "corridor": row.get("corridor"),
        "nodes": nodes,
        "links": links,
        "methodology": "Research estimate under stated assumptions. Not investment advice.",
    }


def _value_flow_lines(summary: pd.DataFrame) -> list[dict]:
    lines = []
    for _, r in summary.iterrows():
        corridor = str(r.get("corridor", ""))
        if "→" not in corridor:
            continue
        sender, receiver = [p.strip() for p in corridor.split("→", 1)]
        if sender not in COUNTRY_COORDS or receiver not in COUNTRY_COORDS:
            continue
        slon, slat = COUNTRY_COORDS[sender]
        rlon, rlat = COUNTRY_COORDS[receiver]
        loss = float(r.get("value_loss_usd_per_100", 5) or 5)
        vsi = float(r.get("value_survival_index", 90) or 90)
        lines.append({
            "corridor": corridor,
            "sender": sender,
            "receiver": receiver,
            "coords": [[slon, slat], [rlon, rlat]],
            "value_loss_per_100": loss,
            "vsi": vsi,
            "width": max(1, min(8, loss / 2)),
        })
    return lines


def _lineage_graph(data) -> dict:
    nodes = [
        {"id": "rpw", "name": "World Bank RPW", "category": "source", "tier": 1},
        {"id": "imf", "name": "IMF / FRED", "category": "source", "tier": 1},
        {"id": "bis", "name": "BIS CPMI", "category": "source", "tier": 1},
        {"id": "defillama", "name": "DeFiLlama", "category": "source", "tier": 3},
        {"id": "bronze", "name": "Bronze raw", "category": "layer"},
        {"id": "silver", "name": "Silver cleaned", "category": "layer"},
        {"id": "gold", "name": "Gold research", "category": "layer"},
        {"id": "vsi", "name": "VSI outputs", "category": "module"},
        {"id": "settlement", "name": "Settlement lab", "category": "module"},
        {"id": "stablecoin", "name": "Stablecoin lab", "category": "module"},
        {"id": "audit", "name": "Audit / quality", "category": "module"},
        {"id": "dashboard", "name": "Command Center", "category": "ui"},
    ]
    links = [
        {"source": "rpw", "target": "bronze"},
        {"source": "imf", "target": "bronze"},
        {"source": "bis", "target": "bronze"},
        {"source": "defillama", "target": "bronze"},
        {"source": "bronze", "target": "silver"},
        {"source": "silver", "target": "gold"},
        {"source": "gold", "target": "vsi"},
        {"source": "gold", "target": "settlement"},
        {"source": "gold", "target": "stablecoin"},
        {"source": "vsi", "target": "audit"},
        {"source": "settlement", "target": "audit"},
        {"source": "stablecoin", "target": "audit"},
        {"source": "vsi", "target": "dashboard"},
        {"source": "settlement", "target": "dashboard"},
        {"source": "stablecoin", "target": "dashboard"},
        {"source": "audit", "target": "dashboard"},
    ]
    return {"nodes": nodes, "links": links}


def _settlement_timeline(fqi_df: pd.DataFrame) -> list[dict]:
    if fqi_df.empty:
        return [
            {"stage": "Authorization", "hours": 0.5, "score": 55},
            {"stage": "Clearing", "hours": 4, "score": 60},
            {"stage": "Settlement", "hours": 24, "score": 65},
            {"stage": "Funds availability", "hours": 48, "score": 72},
            {"stage": "Legal finality", "hours": 72, "score": 80},
        ]
    row = fqi_df.iloc[0]
    lag = float(row.get("finality_lag_hours", 24) or 24)
    fqi = float(row.get("finality_quality_index", 60) or 60)
    op = float(row.get("operational_finality_score", 55) or 55)
    legal = float(row.get("legal_finality_score", 70) or 70)
    return [
        {"stage": "Authorization", "hours": round(lag * 0.05, 2), "score": op * 0.9},
        {"stage": "Clearing", "hours": round(lag * 0.15, 2), "score": op},
        {"stage": "Settlement", "hours": round(lag * 0.35, 2), "score": fqi * 0.95},
        {"stage": "Funds availability", "hours": round(lag * 0.7, 2), "score": fqi},
        {"stage": "Legal finality", "hours": round(lag, 2), "score": legal},
    ]


def _finality_matrix(sfqi_df: pd.DataFrame) -> list[dict]:
    if sfqi_df.empty:
        return []
    cols = ["stablecoin", "ledger_finality_score", "economic_finality_score", "stablecoin_finality_quality_index", "mock_data_flag"]
    present = [c for c in cols if c in sfqi_df.columns]
    return _df_records(sfqi_df[present].head(20))


def _risk_relocation_sankey() -> dict:
    nodes = [{"name": "Counterparty risk ↓"}, {"name": "Issuer risk ↑"}, {"name": "Reserve risk ↑"}, {"name": "Off-ramp risk ↑"}, {"name": "Compliance risk ↑"}]
    links = [
        {"source": 0, "target": 1, "value": 25},
        {"source": 0, "target": 2, "value": 25},
        {"source": 0, "target": 3, "value": 25},
        {"source": 0, "target": 4, "value": 25},
    ]
    return {"nodes": nodes, "links": links, "note": "Conceptual risk relocation under SWC spec — not causal."}


def _df_records(df: pd.DataFrame, limit: int = 500) -> list[dict]:
    if df.empty:
        return []
    d = df.head(limit).copy()
    for col in d.columns:
        if pd.api.types.is_datetime64_any_dtype(d[col]):
            d[col] = d[col].astype(str)
    return json.loads(d.to_json(orient="records"))


def _executive_summary(data) -> dict:
    vsi = data.vsi.get("value_survival").df
    sdi = data.settlement.get("settlement_drag").df
    sfqi = data.stablecoin.get("finality_quality").df
    summary = corridor_summary(vsi) if not vsi.empty else pd.DataFrame()

    global_vsi = float(summary["value_survival_index"].mean()) if not summary.empty else None
    worst = summary.nsmallest(1, "value_survival_index").iloc[0].to_dict() if not summary.empty else {}
    worst_sdi = sdi.nsmallest(1, "settlement_drag_index").iloc[0].to_dict() if not sdi.empty and "settlement_drag_index" in sdi.columns else {}
    worst_sfqi = sfqi.nsmallest(1, "stablecoin_finality_quality_index").iloc[0].to_dict() if not sfqi.empty else {}

    return {
        "global_vsi": global_vsi,
        "worst_corridor": worst.get("corridor"),
        "worst_vsi": worst.get("value_survival_index"),
        "avg_loss_per_100": float(summary["value_loss_usd_per_100"].mean()) if not summary.empty and "value_loss_usd_per_100" in summary.columns else None,
        "official_coverage_pct": official_coverage_pct([vsi, sdi, sfqi]),
        "worst_settlement_entity": worst_sdi.get("entity"),
        "worst_sdi": worst_sdi.get("settlement_drag_index"),
        "worst_stablecoin": worst_sfqi.get("stablecoin"),
        "worst_sfqi": worst_sfqi.get("stablecoin_finality_quality_index"),
    }


def _hypotheses_all() -> dict:
    import importlib.util

    rows = {"vsi": [], "settlement": [], "stablecoin": [], "flagship_questions": []}
    try:
        from src.research.hypotheses import hypotheses_dataframe as vsi_h
        rows["vsi"] = _df_records(vsi_h(), 50)
    except Exception:
        pass

    for key, rel in [("settlement", "settlement_lab/src/research/hypotheses.py"), ("stablecoin", "stablecoin_lab/src/research/hypotheses.py")]:
        path = ROOT / rel
        if not path.exists():
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"{key}_hyp", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            rows[key] = _df_records(mod.hypotheses_dataframe(), 50)
            if key == "stablecoin" and hasattr(mod, "FLAGSHIP_QUESTIONS"):
                rows["flagship_questions"] = mod.FLAGSHIP_QUESTIONS
        except Exception:
            pass
    return rows


def build_export() -> dict:
    data = load_all_dashboard_data()
    lake_status = get_lake_status()
    vsi_df = data.vsi["value_survival"].df
    summary = corridor_summary(vsi_df) if not vsi_df.empty else pd.DataFrame()
    sfqi_df = data.stablecoin.get("finality_quality").df if data.stablecoin.get("finality_quality") else pd.DataFrame()
    fqi_df = data.settlement.get("finality_quality").df if data.settlement.get("finality_quality") else pd.DataFrame()

    sankey_rows = []
    if not vsi_df.empty:
        for corridor in summary["corridor"].head(5) if not summary.empty else []:
            sub = vsi_df[vsi_df["corridor"] == corridor]
            if not sub.empty:
                sankey_rows.append(_sankey_from_row(sub.iloc[0]))
    elif not vsi_df.empty:
        sankey_rows.append(_sankey_from_row(vsi_df.iloc[0]))

    payload = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "lab": "BR3N Macro Lab",
            "disclaimer": "Research only. Not investment advice.",
        },
        "modules": {
            "vsi": data.modules.vsi,
            "settlement": data.modules.settlement,
            "stablecoin": data.modules.stablecoin,
            "data_lake": data.modules.data_lake,
            "audit": data.modules.audit,
        },
        "executive": _executive_summary(data),
        "vsi": {
            "corridor_summary": _df_records(corridor_summary(data.vsi["value_survival"].df)) if not data.vsi["value_survival"].df.empty else [],
            "outputs_sample": _df_records(data.vsi["value_survival"].df, 200),
            "sensitivity_sample": _df_records(data.vsi.get("sensitivity").df, 100),
        },
        "settlement": {
            k: _df_records(lr.df, 150) for k, lr in data.settlement.items() if not lr.df.empty
        },
        "stablecoin": {
            k: _df_records(lr.df, 150) for k, lr in data.stablecoin.items() if not lr.df.empty
        },
        "data_lake": {**load_data_lake_catalog(), **lake_status},
        "audit": {
            "latest_snapshot": load_audit_reports().get("latest_snapshot"),
            "quality_summary": load_audit_reports().get("quality", {}).get("data", {}).get("summary", {}),
        },
        "coverage": {
            mod: {name: mock_coverage_pct(lr.df) for name, lr in bundle.items()}
            for mod, bundle in [("vsi", data.vsi), ("settlement", data.settlement), ("stablecoin", data.stablecoin)]
        },
        "hypotheses": _hypotheses_all(),
        "gallery": data.gallery[:60],
        "visualizations": {
            "sankey_by_corridor": sankey_rows,
            "value_flow_lines": _value_flow_lines(summary),
            "lineage_graph": _lineage_graph(data),
            "settlement_timeline": _settlement_timeline(fqi_df),
            "finality_matrix": _finality_matrix(sfqi_df),
            "risk_relocation_sankey": _risk_relocation_sankey(),
        },
    }
    return payload


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_export()
    OUT_FILE.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"Exported: {OUT_FILE.relative_to(ROOT)}")
    print(f"  VSI corridors: {len(payload['vsi']['corridor_summary'])}")
    print(f"  Settlement tables: {len(payload['settlement'])}")
    print(f"  Stablecoin tables: {len(payload['stablecoin'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

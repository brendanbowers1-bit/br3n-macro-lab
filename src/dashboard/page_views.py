"""Page renderers for Bowers Frontier Command Center."""

from __future__ import annotations

import html as html_lib
from pathlib import Path

import pandas as pd
import streamlit as st

from src.dashboard import charts
from src.dashboard.components import (
    chart_card,
    export_csv_button,
    kpi_card,
    kpi_row,
    methodology_note,
    missing_data_panel,
    page_header,
    premium_table,
    publication_checklist,
    read_markdown_snippet,
    section_header,
    warning_banner,
)
from src.dashboard.data_loader import (
    DashboardData,
    LoadResult,
    ROOT,
    apply_data_filters,
    mock_coverage_pct,
    official_coverage_pct,
)
from src.visuals.vsi_charts import corridor_summary

ROOT_PATH = ROOT


def render_command_center(data: DashboardData, flt: dict) -> None:
    page_header(
        "Executive Command Center",
        "Cross-lab intelligence · VSI · Settlement · Stablecoin · Audit",
        tag="EXECUTIVE",
        meta_badges=[("MULTI-MODULE", "gold"), ("RESEARCH ONLY", "amber")],
    )
    vsi_lr = data.vsi.get("value_survival", LoadResult("", None, pd.DataFrame(), ""))
    vsi = apply_data_filters(vsi_lr.df, **flt)
    sdi = data.settlement.get("settlement_drag", LoadResult("", None, pd.DataFrame(), "")).df
    sfqi = data.stablecoin.get("finality_quality", LoadResult("", None, pd.DataFrame(), "")).df

    mock_any = False
    for lr in [vsi_lr] + list(data.settlement.values()) + list(data.stablecoin.values()):
        if not lr.df.empty and "mock_data_flag" in lr.df.columns and lr.df["mock_data_flag"].fillna(False).astype(bool).any():
            mock_any = True
            break
    if mock_any:
        warning_banner("Mock or mixed-mode data detected in one or more modules. Verify lineage before drawing conclusions.")

    summary = corridor_summary(vsi) if not vsi.empty else pd.DataFrame()
    global_vsi = summary["value_survival_index"].mean() if not summary.empty else None
    worst = summary.nsmallest(1, "value_survival_index").iloc[0] if not summary.empty else None
    worst_sdi = sdi.nsmallest(1, "settlement_drag_index").iloc[0] if not sdi.empty and "settlement_drag_index" in sdi.columns else None
    worst_sfqi = sfqi.nsmallest(1, "stablecoin_finality_quality_index").iloc[0] if not sfqi.empty and "stablecoin_finality_quality_index" in sfqi.columns else None
    avg_loss = summary["value_loss_usd_per_100"].mean() if not summary.empty and "value_loss_usd_per_100" in summary.columns else None
    cov = official_coverage_pct([vsi, sdi, sfqi])
    grade = summary["data_quality_grade"].mode().iloc[0] if not summary.empty and "data_quality_grade" in summary.columns else "N/A"
    dq_mean = summary["data_quality_score"].mean() if not summary.empty and "data_quality_score" in summary.columns else None

    q = data.audit.get("quality", {})
    st_val = q.get("data", {}).get("summary", {}) if q.get("status") == "loaded" else {}
    snap = data.audit.get("latest_snapshot") or "None"

    kpi_row([
        ("Global VSI", f"{global_vsi:.1f}" if global_vsi else "—", "Mean corridor", "cyan"),
        ("Worst corridor", str(worst["corridor"])[:22] if worst is not None else "—", f"VSI {worst['value_survival_index']:.1f}" if worst is not None else "", "red"),
        ("Value lost / $100", f"${avg_loss:.2f}" if avg_loss else "—", "Est. leakage", "amber"),
        ("Official coverage", f"{cov}%" if cov else "—", f"Grade {grade}", "gold"),
    ])
    kpi_row([
        ("Settlement drag", str(worst_sdi["entity"])[:22] if worst_sdi is not None else "—", f"SDI {worst_sdi['settlement_drag_index']:.1f}" if worst_sdi is not None else "", "amber"),
        ("Lowest SFQI", str(worst_sfqi["stablecoin"]) if worst_sfqi is not None else "—", f"SFQI {worst_sfqi['stablecoin_finality_quality_index']:.1f}" if worst_sfqi is not None else "", "red"),
        ("Latest snapshot", snap.split("/")[-1][:18], "Audit trail", "cyan"),
        ("Quality run", f"PASS {st_val.get('pass', '—')}", f"FAIL {st_val.get('fail', '—')}", "green" if st_val.get("fail", 1) == 0 else "amber"),
    ])

    section_header("Risk intelligence")
    col_a, col_b = st.columns([1.2, 1])
    with col_a:
        if not summary.empty:
            fig = charts.ranked_bar(summary.head(10), "corridor", "value_survival_index", "Top 10 worst corridors (lowest VSI)", ascending=True)
            chart_card(
                fig,
                "Corridor leakage ranking",
                subtitle="Lower VSI = greater estimated value leakage",
                source="World Bank RPW + Bowers Frontier VSI pipeline",
                source_id="world_bank_rpw",
                tier=1,
                quality_score=dq_mean,
                quality_note=f"Official coverage {mock_coverage_pct(vsi)}%",
                methodology="vsi-credible-1.0 · Research estimate under stated assumptions.",
                mock_warning=mock_any,
            )
        else:
            missing_data_panel(vsi_lr, "python scripts/reproduce_all.py")
    with col_b:
        fig = charts.global_risk_heatmap(vsi, sdi, sfqi)
        chart_card(
            fig,
            "Global risk heatmap",
            subtitle="Inverted indices — higher = more fragility/leakage",
            source="VSI · Settlement · Stablecoin outputs",
            methodology="Descriptive cross-module risk map. Not causal.",
        )

    section_header("Module connectivity")
    from src.dashboard.components import module_status_panel
    module_status_panel(data.modules)


def render_value_survival(data: DashboardData, flt: dict) -> None:
    page_header(
        "Value Survival Index",
        "How much value survives when money crosses borders?",
        tag="VSI",
        meta_badges=[("T1 RPW", "cyan"), ("FLAGSHIP", "gold")],
    )
    lr = data.vsi.get("value_survival", LoadResult("", None, pd.DataFrame(), ""))
    vsi = apply_data_filters(lr.df, **flt)
    if vsi.empty:
        missing_data_panel(lr, "python scripts/reproduce_all.py")
        return

    summary = corridor_summary(vsi)
    tab1, tab2, tab3, tab4 = st.tabs(["Rankings", "Components", "Sankey", "Table"])
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            fig = charts.ranked_bar(summary, "corridor", "value_survival_index", "VSI ranked", ascending=True)
            chart_card(
                fig, "Ranked VSI",
                subtitle="Corridor-level value survival",
                source="World Bank RPW + Bowers Frontier VSI",
                source_id="world_bank_rpw", tier=1,
                methodology="vsi-credible-1.0",
                mock_warning=bool(vsi["mock_data_flag"].any()) if "mock_data_flag" in vsi.columns else False,
            )
        with c2:
            if "value_loss_usd_per_100" in summary.columns:
                fig = charts.ranked_bar(summary.sort_values("value_loss_usd_per_100", ascending=False), "corridor", "value_loss_usd_per_100", "Value lost per $100")
                chart_card(fig, "Leakage in USD per $100 sent", source="RPW + component spec", tier=1)
    with tab2:
        row = vsi.iloc[0]
        if flt.get("corridor") and "corridor" in vsi.columns:
            sub = vsi[vsi["corridor"] == flt["corridor"]]
            if not sub.empty:
                row = sub.iloc[0]
        fig = charts.stacked_component_breakdown(row)
        chart_card(fig, "Component breakdown", methodology="vsi-credible-1.0 · Extended spec components are model-based.", source="RPW + IMF macro", tier=1)
    with tab3:
        fig = charts.sankey_value_survival(row)
        chart_card(fig, "Value survival Sankey", subtitle="$100 sent → leakage channels → usable value", methodology="Illustrative decomposition per corridor row.")
    with tab4:
        show = summary[["corridor", "value_survival_index", "vsi_core", "vsi_risk_adjusted", "vsi_extended", "value_loss_usd_per_100", "data_quality_score"]].copy() if not summary.empty else summary
        premium_table(show, title="Corridor comparison", numeric_cols=["value_survival_index", "value_loss_usd_per_100", "data_quality_score"])
        export_csv_button(show, "vsi_corridor_summary.csv")


def render_settlement(data: DashboardData, flt: dict) -> None:
    page_header(
        "Settlement Economics",
        "Settlement drag · liquidity burden · finality · fragility",
        tag="SETTLEMENT",
        meta_badges=[("BIS CPMI", "cyan"), ("MIXED MODE", "amber")],
    )
    sdi_lr = data.settlement.get("settlement_drag", LoadResult("", None, pd.DataFrame(), ""))
    fqi_lr = data.settlement.get("finality_quality", LoadResult("", None, pd.DataFrame(), ""))
    olb_lr = data.settlement.get("operational_liquidity", LoadResult("", None, pd.DataFrame(), ""))
    pfi_lr = data.settlement.get("friction_incidence", LoadResult("", None, pd.DataFrame(), ""))

    sdi = apply_data_filters(sdi_lr.df, **flt)
    fqi = fqi_lr.df
    olb = olb_lr.df
    pfi = pfi_lr.df

    rail = st.selectbox("Rail type filter", ["All"] + sorted(sdi["rail_type"].dropna().unique().tolist())) if not sdi.empty and "rail_type" in sdi.columns else "All"
    if rail != "All" and not sdi.empty:
        sdi = sdi[sdi["rail_type"] == rail]

    tab1, tab2, tab3, tab4 = st.tabs(["SDI", "Frontier", "Finality ladder", "PFI"])
    with tab1:
        if sdi.empty:
            missing_data_panel(sdi_lr, "cd settlement_lab && python scripts/reproduce_settlement_lab.py")
        else:
            top = sdi.nsmallest(20, "settlement_drag_index")
            fig = charts.ranked_bar(top, "entity", "settlement_drag_index", "Settlement drag (lowest SDI = highest drag proxy)", ascending=True)
            mock = bool(sdi["mock_data_flag"].any()) if "mock_data_flag" in sdi.columns else False
            chart_card(fig, "Settlement drag ranked", source="BIS CPMI + settlement_lab", source_id="bis_cpmi", tier=1, mock_warning=mock, methodology="settlement-lab-credible-1.0")
    with tab2:
        if not olb.empty and "operational_liquidity_burden_score" in olb.columns and not fqi.empty and "finality_quality_index" in fqi.columns:
            merged = olb.merge(fqi[["entity", "finality_quality_index"]], on="entity", how="inner")
            fig = charts.scatter_frontier(merged.head(40), "finality_quality_index", "operational_liquidity_burden_score", "entity", "OLB vs finality frontier")
            chart_card(fig, "Liquidity burden frontier")
        else:
            st.info("Load OLB + FQI outputs for frontier chart.")
    with tab3:
        if not fqi.empty:
            row = fqi.iloc[0]
            scores = {
                "Authorization": float(row.get("operational_finality_score", 50) or 50),
                "Clearing": float(row.get("operational_finality_score", 55) or 55),
                "Settlement": float(row.get("finality_quality_index", 60) or 60),
                "Funds availability": float(row.get("legal_finality_score", 65) or 65),
                "Legal finality": float(row.get("legal_finality_score", 70) or 70),
            }
            chart_card(charts.finality_ladder(scores), "Finality ladder (illustrative row)")
        else:
            missing_data_panel(fqi_lr, "cd settlement_lab && python scripts/reproduce_settlement_lab.py")
    with tab4:
        if not pfi.empty and "incidence_share_sender" in pfi.columns:
            cols = [c for c in pfi.columns if "incidence" in c][:4]
            fig = charts.ranked_bar(pfi.head(15), "entity", cols[0] if cols else "entity", "Payment friction incidence")
            chart_card(fig, "Friction incidence")
        else:
            st.dataframe(pfi.head(20) if not pfi.empty else pd.DataFrame(), use_container_width=True)


def render_stablecoin(data: DashboardData, flt: dict) -> None:
    page_header(
        "Stablecoin Settlement Windows",
        "Finality · compression · compliance · run conditions",
        tag="STABLECOIN",
        meta_badges=[("DEFILLAMA", "cyan"), ("MIXED OFF-RAMP", "amber")],
    )
    sfqi_lr = data.stablecoin.get("finality_quality", LoadResult("", None, pd.DataFrame(), ""))
    swc_lr = data.stablecoin.get("swc", LoadResult("", None, pd.DataFrame(), ""))
    svsi_lr = data.stablecoin.get("svsi", LoadResult("", None, pd.DataFrame(), ""))
    drv_lr = data.stablecoin.get("digital_run_velocity", LoadResult("", None, pd.DataFrame(), ""))
    sing_lr = data.stablecoin.get("singleness", LoadResult("", None, pd.DataFrame(), ""))
    csd_lr = data.stablecoin.get("compliance_drag", LoadResult("", None, pd.DataFrame(), ""))

    sfqi = apply_data_filters(sfqi_lr.df, **flt)
    swc = apply_data_filters(swc_lr.df, **flt)
    coin = st.selectbox("Stablecoin", ["All"] + sorted(sfqi["stablecoin"].dropna().unique().tolist())) if not sfqi.empty and "stablecoin" in sfqi.columns else "All"
    if coin != "All" and not sfqi.empty:
        sfqi = sfqi[sfqi["stablecoin"] == coin]

    tab1, tab2, tab3, tab4 = st.tabs(["Finality matrix", "SWC & SVSI", "DRV & singleness", "Risk relocation"])
    with tab1:
        if sfqi.empty:
            missing_data_panel(sfqi_lr, "cd stablecoin_lab && python scripts/reproduce_stablecoin_lab.py")
        else:
            fig = charts.scatter_frontier(sfqi, "ledger_finality_score", "economic_finality_score", "stablecoin", "Ledger vs economic finality")
            mock = bool(sfqi["mock_data_flag"].any()) if "mock_data_flag" in sfqi.columns else False
            chart_card(fig, "Finality scatter", mock_warning=mock)
            fig2 = charts.ranked_bar(sfqi, "stablecoin", "stablecoin_finality_quality_index", "Stablecoin Finality Quality Index")
            chart_card(fig2, "SFQI ranked")
    with tab2:
        if not swc.empty:
            chart_card(charts.ranked_bar(swc, "entity", "swc_core", "Settlement Window Compression"), "SWC by corridor")
        if not svsi_lr.df.empty and "stablecoin_vsi" in svsi_lr.df.columns:
            chart_card(charts.scatter_frontier(svsi_lr.df, "traditional_vsi", "stablecoin_vsi", "corridor", "Stablecoin VSI vs traditional VSI"), "SVSI comparison")
    with tab3:
        if not drv_lr.df.empty and "digital_run_velocity_score" in drv_lr.df.columns:
            chart_card(charts.gauge_card(float(drv_lr.df["digital_run_velocity_score"].mean()), "Mean Digital Run Velocity"), "DRV gauge")
        if not sing_lr.df.empty:
            chart_card(charts.ranked_bar(sing_lr.df, "stablecoin", "tokenized_money_singleness_index", "Tokenized money singleness"), "TMS")
        if not csd_lr.df.empty and "compliance_settlement_drag_index" in csd_lr.df.columns:
            chart_card(charts.ranked_bar(csd_lr.df, "stablecoin", "compliance_settlement_drag_index", "Compliance settlement drag"), "CSD")
    with tab4:
        row = swc.iloc[0] if not swc.empty else pd.Series()
        chart_card(charts.sankey_risk_relocation(row), "Conceptual risk relocation Sankey")


def render_data_lake(data: DashboardData) -> None:
    page_header(
        "Data Lake Command Center",
        "Bronze · Silver · Gold · DuckDB · lineage catalog",
        tag="DATA LAKE",
        meta_badges=[("MEDALLION", "purple"), ("DUCKDB", "green")],
    )
    lake = data.data_lake
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Bronze files", str(lake.get("bronze_count", 0)), "Raw extracts", "gold")
    with c2:
        kpi_card("Silver tables", str(lake.get("silver_count", 0)), "Cleaned layer", "cyan")
    with c3:
        kpi_card("Gold outputs", str(lake.get("gold_count", 0)), "Research-ready", "green")
    with c4:
        kpi_card("DuckDB", "ONLINE" if lake.get("duckdb_exists") else "OFF", str(lake.get("duckdb_status", "")), "green" if lake.get("duckdb_exists") else "amber")

    warning_banner("Gold/silver layers sync from module outputs via scripts/sync_data_lake.py. Bronze remains sparse.", "amber")

    catalog_rows = []
    for mod, bundle in [("VSI", data.vsi), ("Settlement", data.settlement), ("Stablecoin", data.stablecoin)]:
        for name, lr in bundle.items():
            catalog_rows.append({"Module": mod, "Dataset": name, "Status": lr.status, "Rows": len(lr.df), "Path": lr.path or "—"})
    premium_table(pd.DataFrame(catalog_rows), title="Dataset catalog")

    mock_rows = []
    for mod, bundle in [("VSI", data.vsi), ("Settlement", data.settlement), ("Stablecoin", data.stablecoin)]:
        for name, lr in bundle.items():
            pct = mock_coverage_pct(lr.df)
            if pct is not None:
                mock_rows.append({"Module": mod, "Dataset": name, "Official %": pct})
    if mock_rows:
        fig = charts.heatmap_quality(pd.DataFrame(mock_rows), "Dataset", "Module", "Official %", "Official vs manual coverage")
        chart_card(fig, "Source coverage heatmap")


def render_audit(data: DashboardData) -> None:
    page_header(
        "Data Quality & Audit",
        "Validation · tests · snapshots · credibility",
        tag="AUDIT",
        meta_badges=[("QUALITY SYSTEM", "green")],
    )
    q = data.audit.get("quality", {})
    metrics = data.audit.get("metrics_json", {})

    if q.get("status") == "loaded":
        summary = q["data"].get("summary", {})
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi_card("PASS", str(summary.get("pass", 0)), "Quality steps", "green")
        with c2:
            kpi_card("FAIL", str(summary.get("fail", 0)), "Needs review", "red" if summary.get("fail") else "green")
        with c3:
            kpi_card("Files", str(metrics.get("totals", {}).get("files", "—")), "Project scope", "cyan")
        with c4:
            kpi_card("Snapshot", (data.audit.get("latest_snapshot") or "none").split("/")[-1][:18], "Latest backup", "gold")
    else:
        missing_data_panel(LoadResult("quality", None, pd.DataFrame(), "missing", q.get("message", "")), "python scripts/run_all_quality_checks.py")

    checklist = [
        ("No mock data in final outputs", "WARN", "Mixed mode in settlement/stablecoin off-ramp"),
        ("Tier 1/2 sources for core variables", "WARN", "See data validation report"),
        ("Raw file hashes recorded", "PASS", "stablecoin_lab/metadata/file_checksums.csv"),
        ("Methodology version recorded", "PASS", "Lineage columns in outputs"),
        ("Sensitivity analysis completed", "PASS", "Module sensitivity CSVs"),
        ("Robustness checks completed", "PASS", "Module robustness CSVs"),
        ("Reproduction script passed", "WARN", "Run per-module reproduce scripts"),
        ("Claims limited to evidence", "PASS", "Disclaimers in outputs"),
    ]
    publication_checklist(checklist)

    tab1, tab2, tab3 = st.tabs(["Quality report", "Data validation", "Known failures"])
    with tab1:
        md = read_markdown_snippet(ROOT / "audit" / "test_reports" / "full_quality_report.md", 8000)
        st.markdown(md)
    with tab2:
        st.markdown(read_markdown_snippet(ROOT / "audit" / "data_quality_reports" / "data_validation_report.md", 6000))
    with tab3:
        st.markdown(data.audit.get("known_failures") or "_No known failures file._")


def render_sensitivity(data: DashboardData, flt: dict) -> None:
    page_header(
        "Sensitivity & Robustness",
        "Conservative · baseline · severe · rank stability",
        tag="ROBUSTNESS",
        meta_badges=[("SCENARIO ANALYSIS", "purple")],
    )
    vsi_s = data.vsi.get("sensitivity", LoadResult("", None, pd.DataFrame(), "")).df
    settle_s = data.settlement.get("sensitivity", LoadResult("", None, pd.DataFrame(), "")).df
    stable_s = data.stablecoin.get("sensitivity", LoadResult("", None, pd.DataFrame(), "")).df
    vsi_r = data.vsi.get("rank_stability", LoadResult("", None, pd.DataFrame(), "")).df
    stable_r = data.stablecoin.get("robustness", LoadResult("", None, pd.DataFrame(), "")).df

    tab1, tab2, tab3, tab4 = st.tabs(["VSI", "Settlement", "Stablecoin", "Rank stability"])
    with tab1:
        if not vsi_s.empty and "value_survival_index" in vsi_s.columns:
            entity = "corridor" if "corridor" in vsi_s.columns else vsi_s.columns[0]
            chart_card(charts.sensitivity_band_chart(vsi_s.head(200), entity, "value_survival_index"), "VSI sensitivity bands")
        else:
            st.info("Run VSI sensitivity: outputs in data/outputs/vsi_sensitivity_results.csv")
    with tab2:
        if not settle_s.empty:
            premium_table(settle_s.head(30), title="Settlement sensitivity sample")
        else:
            st.info("Settlement sensitivity_results.csv not found.")
    with tab3:
        if not stable_s.empty:
            chart_card(charts.sensitivity_band_chart(stable_s.head(100), "entity" if "entity" in stable_s.columns else stable_s.columns[0], stable_s.select_dtypes("number").columns[0]), "Stablecoin sensitivity")
        else:
            st.info("Run stablecoin sensitivity pipeline.")
    with tab4:
        chart_card(charts.rank_stability_heatmap(vsi_r if not vsi_r.empty else stable_r), "Rank stability heatmap")


def render_hypotheses(data: DashboardData) -> None:
    page_header(
        "Research Hypotheses",
        "Questions · expected signs · evidence grade · limitations",
        tag="HYPOTHESES",
        meta_badges=[("NO CAUSAL CLAIMS", "amber")],
    )

    def _load_settlement():
        import importlib.util
        path = ROOT_PATH / "settlement_lab" / "src" / "research" / "hypotheses.py"
        spec = importlib.util.spec_from_file_location("settle_hyp", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.hypotheses_dataframe()

    def _load_stablecoin():
        import importlib.util
        path = ROOT_PATH / "stablecoin_lab" / "src" / "research" / "hypotheses.py"
        spec = importlib.util.spec_from_file_location("sc_hyp", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.hypotheses_dataframe(), mod.FLAGSHIP_QUESTIONS

    from src.research.hypotheses import hypotheses_dataframe as vsi_hyp
    vsi_df = vsi_hyp()

    tab_vsi, tab_settle, tab_sc, tab_matrix = st.tabs(["VSI", "Settlement", "Stablecoin", "Evidence matrix"])

    with tab_vsi:
        premium_table(vsi_df, title="VSI hypotheses (H1–H6)")
        export_csv_button(vsi_df, "hypotheses_vsi.csv")

    with tab_settle:
        try:
            settle_df = _load_settlement()
            premium_table(settle_df, title="Settlement hypotheses")
            export_csv_button(settle_df, "hypotheses_settlement.csv")
        except Exception as exc:
            st.warning(f"Settlement hypotheses unavailable: {exc}")

    with tab_sc:
        try:
            sc_df, questions = _load_stablecoin()
            section_header("Flagship research questions")
            for q in questions:
                st.markdown(f'<div class="br3n-caption" style="margin:0.25rem 0;">◈ {html_lib.escape(q)}</div>', unsafe_allow_html=True)
            section_header("Testable hypotheses")
            premium_table(sc_df, title="Stablecoin hypotheses")
            export_csv_button(sc_df, "hypotheses_stablecoin.csv")
        except Exception as exc:
            st.warning(f"Stablecoin hypotheses unavailable: {exc}")

    with tab_matrix:
        frames = []
        for lab, df in [("VSI", vsi_df)]:
            if df is not None and not df.empty:
                tmp = df.copy()
                tmp["lab"] = lab
                tmp["evidence_grade"] = "Descriptive — panel available" if data.modules.vsi else "No data"
                frames.append(tmp)
        try:
            sd = _load_settlement()
            tmp = sd.copy()
            tmp["lab"] = "Settlement"
            tmp["evidence_grade"] = "Mixed BIS CPMI" if data.modules.settlement else "No data"
            frames.append(tmp)
        except Exception:
            pass
        try:
            sc_df, _ = _load_stablecoin()
            tmp = sc_df.copy()
            tmp["lab"] = "Stablecoin"
            tmp["evidence_grade"] = "Mixed official" if data.modules.stablecoin else "No data"
            frames.append(tmp)
        except Exception:
            pass
        if frames:
            combined = pd.concat(frames, ignore_index=True, sort=False)
            id_col = "id" if "id" in combined.columns else combined.columns[0]
            title_col = "title" if "title" in combined.columns else "hypothesis"
            matrix = combined[[c for c in [id_col, title_col, "lab", "expected_sign", "evidence_grade"] if c in combined.columns]]
            premium_table(matrix, title="Cross-lab evidence matrix")
            if "expected_sign" in combined.columns:
                counts = combined.groupby("lab", as_index=False).size().rename(columns={"size": "count"})
                fig = charts.ranked_bar(counts, "lab", "count", "Hypothesis count by lab", ascending=False)
                chart_card(fig, "Model readiness — hypothesis coverage")
        methodology_note("Evidence grades are descriptive under current pipeline — not causal identification.")


def render_methodology(data: DashboardData) -> None:
    page_header(
        "Working Paper / Methodology",
        "Thesis · formulas · assumptions · limitations",
        tag="METHODOLOGY",
        meta_badges=[("WORKING PAPERS", "gold")],
    )
    paths = [
        ("VSI Methodology", ROOT / "METHODOLOGY_VALUE_SURVIVAL_INDEX.md"),
        ("Settlement Methodology", ROOT / "settlement_lab" / "METHODOLOGY_SETTLEMENT_ECONOMICS.md"),
        ("Stablecoin Methodology", ROOT / "stablecoin_lab" / "METHODOLOGY_STABLECOIN_SETTLEMENT.md"),
        ("Credibility report", ROOT / "audit" / "research_credibility_report.md"),
    ]
    choice = st.selectbox("Document", [p[0] for p in paths])
    path = dict(paths)[choice]
    st.markdown(read_markdown_snippet(path, 12000))
    col1, col2 = st.columns(2)
    with col1:
        if path.exists():
            st.download_button("Export markdown", path.read_text(encoding="utf-8"), file_name=path.name)
    with col2:
        qpath = ROOT / "audit" / "data_quality_reports" / "data_validation_report.md"
        if qpath.exists():
            st.download_button("Export data quality report", qpath.read_text(encoding="utf-8"), file_name="data_validation_report.md")


def render_gallery(data: DashboardData) -> None:
    page_header(
        "Visual Gallery",
        "Saved figures from VSI · Settlement · Stablecoin pipelines",
        tag="GALLERY",
    )
    if not data.gallery:
        st.info("No figures found. Run: python scripts/make_dashboard_visuals.py")
        return
    module_filter = st.multiselect("Module", sorted({g["module"] for g in data.gallery}), default=sorted({g["module"] for g in data.gallery}))
    items = [g for g in data.gallery if g["module"] in module_filter]
    cols = st.columns(3)
    for i, item in enumerate(items):
        with cols[i % 3]:
            st.markdown(
                f"""<div class="br3n-glass-panel-head" style="border-radius:10px;margin-bottom:0.5rem;">
                <p class="br3n-panel-title">{html_lib.escape(item['title'])}</p>
                <p class="br3n-panel-subtitle">{html_lib.escape(item['module'])} · {html_lib.escape(item['path'])}</p>
                </div>""",
                unsafe_allow_html=True,
            )
            full = ROOT / item["path"]
            if item["ext"] == ".html" and full.exists():
                st.components.v1.html(full.read_text(encoding="utf-8"), height=320, scrolling=True)
            elif item["ext"] in {".png", ".jpg", ".svg"} and full.exists():
                st.image(str(full), use_container_width=True)
            else:
                st.code(str(full))

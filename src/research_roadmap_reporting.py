"""
Generate FX research roadmap report from the question registry.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .research_questions import (
    FLAGSHIP_QUESTION_ID,
    PRIORITY_LANES,
    get_research_question,
    list_research_questions,
    research_questions_dataframe,
)

HIGHEST_LEVEL_THESIS = (
    "FX markets may be mostly random-walk-like as price processes, but not all FX decisions are price "
    "forecasts. Regime, carry, news, flow, and stress variables may fail to predict exchange rates "
    "directly while still improving hedge governance, risk escalation, and decision discipline."
)

NEXT_30_DAY_PLAN = [
    "Extend OOS hedge-governance tests on flagship lane (forecast failure vs hedge usefulness).",
    "Ingest forward-points CSV and rerun carry layer with trading-grade carry economics.",
    "Add R1 vs R2 trend-quality comparison table to regime intelligence outputs.",
    "Validate news-stress and carry-fragility interaction in stress sub-samples.",
    "Expand corridor flow-proxy tests with remittance seasonality where data quality allows.",
    "Document intervention calendar requirements for USD/MXN (planned lane).",
    "Regenerate LAB_STATUS and FX_RESEARCH_ROADMAP after each nightly pipeline run.",
]


def generate_research_roadmap_report(root: Path | str) -> Path:
    root = Path(root)
    out_path = root / "reports" / "FX_RESEARCH_ROADMAP.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    flagship = get_research_question(FLAGSHIP_QUESTION_ID)
    df = research_questions_dataframe()
    priority_rows = df[df["question_id"].isin(PRIORITY_LANES)].sort_values("priority")

    lines = [
        "# FX Research Roadmap",
        "",
        f"*Generated: {datetime.now():%Y-%m-%d %H:%M}*",
        "",
        "## Purpose",
        "",
        "Organize the major unresolved academic and practical questions in FX, and connect each question "
        "to testable models, data needs, scorecards, and research outputs. Research-only — not investment advice.",
        "",
        "## Highest-Level Thesis",
        "",
        HIGHEST_LEVEL_THESIS,
        "",
        "The question is not only whether FX can be predicted. "
        "The question is whether FX decisions can be improved when prediction fails.",
        "",
        "Bowers Frontier Macro Labs does not need to prove that FX is predictable to create research value. "
        "The strongest current path is testing whether regime intelligence improves hedge-governance "
        "decisions when price prediction fails.",
        "",
        "## Current Flagship Lane",
        "",
        f"**{flagship['title']}**",
        "",
        f"- **Core question:** {flagship['core_question']}",
        f"- **Status:** {flagship['current_status']}",
        f"- **Hypothesis:** {flagship['testable_hypothesis']}",
        "",
        "## Priority Research Questions",
        "",
    ]

    for _, row in priority_rows.iterrows():
        lines.extend(
            [
                f"### {row['priority']}. {row['title']}",
                "",
                f"- **Question:** {row['core_question']}",
                f"- **Status:** {row['current_status']}",
                f"- **Modules:** {row['model_modules']}",
                f"- **Outputs:** {row['output_files']}",
                "",
            ]
        )

    lines.extend(["## Data Needed by Question", ""])
    for q in list_research_questions():
        data = ", ".join(q["data_needed"])
        lines.append(f"- **{q['title']}:** {data}")

    lines.extend(["", "## Model Modules by Question", ""])
    for q in list_research_questions():
        mods = ", ".join(q["model_modules"])
        lines.append(f"- **{q['title']}:** {mods}")

    lines.extend(["", "## Output Files by Question", ""])
    for q in list_research_questions():
        outs = ", ".join(q["output_files"]) if q["output_files"] else "— (not yet defined)"
        lines.append(f"- **{q['title']}:** {outs}")

    lines.extend(["", "## Current Status", ""])
    for q in list_research_questions():
        lines.append(f"- **{q['title']}** — {q['current_status']}")

    lines.extend(["", "## Next 30-Day Plan", ""])
    for item in NEXT_30_DAY_PLAN:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Claim Discipline",
            "",
            "The lab does not claim FX prediction certainty, random-walk disproof, guaranteed trading returns, "
            "or live-trading readiness. Results depend on data quality. Forecast accuracy, trading P&L, and "
            "hedge usefulness are evaluated separately.",
            "",
        ]
    )

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path

"""
Central registry of major unanswered FX research questions.

Connects each question to model modules, data needs, and lab outputs.
Research-only — not investment advice.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

RESEARCH_QUESTION_REGISTRY: dict[str, dict[str, Any]] = {
    "fundamentals_disconnect": {
        "title": "Fundamentals Disconnect",
        "core_question": "When do fundamentals matter, and when are they overwhelmed by flows, positioning, liquidity, and risk appetite?",
        "why_it_matters": "Exchange rates often appear disconnected from macro fundamentals at short and medium horizons; understanding regime-conditional relevance is central to FX research.",
        "testable_hypothesis": "Fundamentals align more with FX behavior in R2, low-news-stress, and stable-carry regimes than in R1/R3 stress or high-liquidity-stress environments.",
        "data_needed": [
            "FX spot",
            "interest rates",
            "inflation",
            "policy rates",
            "trade/current account proxies",
            "VIX / dollar stress",
            "news uncertainty",
            "regime labels",
        ],
        "model_modules": [
            "features.py",
            "regimes.py",
            "news_features.py",
            "carry_features.py",
            "research_runner.py",
        ],
        "output_files": [
            "data/processed/usdmxn_features_regimes.csv",
            "data/outputs/academic_test_results.csv",
            "data/outputs/news_feature_test_results.csv",
        ],
        "current_status": "Partial — regime and stress layers exist; dedicated fundamental panel not yet built.",
        "priority": 6,
    },
    "regime_dependent_uip": {
        "title": "Regime-Dependent UIP",
        "core_question": "Is uncovered interest parity wrong, incomplete, or regime-dependent?",
        "why_it_matters": "UIP failures drive carry research and hedge economics; regime conditioning may explain apparent contradictions in the literature.",
        "testable_hypothesis": "UIP may appear to fail in calm regimes and reassert itself violently during stress regimes (R1, carry fragility, high VIX/dollar stress).",
        "data_needed": [
            "policy rate differentials",
            "forward points",
            "FX swaps",
            "spot returns",
            "VIX / dollar stress",
            "news stress",
            "regime labels",
        ],
        "model_modules": [
            "carry_features.py",
            "carry_models.py",
            "carry_tests.py",
            "forward_points.py",
        ],
        "output_files": [
            "data/processed/usdmxn_features_regimes_carry.csv",
            "data/outputs/carry_regime_test_results.csv",
            "reports/CARRY_RESEARCH_FRAMEWORK.md",
        ],
        "current_status": "Active — carry layer and UIP tests running on policy-rate proxy; forward points placeholder.",
        "priority": 2,
    },
    "carry_fragility": {
        "title": "Carry Fragility",
        "core_question": "Are carry returns payment for bearing rare disaster risk, or evidence of market inefficiency?",
        "why_it_matters": "Carry trades can look profitable until stress regimes; fragility indexing separates stable yield from hidden crash risk.",
        "testable_hypothesis": "High carry combined with low realized vol, strong trend, and rising news/dollar stress predicts drawdowns, vol spikes, and carry reversals.",
        "data_needed": [
            "policy rates",
            "forward points",
            "volatility",
            "dollar stress",
            "news stress",
            "liquidity/spread proxies",
            "regime labels",
        ],
        "model_modules": [
            "carry_features.py",
            "carry_models.py",
            "carry_tests.py",
            "carry_hedge_governance.py",
        ],
        "output_files": [
            "data/processed/usdmxn_features_regimes_carry.csv",
            "data/outputs/carry_regime_test_results.csv",
            "data/outputs/carry_hedge_governance_scorecard.csv",
        ],
        "current_status": "Active — carry fragility index and regime tests implemented.",
        "priority": 3,
    },
    "random_walk_failure": {
        "title": "Random Walk Failure",
        "core_question": "Is random walk a universal model of FX, or a regime-specific model?",
        "why_it_matters": "Random walk is the dominant FX forecast benchmark; regime-specific validity maps inform when conditional models are worth testing.",
        "testable_hypothesis": "R4 is most random-walk-like; R2 may show structure; R1/R3 carry higher noise or stress structure.",
        "data_needed": [
            "FX spot",
            "regime labels",
            "daily returns",
            "walk-forward splits",
        ],
        "model_modules": [
            "random_walk_validity.py",
            "model_evaluation.py",
            "model_walk_forward.py",
            "ladder/level2_oos.py",
            "ladder/level4_forecast.py",
        ],
        "output_files": [
            "data/outputs/random_walk_validity_map.csv",
            "data/outputs/model_zoo_forecast_scorecard.csv",
            "data/outputs/walkforward_oos.csv",
            "reports/research_ladder/level4_forecast_summary.csv",
        ],
        "current_status": "Active — random-walk validity map and model zoo forecast scorecards available.",
        "priority": 6,
    },
    "order_flow_bridge": {
        "title": "Public Flow Proxies",
        "core_question": "Can public proxies approximate private flow pressure well enough to improve FX risk decisions?",
        "why_it_matters": "True order flow is usually private; calendar and payment proxies may still identify risk windows for treasury discipline.",
        "testable_hypothesis": "Payday, month-end, holiday, and central-bank meeting windows show elevated volatility, regime shifts, or hedge-turnover stress.",
        "data_needed": [
            "FX spot",
            "corridor calendar proxies",
            "remittance seasonality",
            "central-bank calendars",
            "holidays",
        ],
        "model_modules": [
            "flow_proxies.py",
            "flow_pressure_tests.py",
        ],
        "output_files": [
            "data/processed/usdmxn_features_regimes_flow.csv",
            "data/outputs/flow_pressure_test_results.csv",
        ],
        "current_status": "Active — USD/MXN flow proxy tests running; exploratory, not causal.",
        "priority": 4,
    },
    "remittance_flow_pressure": {
        "title": "Remittance Flow Pressure",
        "core_question": "Do millions of small cross-border payments create measurable short-term currency pressure in remittance-heavy corridors?",
        "why_it_matters": "Payment-corridor FX risk is under-studied relative to macro and institutional flow research.",
        "testable_hypothesis": "Flow windows in US_MX, US_IN, US_PH, US_CO, US_BR corridors show abnormal vol, regime frequency, or hedge-governance stress.",
        "data_needed": [
            "FX spot per corridor",
            "official remittance data",
            "public calendar proxies",
            "central bank remittance data",
        ],
        "model_modules": [
            "corridor_runner.py",
            "corridor_reporting.py",
            "flow_proxies.py",
            "flow_pressure_tests.py",
        ],
        "output_files": [
            "data/outputs/corridor_master_scorecard.csv",
            "data/outputs/corridor_flow_pressure_summary.csv",
            "reports/corridor_roadmap_report.md",
        ],
        "current_status": "Active — multi-corridor roadmap with flow and hedge scorecards.",
        "priority": 4,
    },
    "forecast_failure_hedge_usefulness": {
        "title": "Forecast Failure and Hedge Usefulness",
        "core_question": "Can FX regime models fail to beat random walk as forecasts but still improve hedge governance?",
        "why_it_matters": "Treasury teams may care more about hedge turnover, cost, exposure volatility, and decision discipline than RMSE.",
        "testable_hypothesis": "Regime-based and no-change-in-range hedge policies reduce hedge turnover and cost-adjusted exposure volatility versus static hedge policies, even when price forecasts fail random-walk tests.",
        "data_needed": [
            "FX spot",
            "regime labels",
            "hedge policy rules",
            "transaction cost assumptions",
            "forward points later",
            "exposure schedules later",
        ],
        "model_modules": [
            "hedge_governance.py",
            "carry_hedge_governance.py",
            "random_walk_validity.py",
            "model_zoo.py",
        ],
        "output_files": [
            "data/outputs/hedge_governance_scorecard.csv",
            "data/outputs/carry_hedge_governance_scorecard.csv",
            "data/outputs/flagship_hedge_oos_scorecard.csv",
            "data/outputs/random_walk_validity_map.csv",
            "data/outputs/model_zoo_hedge_scorecard.csv",
            "reports/FLAGSHIP_RESEARCH_LANE.md",
        ],
        "current_status": "Flagship active research lane.",
        "priority": 1,
    },
    "no_arbitrage_breakdown": {
        "title": "No-Arbitrage Breakdown",
        "core_question": "Is FX pricing partly determined by balance-sheet scarcity rather than pure no-arbitrage?",
        "why_it_matters": "CIP and forward pricing deviations affect hedge costs and carry economics during funding stress.",
        "testable_hypothesis": "Forward/carry anomalies and hedge costs widen during balance-sheet stress windows (quarter-end, year-end, funding stress).",
        "data_needed": [
            "forward points",
            "cross-currency basis",
            "FX swaps",
            "bid/ask spreads",
            "funding stress proxies",
            "professional data source",
        ],
        "model_modules": [
            "forward_points.py",
            "hedge_costs.py",
            "carry_features.py",
        ],
        "output_files": [
            "data/raw/forwards_usdmxn.csv.example",
            "reports/CARRY_RESEARCH_FRAMEWORK.md",
        ],
        "current_status": "Planned — forward points CSV ingest wired; basis and funding stress data not yet integrated.",
        "priority": 8,
    },
    "central_bank_intervention": {
        "title": "Central-Bank Intervention",
        "core_question": "Does FX intervention work by changing supply, signaling policy, breaking momentum, or coordinating expectations?",
        "why_it_matters": "EM corridors (including USD/MXN) face intermittent official intervention that may interact with regime labels.",
        "testable_hypothesis": "Intervention effects differ by regime — stronger in R1 stress, weaker or trend-breaking in R2.",
        "data_needed": [
            "central bank intervention data",
            "reserves",
            "policy dates",
            "FX spot",
            "volatility",
            "regime labels",
        ],
        "model_modules": [
            "regimes.py",
            "features.py",
        ],
        "output_files": [],
        "current_status": "Planned — intervention calendar and event study not yet built.",
        "priority": 9,
    },
    "r1_vs_r2_trend_quality": {
        "title": "R1 vs R2 Trend Quality",
        "core_question": "Are high-volatility FX trends less forecastable because they reflect forced liquidation rather than information?",
        "why_it_matters": "Not all trends are equal; R2 may be information-rich while R1 may signal stress or liquidation.",
        "testable_hypothesis": "R2 shows higher continuation and cleaner drawdown profiles; R1 shows higher news/carry fragility and reversal risk.",
        "data_needed": [
            "FX spot",
            "regime labels",
            "news stress",
            "carry fragility",
            "VIX/dollar stress",
            "flow window proxies",
        ],
        "model_modules": [
            "regimes.py",
            "random_walk_validity.py",
            "news_features.py",
            "carry_features.py",
        ],
        "output_files": [
            "data/outputs/r1_r2_trend_quality_comparison.csv",
            "data/outputs/random_walk_validity_map.csv",
            "data/outputs/regime_attribution_flat_range.csv",
            "data/outputs/news_feature_test_results.csv",
        ],
        "current_status": "Active — regime intelligence and early R1/R2 comparisons in validity and news tests.",
        "priority": 5,
    },
    "corporate_hedge_objective": {
        "title": "Corporate Hedge Objective Function",
        "core_question": "What is the optimal hedge policy when prediction is weak, hedge costs are real, and over-adjustment is costly?",
        "why_it_matters": "Corporate treasury optimizes cash-flow stability and policy compliance, not forecast RMSE or trading Sharpe.",
        "testable_hypothesis": "Regime and no-change-in-range policies improve cost-adjusted protection and policy stability versus static or calendar hedging.",
        "data_needed": [
            "FX spot",
            "regime labels",
            "hedge cost assumptions",
            "exposure schedules",
            "forward points later",
        ],
        "model_modules": [
            "hedge_governance.py",
            "carry_hedge_governance.py",
            "hedge_costs.py",
            "fx_desk_framework.py",
        ],
        "output_files": [
            "data/outputs/hedge_governance_scorecard.csv",
            "data/outputs/hedge_policy_scorecard.csv",
            "data/outputs/fx_desk_scorecard.csv",
        ],
        "current_status": "Active — hedge policy suite and FX desk scorecards implemented.",
        "priority": 7,
    },
    "ai_decision_architecture": {
        "title": "AI Decision Architecture",
        "core_question": "Does AI create value in FX by improving decision architecture rather than prediction accuracy?",
        "why_it_matters": "AI may improve classification, monitoring, memos, and policy discipline even when it does not beat random walk on price forecasts.",
        "testable_hypothesis": "Dashboard, memos, and scorecards improve explanation quality and reduce over-adjustment versus raw model signals alone.",
        "data_needed": [
            "model outputs",
            "regime labels",
            "hedge scorecards",
            "publication memos",
        ],
        "model_modules": [
            "luxury_dashboard.py",
            "flagship_memo.py",
            "lab_status.py",
            "self_improve/runner.py",
        ],
        "output_files": [
            "reports/LAB_STATUS.md",
            "reports/publication/HEDGE_GOVERNANCE_MEMO.md",
            "reports/publication/UNANSWERED_FX_QUESTIONS_SUMMARY.md",
        ],
        "current_status": "Partial — dashboard, memos, and lab status exist; formal AI-layer evaluation not yet scored.",
        "priority": 10,
    },
}

PRIORITY_LANES = [
    "forecast_failure_hedge_usefulness",
    "regime_dependent_uip",
    "carry_fragility",
    "order_flow_bridge",
    "r1_vs_r2_trend_quality",
]

FLAGSHIP_QUESTION_ID = "forecast_failure_hedge_usefulness"


def get_research_question(question_id: str) -> dict[str, Any]:
    if question_id not in RESEARCH_QUESTION_REGISTRY:
        raise KeyError(f"Unknown research question: {question_id}")
    return {"question_id": question_id, **RESEARCH_QUESTION_REGISTRY[question_id]}


def list_research_questions(priority: Optional[int] = None) -> list[dict[str, Any]]:
    items = [get_research_question(qid) for qid in RESEARCH_QUESTION_REGISTRY]
    items.sort(key=lambda x: (x["priority"], x["question_id"]))
    if priority is not None:
        items = [q for q in items if q["priority"] == priority]
    return items


def research_questions_dataframe() -> pd.DataFrame:
    rows = []
    for qid, meta in RESEARCH_QUESTION_REGISTRY.items():
        rows.append(
            {
                "question_id": qid,
                "title": meta["title"],
                "core_question": meta["core_question"],
                "why_it_matters": meta["why_it_matters"],
                "testable_hypothesis": meta["testable_hypothesis"],
                "priority": meta["priority"],
                "current_status": meta["current_status"],
                "model_modules": ", ".join(meta["model_modules"]),
                "output_files": ", ".join(meta["output_files"]) if meta["output_files"] else "—",
                "data_needed": ", ".join(meta["data_needed"]),
            }
        )
    df = pd.DataFrame(rows)
    return df.sort_values(["priority", "question_id"]).reset_index(drop=True)


def research_question_status_report() -> str:
    """Markdown summary of registry status counts."""
    df = research_questions_dataframe()
    flagship = get_research_question(FLAGSHIP_QUESTION_ID)

    def _count(prefix: str) -> int:
        return int(df["current_status"].str.startswith(prefix, na=False).sum())

    lines = [
        "# Research Question Status",
        "",
        f"**Flagship lane:** {flagship['title']} — {flagship['current_status']}",
        "",
        "## Counts by status prefix",
        f"- Active: {_count('Active')}",
        f"- Partial: {_count('Partial')}",
        f"- Planned: {_count('Planned')}",
        f"- Flagship: {int(df['current_status'].str.contains('Flagship', na=False).sum())}",
        "",
        "## Priority lanes (top 5)",
    ]
    for qid in PRIORITY_LANES:
        q = get_research_question(qid)
        lines.append(f"- **{q['title']}** (priority {q['priority']}): {q['current_status']}")
    lines.extend(["", "## Full registry", ""])
    for _, row in df.iterrows():
        lines.append(f"- `{row['question_id']}` — {row['title']} [{row['current_status']}]")
    return "\n".join(lines)

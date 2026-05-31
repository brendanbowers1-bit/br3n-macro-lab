"""Research modeling layer — hypothesis tests, not prediction hype."""

from __future__ import annotations

import pandas as pd
import numpy as np

from src.models.event_study import run_dxy_event_study
from src.models.panel_regression import (
    build_panel_dataset,
    panel_regression_with_fe,
    remittance_growth_regression,
)


def panel_regression_summary(
    welfare: pd.DataFrame,
    hidden_fx_tax: pd.DataFrame,
    macro: pd.DataFrame | None = None,
) -> dict:
    """Panel regression with corridor and year fixed effects."""
    panel = build_panel_dataset(welfare, hidden_fx_tax, macro)
    result = panel_regression_with_fe(panel)
    growth = remittance_growth_regression(panel)
    result["remittance_growth_model"] = growth
    return result


def corridor_clustering_features(indices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build feature matrix for corridor/country clustering."""
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    rows = []
    hft = indices.get("hidden_fx_tax")
    if hft is not None and not hft.empty:
        for corridor, g in hft.groupby("corridor"):
            rows.append(
                {
                    "entity": corridor,
                    "entity_type": "corridor",
                    "hidden_fx_tax": g["hidden_fx_tax_pct"].mean(),
                    "volatility": g.get("volatility_30d", pd.Series([0.12])).mean(),
                }
            )
    cred = indices.get("currency_credibility")
    if cred is not None and not cred.empty:
        for _, r in cred.iterrows():
            rows.append(
                {
                    "entity": r["country"],
                    "entity_type": "country",
                    "credibility": r.get("credibility_score"),
                    "inflation": r.get("inflation_yoy"),
                    "hidden_fx_tax": np.nan,
                    "volatility": np.nan,
                }
            )
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    num = df.select_dtypes(include=[np.number]).fillna(0)
    if len(df) >= 3:
        scaler = StandardScaler()
        X = scaler.fit_transform(num)
        k = min(3, len(df))
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        df["cluster"] = km.fit_predict(X)
    return df


def stress_forecast_logistic(stress: pd.DataFrame, fx_rates: pd.DataFrame) -> dict:
    """Simple logistic model: high stress today → depreciation stress next 90d."""
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        return {"error": "scikit-learn required"}

    fx = fx_rates.sort_values(["currency", "date"]).copy()
    fx["stress_next_90d"] = (
        fx.groupby("currency")["usd_fx_rate"].pct_change(63).shift(-63).abs() > 0.05
    ).astype(int)
    latest_stress = stress.set_index("currency")["stress_score"].to_dict()
    fx["stress_score"] = fx["currency"].map(latest_stress).fillna(50)
    fx["volatility_30d"] = fx.get("volatility_30d", 0.12)
    use = fx.dropna(subset=["stress_next_90d", "volatility_30d"])
    if len(use) < 50:
        return {
            "status": "insufficient_data",
            "n": len(use),
            "limitation": "Need longer FX history for stress forecast.",
        }
    X = use[["stress_score", "volatility_30d"]].astype(float)
    y = use["stress_next_90d"].astype(int)
    if y.nunique() < 2:
        return {"status": "single_class", "limitation": "Not enough stress events in sample."}
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    model = LogisticRegression(max_iter=500)
    model.fit(Xs, y)
    return {
        "n": len(use),
        "accuracy_in_sample": float(model.score(Xs, y)),
        "coefficients": dict(zip(X.columns, model.coef_.ravel().tolist())),
        "interpretation": "In-sample only; research placeholder until walk-forward labels.",
        "limitation": "Not validated OOS; do not use for trading.",
    }


def full_model_lab_report(indices: dict[str, pd.DataFrame]) -> dict:
    return {
        "panel_regression": panel_regression_summary(
            indices["remittance_welfare"],
            indices["hidden_fx_tax"],
            indices.get("macro_country_panel"),
        ),
        "dxy_event_study": run_dxy_event_study(
            indices["hidden_fx_tax"],
            indices["remittance_welfare"],
        ),
        "clustering": corridor_clustering_features(indices).to_dict(orient="records"),
        "stress_forecast": stress_forecast_logistic(
            indices["currency_stress"],
            indices.get("fx_rates", pd.DataFrame()),
        ),
    }

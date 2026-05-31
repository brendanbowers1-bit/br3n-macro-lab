"""
Panel regression with corridor and time fixed effects.

Research-only — tests whether hidden FX tax reduces real remittance value.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


def build_panel_dataset(
    welfare: pd.DataFrame,
    hidden_fx_tax: pd.DataFrame,
    macro: pd.DataFrame | None = None,
) -> pd.DataFrame:
    h = hidden_fx_tax.groupby(["corridor", "date"], as_index=False).agg(
        hidden_fx_tax_pct=("hidden_fx_tax_pct", "mean"),
        volatility_30d=("volatility_30d", "mean"),
    )
    w = welfare.copy()
    if "year" not in w.columns and "date" in w.columns:
        w["year"] = pd.to_datetime(w["date"]).dt.year
    panel = w.merge(h, on=["corridor", "date"], how="left", suffixes=("", "_hft"))
    if "hidden_fx_tax_pct" not in panel.columns or panel["hidden_fx_tax_pct"].isna().all():
        h_mean = hidden_fx_tax.groupby("corridor", as_index=False)["hidden_fx_tax_pct"].mean()
        panel = panel.merge(h_mean, on="corridor", how="left", suffixes=("", "_corridor"))
        panel["hidden_fx_tax_pct"] = panel["hidden_fx_tax_pct"].fillna(panel.get("hidden_fx_tax_pct_corridor"))

    panel["real_value_delivered_pct"] = panel.get(
        "real_value_delivered_pct", 1 - panel["welfare_loss_pct"]
    )
    if macro is not None and not macro.empty:
        recv = hidden_fx_tax[["corridor", "receiver_country"]].drop_duplicates()
        panel = panel.merge(recv, on="corridor", how="left")
        m = macro.sort_values("date").groupby("country", as_index=False).tail(1)
        panel = panel.merge(
            m[["country", "inflation_yoy", "gdp_growth"]],
            left_on="receiver_country",
            right_on="country",
            how="left",
        )
    return panel.dropna(subset=["real_value_delivered_pct", "hidden_fx_tax_pct"])


def panel_regression_with_fe(
    panel: pd.DataFrame,
    dependent: str = "real_value_delivered_pct",
) -> dict:
    """
    OLS with corridor and year fixed effects (dummy variables).
    """
    try:
        import statsmodels.api as sm
    except ImportError:
        return {"error": "statsmodels required"}

    df = panel.copy()
    if len(df) < 8:
        return {"error": "insufficient observations", "n": len(df)}

    regressors = ["hidden_fx_tax_pct"]
    for col in ("volatility_30d", "inflation_yoy", "gdp_growth"):
        if col in df.columns and df[col].notna().any():
            regressors.append(col)

    fe_cols = []
    if "corridor" in df.columns:
        fe_cols.append("corridor")
    if "year" in df.columns:
        fe_cols.append("year")

    X_parts = [df[regressors].astype(float)]
    for fe in fe_cols:
        dummies = pd.get_dummies(df[fe].astype(str), prefix=fe, drop_first=True)
        X_parts.append(dummies.astype(float))

    X = sm.add_constant(pd.concat(X_parts, axis=1).astype(float))
    y = df[dependent].astype(float)
    try:
        model = sm.OLS(y, X).fit(cov_type="HC1")
    except Exception as exc:
        return {"error": str(exc), "n": len(df), "limitation": "Singular design matrix — reduce FE or add data."}

    return {
        "n": int(model.nobs),
        "r_squared": float(model.rsquared),
        "r_squared_adj": float(model.rsquared_adj),
        "hidden_fx_tax_coef": float(model.params.get("hidden_fx_tax_pct", np.nan)),
        "hidden_fx_tax_pvalue": float(model.pvalues.get("hidden_fx_tax_pct", np.nan)),
        "fixed_effects": fe_cols,
        "regressors": regressors,
        "interpretation": (
            "Negative hidden_fx_tax coefficient supports hypothesis: higher hidden tax "
            "→ lower real value delivered, conditional on corridor and year FE."
        ),
        "limitation": "Curated/mixed data; causal claims require instrument or natural experiment.",
    }


def remittance_growth_regression(panel: pd.DataFrame) -> dict:
    """Test whether hidden FX tax predicts remittance growth (corridor-year panel)."""
    try:
        import statsmodels.api as sm
    except ImportError:
        return {"error": "statsmodels required"}

    df = panel.sort_values(["corridor", "year"])
    df["remittance_growth"] = df.groupby("corridor")["remittance_usd"].pct_change()
    df = df.dropna(subset=["remittance_growth", "hidden_fx_tax_pct"])
    if len(df) < 6:
        return {"error": "insufficient observations for growth regression", "n": len(df)}

    X = sm.add_constant(df[["hidden_fx_tax_pct"]])
    if "inflation_yoy" in df.columns:
        X["inflation_yoy"] = df["inflation_yoy"].fillna(0)
    model = sm.OLS(df["remittance_growth"], X).fit(cov_type="HC1")
    return {
        "n": int(model.nobs),
        "hidden_fx_tax_coef_on_growth": float(model.params.get("hidden_fx_tax_pct", np.nan)),
        "pvalue": float(model.pvalues.get("hidden_fx_tax_pct", np.nan)),
        "interpretation": "Negative coef → higher hidden tax associated with slower remittance growth.",
    }

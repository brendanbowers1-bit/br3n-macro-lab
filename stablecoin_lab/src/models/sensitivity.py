"""Sensitivity analysis for Stablecoin Settlement Window Lab."""

from __future__ import annotations

import pandas as pd

from src.config.research_settings import SENSITIVITY_CASES


def run_sensitivity_analysis(tables: dict[str, pd.DataFrame] | None = None) -> pd.DataFrame:
    if tables is None:
        try:
            from src.data.loaders import load_all_tables
            tables = load_all_tables()
        except ImportError:
            tables = {}

    from src.indices.compliance_settlement_drag import calculate_compliance_drag_table
    from src.indices.stablecoin_dollarization import calculate_stablecoin_dollarization_table
    from src.indices.stablecoin_finality_quality import calculate_stablecoin_finality_quality_table
    from src.indices.stablecoin_value_survival import calculate_stablecoin_vsi_table
    from src.indices.tokenized_money_singleness import calculate_singleness_table
    from src.models.digital_run_velocity import calculate_digital_run_velocity_table
    from src.models.settlement_window_compression import calculate_settlement_window_compression_table
    from src.models.stablecoin_liquidity_transformation import calculate_liquidity_transformation_table

    frames = []
    for case in SENSITIVITY_CASES:
        sfqi = calculate_stablecoin_finality_quality_table(
            tables.get("blockchain_settlement_characteristics", pd.DataFrame()),
            tables.get("stablecoin_reserves"),
            tables.get("stablecoin_redemption_characteristics"),
            tables.get("off_ramp_characteristics"),
            tables.get("stablecoin_price_peg"),
        )
        if not sfqi.empty:
            sfqi = sfqi.assign(model_name="SFQI", sensitivity_case=case)
            frames.append(sfqi)

        csd = calculate_compliance_drag_table(
            tables.get("off_ramp_characteristics", pd.DataFrame()),
            tables.get("blockchain_settlement_characteristics"),
            tables.get("stablecoin_redemption_characteristics"),
            sensitivity_case=case,
        )
        if not csd.empty:
            frames.append(csd.assign(model_name="CSD", sensitivity_case=case))

        vsi = calculate_stablecoin_vsi_table(
            tables.get("remittance_comparison", pd.DataFrame()),
            sensitivity_case=case,
        )
        if not vsi.empty:
            frames.append(vsi.assign(model_name="SVSI", sensitivity_case=case))

        swc = calculate_settlement_window_compression_table(
            tables.get("remittance_comparison", pd.DataFrame()),
            tables.get("blockchain_settlement_characteristics"),
            tables.get("off_ramp_characteristics"),
            sensitivity_case=case,
        )
        if not swc.empty:
            frames.append(swc.assign(model_name="SWC", sensitivity_case=case))

        slt = calculate_liquidity_transformation_table(
            tables.get("stablecoin_supply", pd.DataFrame()),
            tables.get("stablecoin_reserves"),
            tables.get("stablecoin_redemption_characteristics"),
            sensitivity_case=case,
        )
        if not slt.empty:
            frames.append(slt.assign(model_name="SLT", sensitivity_case=case))

        sing = calculate_singleness_table(
            tables.get("stablecoin_price_peg", pd.DataFrame()),
            tables.get("stablecoin_reserves"),
            tables.get("stablecoin_redemption_characteristics"),
        )
        if not sing.empty:
            frames.append(sing.assign(model_name="Singleness", sensitivity_case=case))

        drv = calculate_digital_run_velocity_table(
            tables.get("stablecoin_supply", pd.DataFrame()),
            tables.get("stablecoin_redemption_characteristics"),
            tables.get("stablecoin_price_peg"),
        )
        if not drv.empty:
            frames.append(drv.assign(model_name="DRV", sensitivity_case=case))

        dollar = calculate_stablecoin_dollarization_table(
            tables.get("macro", pd.DataFrame()),
            tables.get("stablecoin_supply"),
            tables.get("remittance_comparison"),
        )
        if not dollar.empty:
            frames.append(dollar.assign(model_name="Dollarization", sensitivity_case=case))

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def sensitivity_summary(results: pd.DataFrame, score_col: str = "stablecoin_finality_quality_index") -> pd.DataFrame:
    if results.empty or score_col not in results.columns:
        for alt in ("swc_extended", "stablecoin_vsi", "compliance_drag_index", "singleness_index"):
            if alt in results.columns:
                score_col = alt
                break
        else:
            return pd.DataFrame()

    sub = results[results[score_col].notna()]
    if sub.empty or "entity" not in sub.columns:
        return pd.DataFrame()

    return (
        sub.groupby("entity", as_index=False)
        .agg(
            score_min=(score_col, "min"),
            score_max=(score_col, "max"),
            score_mean=(score_col, "mean"),
        )
        .assign(score_range=lambda d: d["score_max"] - d["score_min"])
        .sort_values("score_mean")
    )

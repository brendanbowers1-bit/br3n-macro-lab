"""Run all flagship indices and save processed outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.loaders import load_all_canonical_tables
from src.utils.paths import OUTPUTS_DIR, PROCESSED_DIR

from .currency_credibility import calculate_currency_credibility_table
from .currency_stress import calculate_currency_stress_table
from .dollar_dependency import calculate_dollar_dependency_table
from .hidden_fx_tax import calculate_hidden_fx_tax_table
from .labor_conversion import calculate_labor_conversion_table
from .remittance_welfare import calculate_remittance_welfare_table


def run_all_indices(tables: dict[str, pd.DataFrame] | None = None) -> dict[str, pd.DataFrame]:
    tables = tables or load_all_canonical_tables()
    hft = calculate_hidden_fx_tax_table(
        tables["corridor_prices"], tables["fx_rates"], tables["macro_country_panel"]
    )
    welfare = calculate_remittance_welfare_table(hft, tables["remittance_flows"])
    sovereignty = tables.get("country_sovereignty")
    credibility = calculate_currency_credibility_table(
        tables["macro_country_panel"],
        tables["fx_rates"],
        sovereignty,
    )
    dollar_dep = calculate_dollar_dependency_table(
        tables["macro_country_panel"],
        tables["currency_market_structure"],
        tables["remittance_flows"],
        sovereignty,
    )
    labor = calculate_labor_conversion_table(
        tables["macro_country_panel"], tables["fx_rates"], hft
    )
    stress = calculate_currency_stress_table(
        tables["fx_rates"], tables["macro_country_panel"]
    )
    return {
        "hidden_fx_tax": hft,
        "remittance_welfare": welfare,
        "currency_credibility": credibility,
        "dollar_dependency": dollar_dep,
        "labor_conversion": labor,
        "currency_stress": stress,
    }


def save_index_outputs(indices: dict[str, pd.DataFrame], out_dir: Path | None = None) -> dict[str, Path]:
    out_dir = out_dir or OUTPUTS_DIR
    proc = PROCESSED_DIR
    proc.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, df in indices.items():
        p_out = out_dir / f"index_{name}.csv"
        p_proc = proc / f"index_{name}.csv"
        df.to_csv(p_out, index=False)
        df.to_csv(p_proc, index=False)
        paths[name] = p_out
    return paths

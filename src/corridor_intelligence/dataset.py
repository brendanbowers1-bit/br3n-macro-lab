"""Load validated USD/MXN corridor source data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = ROOT / "data" / "raw" / "corridor" / "us_mx_banxico_remittances.csv"


def load_us_mx_remittances(path: Path | None = None) -> pd.DataFrame:
    csv_path = path or DEFAULT_CSV
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing corridor dataset: {csv_path}")
    df = pd.read_csv(csv_path)
    df["month"] = pd.to_datetime(df["month"])
    df = df.sort_values("month").reset_index(drop=True)
    df["month_label"] = df["month"].dt.strftime("%b %Y")
    return df

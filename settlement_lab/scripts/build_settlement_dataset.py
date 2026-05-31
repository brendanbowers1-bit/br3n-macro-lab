#!/usr/bin/env python3
"""Build settlement lab processed dataset."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_dataset import build_settlement_dataset, save_outputs, save_processed


def main() -> None:
    print("BR3N Settlement Economics Lab — build dataset")
    ds = build_settlement_dataset()
    paths = save_processed(ds)
    save_outputs(ds)
    mock = ds["_mock_data_flag"]["mock_data_flag"].iloc[0]
    print(f"Mock data: {mock}")
    for k, p in paths.items():
        print(f"  {k}: {p}")
    print(ds["_validation"].to_string(index=False))


if __name__ == "__main__":
    main()

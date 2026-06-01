"""
Data lineage attachment for Stablecoin Settlement Window Lab.

Every row must carry source and quality metadata when NO_UNLABELED_DATA=True.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config.data_sources import get_source
from src.config.research_settings import METHODOLOGY_VERSION, MOCK_SOURCE_ID


def calculate_file_hash(path: Path) -> str:
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def base_lineage(
    source_id: str,
    raw_file_name: str = "",
    raw_file_hash: str = "n/a",
    transformation_script: str = "stablecoin_lab/src/data/build_dataset.py",
    mock_data_flag: bool = False,
    observed: bool = True,
    manual: bool = False,
    blockchain_network: str = "",
    jurisdiction: str = "",
) -> dict:
    try:
        spec = get_source(source_id)
        tier = spec.credibility_tier
        provider = spec.provider
        source_name = spec.name
        url = spec.url_placeholder
        license_note = spec.limitations or spec.usage_notes
        update_freq = spec.update_frequency
    except KeyError:
        tier = 5
        provider = "unknown"
        source_name = source_id
        url = "N/A"
        license_note = "Unknown source"
        update_freq = "unknown"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "source_name": source_name,
        "source_url_or_reference": url,
        "data_provider": provider,
        "publication_date": "",
        "extraction_date": now,
        "vintage_date": "",
        "update_frequency": update_freq,
        "license_or_usage_note": license_note,
        "raw_file_name": raw_file_name,
        "raw_file_hash_sha256": raw_file_hash,
        "transformation_script": transformation_script,
        "methodology_version": METHODOLOGY_VERSION,
        "observed_vs_estimated_flag": "observed" if observed and not mock_data_flag else "estimated",
        "official_vs_manual_flag": "manual" if manual or source_id == "manual_assumptions" else "official",
        "mock_data_flag": mock_data_flag,
        "source_id": MOCK_SOURCE_ID if mock_data_flag else source_id,
        "credibility_tier": tier,
        "blockchain_network": blockchain_network,
        "jurisdiction": jurisdiction,
    }


def attach_lineage(df: pd.DataFrame, lineage: dict) -> pd.DataFrame:
    out = df.copy()
    for k, v in lineage.items():
        if k not in out.columns:
            out[k] = v
        elif out[k].isna().all():
            out[k] = v
    return out

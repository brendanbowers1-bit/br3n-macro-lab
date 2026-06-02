"""Download FRED public graph CSV (no API key)."""

from __future__ import annotations

from urllib.request import urlopen


def fetch_fred_graph_csv(series_id: str, *, min_date: str | None = None) -> str:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    with urlopen(url, timeout=60) as resp:
        content = resp.read().decode("utf-8")
    if not min_date:
        return content
    lines = content.strip().splitlines()
    if not lines:
        return content
    header, *rows = lines
    filtered = [header]
    for row in rows:
        if not row.strip():
            continue
        obs = row.split(",")[0].strip('"')
        if obs >= min_date:
            filtered.append(row)
    return "\n".join(filtered) + "\n"

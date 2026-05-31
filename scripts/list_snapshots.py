#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.audit.snapshots import list_snapshots

def main():
    rows = list_snapshots()
    if not rows:
        print("No snapshots found in _snapshots/")
        return
    print(f"{'ID':<40} {'MB':>8}  PATH")
    for r in rows:
        print(f"{r['snapshot_id']:<40} {r['size_mb']:>8.2f}  {r['path']}")

if __name__ == "__main__":
    main()

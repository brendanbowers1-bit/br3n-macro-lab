#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.audit.snapshots import create_snapshot

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--reason", default="manual snapshot")
    p.add_argument("--created-by", default="user")
    args = p.parse_args()
    path = create_snapshot(reason=args.reason, created_by=args.created_by)
    print(f"Snapshot: {path}")

if __name__ == "__main__":
    main()

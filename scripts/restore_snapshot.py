#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.audit.snapshots import list_snapshots, restore_snapshot

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("list")
    r = sub.add_parser("restore")
    r.add_argument("--snapshot", required=True)
    r.add_argument("--target", default="restored_project")
    args = p.parse_args()
    if args.cmd == "restore":
        path = restore_snapshot(args.snapshot, args.target)
        print(f"Restored to: {path}")
    else:
        for row in list_snapshots():
            print(f"{row['snapshot_id']}  {row['size_mb']} MB  {row['path']}")

if __name__ == "__main__":
    main()

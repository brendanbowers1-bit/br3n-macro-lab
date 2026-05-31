#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.audit.snapshots import create_snapshot

def main():
    p = argparse.ArgumentParser(description="Mandatory backup before major changes")
    p.add_argument("--reason", required=True)
    args = p.parse_args()
    path = create_snapshot(reason=args.reason, created_by="pre_change_backup")
    print(f"Pre-change backup: {path}")

if __name__ == "__main__":
    main()

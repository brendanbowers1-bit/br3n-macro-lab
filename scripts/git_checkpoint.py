#!/usr/bin/env python3
import argparse, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.audit.snapshots import create_snapshot
from src.audit.git_utils import git_available

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--message", required=True)
    p.add_argument("--skip-tests", action="store_true")
    args = p.parse_args()

    snap = create_snapshot(reason=args.message, created_by="git_checkpoint")
    print(f"Snapshot: {snap}")

    if not args.skip_tests:
        r = subprocess.run([sys.executable, str(ROOT / "scripts/run_all_quality_checks.py"), "--skip-snapshot"], cwd=ROOT)
        if r.returncode != 0:
            print("WARNING: quality checks failed — commit skipped")
            return 1

    if git_available(ROOT):
        subprocess.run(["git", "add", "-A"], cwd=ROOT)
        msg = f"{args.message} [{snap.name}]"
        cr = subprocess.run(["git", "commit", "-m", msg], cwd=ROOT)
        if cr.returncode != 0:
            print("WARNING: git commit failed or nothing to commit")
    else:
        print("WARNING: git unavailable — snapshot only")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

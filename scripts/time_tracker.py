#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.audit.time_tracking import TimeTracker

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--task", required=True)
    s.add_argument("--notes", default="")
    sub.add_parser("stop")
    sub.add_parser("status")
    sub.add_parser("report")
    args = p.parse_args()
    tt = TimeTracker(ROOT)
    if args.cmd == "start":
        print(tt.start(args.task, args.notes))
    elif args.cmd == "stop":
        print(tt.stop())
    elif args.cmd == "status":
        print(tt.status())
    else:
        print(tt.report())

if __name__ == "__main__":
    main()

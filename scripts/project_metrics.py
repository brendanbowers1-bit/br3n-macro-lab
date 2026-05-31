#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.audit.metrics import count_project_lines, write_metrics_reports

def main():
    m = count_project_lines(ROOT)
    paths = write_metrics_reports(m, ROOT)
    t = m["totals"]
    print(f"Files: {t['files']}  Lines: {t['total_lines']}  Code: {t['code_lines']}  Test ratio: {m['test_to_code_ratio']}")
    for k, v in paths.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()

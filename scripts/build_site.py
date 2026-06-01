#!/usr/bin/env python3
"""Build styled HTML site + regenerate markdown publication."""

import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.publication import build_publication
from src.site_builder import build_site


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Build BR3N Macro Lab publication site")
    p.add_argument("--open", action="store_true", help="Open index.html in default browser")
    args = p.parse_args()

    build_publication()
    paths = build_site()

    # Static Next.js dashboard → reports/publication/dashboard/
    import subprocess

    dash_script = ROOT / "scripts" / "build_web_dashboard_pages.sh"
    if dash_script.exists():
        print("\n==> Building web dashboard for GitHub Pages...")
        subprocess.run(["bash", str(dash_script)], check=False)

    print(f"\n{paths['index'].parent}\n")
    print("Site built:")
    for name, path in paths.items():
        print(f"  {name}: file://{path}")

    print("\nLocal server (share on your network):")
    print("  python scripts/serve_publication.py")

    if args.open:
        webbrowser.open(paths["index"].as_uri())


if __name__ == "__main__":
    main()

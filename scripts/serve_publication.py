#!/usr/bin/env python3
"""Serve publication site on localhost."""

import http.server
import socketserver
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "reports" / "publication"
PORT = 8765


def main() -> None:
    if not (SITE / "index.html").exists():
        print("Run first: python scripts/build_site.py")
        sys.exit(1)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(SITE), **kwargs)

    url = f"http://127.0.0.1:{PORT}/"
    print(f"Serving {SITE}")
    print(f"Open: {url}")
    print("Ctrl+C to stop")

    webbrowser.open(url)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()

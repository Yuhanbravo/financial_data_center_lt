from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fdc.api.app import create_app


def main() -> None:
    app = create_app()
    client = TestClient(app)

    endpoints = [
        ("GET", "/health"),
        ("GET", "/portfolios"),
        ("GET", "/portfolios/PF_DEMO_A"),
        ("GET", "/portfolios/PF_DEMO_A/nav"),
        ("GET", "/portfolios/PF_DEMO_A/analysis"),
        ("GET", "/batches/latest"),
        ("GET", "/portfolios/UNKNOWN"),
    ]

    print("# API Smoke")
    for method, path in endpoints:
        response = client.request(method, path)
        print(f"{method} {path} -> {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    main()

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fdc.db.session import get_session_local, resolve_database_url
from fdc.portfolio.nav_analysis import analyze_nav, build_nav_analysis_report


if __name__ == "__main__":
    db_url = resolve_database_url()
    session_local = get_session_local(db_url)

    with session_local() as session:
        metrics = analyze_nav(session)

    report = build_nav_analysis_report(metrics)

    runtime_report = ROOT / "data" / "artifacts" / "reports" / "sample_nav_analysis_report.md"
    runtime_report.parent.mkdir(parents=True, exist_ok=True)
    runtime_report.write_text(report, encoding="utf-8")

    print(f"Analyzed portfolios: {len(metrics)}")
    print(f"Runtime report generated: {runtime_report}")

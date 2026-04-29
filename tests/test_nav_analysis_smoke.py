from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import func, select

from fdc.db.models import PortfolioMetricDaily
from fdc.db.session import get_session_local


ROOT = Path(__file__).resolve().parents[1]


def test_sample_nav_analysis_script_generates_reports_without_metric_persistence(tmp_path):
    db_file = tmp_path / "phase1a3.sqlite3"
    db_url = f"sqlite:///{db_file}"

    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url

    subprocess.run([sys.executable, "scripts/init_sqlite.py"], check=True, cwd=ROOT, env=env)
    subprocess.run([sys.executable, "scripts/import_sample_nav.py"], check=True, cwd=ROOT, env=env)
    subprocess.run([sys.executable, "scripts/analyze_sample_nav.py"], check=True, cwd=ROOT, env=env)

    runtime_report = ROOT / "data" / "artifacts" / "reports" / "sample_nav_analysis_report.md"
    example_report = ROOT / "docs" / "reports" / "sample_nav_analysis_report.example.md"

    assert runtime_report.is_file()
    assert example_report.is_file()

    content = runtime_report.read_text(encoding="utf-8")
    assert "# Sample NAV Analysis Report" in content
    assert "PF_DEMO_A" in content
    assert "Cumulative return" in content

    session_local = get_session_local(db_url)
    with session_local() as session:
        persisted_metric_count = session.scalar(select(func.count()).select_from(PortfolioMetricDaily))
    assert persisted_metric_count == 0

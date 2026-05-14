from __future__ import annotations

import os
import subprocess
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select

from fdc.db.models import NavDaily, Portfolio, PortfolioMetricDaily
from fdc.db.session import get_session_local

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_REPORT = ROOT / "data" / "artifacts" / "reports" / "sample_portfolio_report.md"


def _run(script: str, env: dict[str, str]) -> None:
    subprocess.run([sys.executable, script], check=True, cwd=ROOT, env=env)


def _report_row_counts(content: str) -> tuple[int, int, int]:
    prefix = "- Rows (total/accepted/rejected): "
    for line in content.splitlines():
        if line.startswith(prefix):
            values = line.removeprefix(prefix).replace("`", "").split(" / ")
            return tuple(int(value) for value in values)
    raise AssertionError("Import Summary row counts line not found")


def test_portfolio_report_generation_uses_sqlite_workflow_and_preserves_example(tmp_path):
    db_file = tmp_path / "phase1a4.sqlite3"
    db_url = f"sqlite:///{db_file}"
    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url

    stable_example = ROOT / "docs" / "reports" / "sample_portfolio_report.example.md"
    before_example = stable_example.read_text(encoding="utf-8") if stable_example.exists() else ""

    _run("scripts/init_sqlite.py", env)
    _run("scripts/import_sample_nav.py", env)
    _run("scripts/analyze_sample_nav.py", env)
    _run("scripts/generate_sample_portfolio_report.py", env)

    assert RUNTIME_REPORT.is_file()
    assert stable_example.is_file()
    assert stable_example.read_text(encoding="utf-8") == before_example

    content = RUNTIME_REPORT.read_text(encoding="utf-8")
    for section in [
        "# Sample Portfolio Report",
        "## Report Overview",
        "## Import Summary",
        "## Issue Summary",
        "## Portfolio Summary",
        "## NAV Analysis Summary",
        "## Monthly Return Table",
        "## Method Notes",
        "## Known Limitations and Next Steps",
    ]:
        assert section in content

    assert "Batch ID:" in content
    assert "Annualized volatility (ddof=1):" in content
    assert "| Month | Return |" in content
    assert _report_row_counts(content) == (4, 4, 0)

    session_local = get_session_local(db_url)
    with session_local() as session:
        persisted_metric_count = session.scalar(select(func.count()).select_from(PortfolioMetricDaily))
    assert persisted_metric_count == 0


def test_import_summary_uses_latest_batch_counts_not_portfolio_observation_count(tmp_path):
    db_file = tmp_path / "phase1a4_batch_counts.sqlite3"
    db_url = f"sqlite:///{db_file}"
    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url

    _run("scripts/init_sqlite.py", env)
    _run("scripts/import_sample_nav.py", env)

    session_local = get_session_local(db_url)
    with session_local() as session:
        portfolio = session.scalar(select(Portfolio).where(Portfolio.portfolio_code == "PF_DEMO_A"))
        assert portfolio is not None
        session.add_all(
            [
                NavDaily(
                    portfolio_id=portfolio.id,
                    nav_date=date(2025, 12, 20) + timedelta(days=index),
                    nav=Decimal("1.00000000") + Decimal(index) / Decimal("10000"),
                )
                for index in range(10)
            ]
        )
        session.commit()

    _run("scripts/import_sample_nav.py", env)
    _run("scripts/analyze_sample_nav.py", env)
    _run("scripts/generate_sample_portfolio_report.py", env)

    content = RUNTIME_REPORT.read_text(encoding="utf-8")
    assert "- Observation count: `12`" in content
    assert _report_row_counts(content) == (4, 4, 0)


def test_no_pandas_numpy_core_dependency_introduced():
    for file_path in [
        ROOT / "src" / "fdc" / "portfolio" / "report.py",
        ROOT / "scripts" / "generate_sample_portfolio_report.py",
    ]:
        content = file_path.read_text(encoding="utf-8").lower()
        assert "import pandas" not in content
        assert "import numpy" not in content

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import func, select, text

from fdc.db.models import PortfolioMetricDaily
from fdc.db.session import get_session_local
from fdc.portfolio.nav_analysis import analyze_nav


ROOT = Path(__file__).resolve().parents[1]


def test_sample_nav_analysis_script_generates_reports_without_metric_persistence(tmp_path):
    db_file = tmp_path / "phase1a3.sqlite3"
    db_url = f"sqlite:///{db_file}"

    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url

    subprocess.run([sys.executable, "scripts/init_sqlite.py"], check=True, cwd=ROOT, env=env)
    subprocess.run([sys.executable, "scripts/import_sample_nav.py"], check=True, cwd=ROOT, env=env)
    before_example = (ROOT / "docs" / "reports" / "sample_nav_analysis_report.example.md").read_text(encoding="utf-8")
    subprocess.run([sys.executable, "scripts/analyze_sample_nav.py"], check=True, cwd=ROOT, env=env)

    runtime_report = ROOT / "data" / "artifacts" / "reports" / "sample_nav_analysis_report.md"
    example_report = ROOT / "docs" / "reports" / "sample_nav_analysis_report.example.md"

    assert runtime_report.is_file()
    assert example_report.read_text(encoding="utf-8") == before_example

    content = runtime_report.read_text(encoding="utf-8")
    assert "PF_DEMO_A" in content
    assert "Max drawdown" in content
    assert "Simple annualized volatility (ddof=1)" in content
    assert "Win rate" in content
    assert "| Month | Return |" in content
    assert "| 2026-01 | n/a |" in content

    session_local = get_session_local(db_url)
    with session_local() as session:
        metrics = {m.portfolio_code: m for m in analyze_nav(session)}
        persisted_metric_count = session.scalar(select(func.count()).select_from(PortfolioMetricDaily))

    a = metrics["PF_DEMO_A"]
    assert float(a.cumulative_return) == pytest.approx(-0.0012967581, abs=1e-10)
    assert float(a.max_drawdown) == pytest.approx(-0.0012967581, abs=1e-10)
    assert float(a.annualized_volatility) == pytest.approx(0.0426185253, rel=1e-6)
    assert float(a.win_rate) == pytest.approx(0.5, abs=1e-12)
    assert a.monthly_returns == [("2026-01", None)]

    assert persisted_metric_count == 0


@pytest.mark.parametrize("invalid_nav", ["0", "-1", "1E9999"])
def test_analyze_nav_rejects_invalid_nav_value(tmp_path, invalid_nav):
    db_file = tmp_path / "invalid.sqlite3"
    db_url = f"sqlite:///{db_file}"
    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url

    subprocess.run([sys.executable, "scripts/init_sqlite.py"], check=True, cwd=ROOT, env=env)
    subprocess.run([sys.executable, "scripts/import_sample_nav.py"], check=True, cwd=ROOT, env=env)

    session_local = get_session_local(db_url)
    with session_local() as session:
        session.execute(text("UPDATE nav_daily SET nav = :nav WHERE portfolio_id = (SELECT id FROM portfolio WHERE portfolio_code = 'PF_DEMO_A')"), {"nav": invalid_nav})
        session.commit()

    with session_local() as session:
        with pytest.raises(ValueError, match="Invalid NAV"):
            analyze_nav(session)

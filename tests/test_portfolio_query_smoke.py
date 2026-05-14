from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import func, select

from fdc.db.models import DataBatch, DataIssueLog, NavDaily, Portfolio, PortfolioMetricDaily
from fdc.db.session import get_session_local
from fdc.portfolio.nav_analysis import analyze_nav
from fdc.portfolio.query import (
    get_latest_batch_summary,
    get_nav_analysis_summary,
    get_nav_series,
    get_portfolio_summary,
    list_portfolios,
)

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_QUERY_REPORT = ROOT / "data" / "artifacts" / "reports" / "sample_query_output.md"


def _run(script: str, env: dict[str, str]) -> None:
    subprocess.run([sys.executable, script], check=True, cwd=ROOT, env=env)


def _counts(session) -> dict[str, int]:
    return {
        "portfolio": session.scalar(select(func.count()).select_from(Portfolio)) or 0,
        "nav_daily": session.scalar(select(func.count()).select_from(NavDaily)) or 0,
        "data_batch": session.scalar(select(func.count()).select_from(DataBatch)) or 0,
        "data_issue_log": session.scalar(select(func.count()).select_from(DataIssueLog)) or 0,
        "portfolio_metric_daily": session.scalar(select(func.count()).select_from(PortfolioMetricDaily)) or 0,
    }


def test_query_layer_smoke_and_readonly_guarantees(tmp_path):
    db_file = tmp_path / "phase1a5a.sqlite3"
    db_url = f"sqlite:///{db_file}"
    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url

    _run("scripts/init_sqlite.py", env)
    _run("scripts/import_sample_nav.py", env)
    _run("scripts/analyze_sample_nav.py", env)
    _run("scripts/generate_sample_portfolio_report.py", env)

    session_local = get_session_local(db_url)
    with session_local() as session:
        before = _counts(session)

        portfolios = list_portfolios(session)
        assert portfolios
        assert [p.portfolio_code for p in portfolios] == sorted(p.portfolio_code for p in portfolios)

        code = portfolios[0].portfolio_code
        summary = get_portfolio_summary(session, code)
        assert summary is not None
        assert summary.portfolio_code == code
        assert summary.nav_obs_count > 0

        nav_series = get_nav_series(session, code)
        assert nav_series
        assert [r.nav_date for r in nav_series] == sorted(r.nav_date for r in nav_series)

        analysis = get_nav_analysis_summary(session, code)
        assert analysis is not None
        analysis_ref = next(item for item in analyze_nav(session) if item.portfolio_code == code)
        assert analysis.cumulative_return == analysis_ref.cumulative_return
        assert analysis.max_drawdown == analysis_ref.max_drawdown
        assert analysis.annualized_volatility == analysis_ref.annualized_volatility

        latest_batch = get_latest_batch_summary(session)
        assert latest_batch is not None
        assert latest_batch.batch_id > 0
        assert latest_batch.issue_breakdown.issue_type_counts == sorted(latest_batch.issue_breakdown.issue_type_counts)
        assert latest_batch.issue_breakdown.severity_counts == sorted(latest_batch.issue_breakdown.severity_counts)

        assert get_portfolio_summary(session, "UNKNOWN") is None
        assert get_nav_analysis_summary(session, "UNKNOWN") is None
        assert get_nav_series(session, "UNKNOWN") == []

        after = _counts(session)
        assert before == after
        assert after["portfolio_metric_daily"] == 0


def test_query_script_no_runtime_artifact_write_and_no_numpy_pandas_dependency(tmp_path):
    db_file = tmp_path / "phase1a5a_script.sqlite3"
    db_url = f"sqlite:///{db_file}"
    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url

    _run("scripts/init_sqlite.py", env)
    _run("scripts/import_sample_nav.py", env)
    _run("scripts/analyze_sample_nav.py", env)
    _run("scripts/generate_sample_portfolio_report.py", env)

    before_exists = RUNTIME_QUERY_REPORT.exists()
    _run("scripts/query_sample_portfolio.py", env)
    after_exists = RUNTIME_QUERY_REPORT.exists()
    assert before_exists == after_exists

    for file_path in [
        ROOT / "src" / "fdc" / "portfolio" / "query.py",
        ROOT / "scripts" / "query_sample_portfolio.py",
    ]:
        content = file_path.read_text(encoding="utf-8").lower()
        assert "import pandas" not in content
        assert "import numpy" not in content

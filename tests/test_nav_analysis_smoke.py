from __future__ import annotations

import os
import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import func, select, text

from fdc.db.models import NavDaily, Portfolio, PortfolioMetricDaily
from fdc.db.session import get_session_local
from fdc.portfolio.nav_analysis import _validate_nav_series, analyze_nav


ROOT = Path(__file__).resolve().parents[1]


def _run_script(script_name: str, env: dict[str, str]) -> None:
    subprocess.run([sys.executable, script_name], check=True, cwd=ROOT, env=env)


def _init_and_import_sample(db_url: str) -> dict[str, str]:
    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url
    _run_script("scripts/init_sqlite.py", env)
    _run_script("scripts/import_sample_nav.py", env)
    return env


def test_sample_nav_analysis_script_generates_runtime_report_without_metric_persistence(tmp_path):
    db_file = tmp_path / "phase1a3.sqlite3"
    db_url = f"sqlite:///{db_file}"

    env = _init_and_import_sample(db_url)
    session_local = get_session_local(db_url)
    with session_local() as session:
        session.execute(
            text(
                "UPDATE nav_daily SET daily_return = :daily_return "
                "WHERE portfolio_id = (SELECT id FROM portfolio WHERE portfolio_code = 'PF_DEMO_A')"
            ),
            {"daily_return": "0.12345678"},
        )
        session.commit()

    before_example = (ROOT / "docs" / "reports" / "sample_nav_analysis_report.example.md").read_text(encoding="utf-8")
    _run_script("scripts/analyze_sample_nav.py", env)

    runtime_report = ROOT / "data" / "artifacts" / "reports" / "sample_nav_analysis_report.md"
    example_report = ROOT / "docs" / "reports" / "sample_nav_analysis_report.example.md"

    assert runtime_report.is_file()
    assert example_report.read_text(encoding="utf-8") == before_example

    content = runtime_report.read_text(encoding="utf-8")
    assert "PF_DEMO_A" in content
    assert "- Date range: `2026-01-02` to `2026-01-03`" in content
    assert "- Latest NAV: `1.00120000`" in content
    assert "- Cumulative return: `-0.1297%`" in content
    assert "- Daily return summary (avg/min/max): `-0.1297%` / `-0.1297%` / `-0.1297%`" in content
    assert "- Max drawdown: `-0.1297%`" in content
    assert "- Annualized volatility (ddof=1): `n/a`" in content
    assert "- Win rate: `0.0000%`" in content
    assert "### PF_DEMO_B" in content
    assert "- Daily return summary (avg/min/max): `n/a` / `n/a` / `n/a`" in content
    assert "| 2026-01 | n/a |" in content

    with session_local() as session:
        metrics = {m.portfolio_code: m for m in analyze_nav(session)}
        persisted_metric_count = session.scalar(select(func.count()).select_from(PortfolioMetricDaily))

    a = metrics["PF_DEMO_A"]
    expected_daily_return = (Decimal("1.00120000") / Decimal("1.00250000")) - Decimal("1")
    assert a.obs_count == 2
    assert a.start_date == "2026-01-02"
    assert a.end_date == "2026-01-03"
    assert float(a.latest_nav) == pytest.approx(1.0012, abs=1e-12)
    assert float(a.cumulative_return) == pytest.approx(float(expected_daily_return), abs=1e-12)
    assert float(a.average_daily_return) == pytest.approx(float(expected_daily_return), abs=1e-12)
    assert float(a.min_daily_return) == pytest.approx(float(expected_daily_return), abs=1e-12)
    assert float(a.max_daily_return) == pytest.approx(float(expected_daily_return), abs=1e-12)
    assert float(a.max_drawdown) == pytest.approx(float(expected_daily_return), abs=1e-12)
    assert a.annualized_volatility is None
    assert float(a.win_rate) == pytest.approx(0.0, abs=1e-12)
    assert a.monthly_returns == [("2026-01", None)]

    b = metrics["PF_DEMO_B"]
    assert b.obs_count == 1
    assert b.start_date == "2026-01-02"
    assert b.end_date == "2026-01-02"
    assert float(b.latest_nav) == pytest.approx(0.998, abs=1e-12)
    assert float(b.cumulative_return) == pytest.approx(0.0, abs=1e-12)
    assert b.average_daily_return is None
    assert b.min_daily_return is None
    assert b.max_daily_return is None
    assert float(b.max_drawdown) == pytest.approx(0.0, abs=1e-12)
    assert b.annualized_volatility is None
    assert b.win_rate is None
    assert b.monthly_returns == [("2026-01", None)]

    c = metrics["PF_DEMO_C"]
    assert c.average_daily_return is None
    assert c.annualized_volatility is None
    assert c.win_rate is None

    assert persisted_metric_count == 0


def test_analyze_nav_builds_monthly_return_table_with_first_month_na(tmp_path):
    db_file = tmp_path / "monthly.sqlite3"
    db_url = f"sqlite:///{db_file}"
    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url

    _run_script("scripts/init_sqlite.py", env)

    session_local = get_session_local(db_url)
    with session_local() as session:
        portfolio = Portfolio(portfolio_code="PF_MONTHLY", portfolio_name="Monthly Demo", base_ccy="CNY")
        session.add(portfolio)
        session.flush()
        session.add_all(
            [
                NavDaily(portfolio_id=portfolio.id, nav_date=date(2026, 1, 31), nav=Decimal("1.00000000"), nav_accum=Decimal("1.00000000")),
                NavDaily(portfolio_id=portfolio.id, nav_date=date(2026, 2, 14), nav=Decimal("1.05000000"), nav_accum=Decimal("1.05000000")),
                NavDaily(portfolio_id=portfolio.id, nav_date=date(2026, 2, 28), nav=Decimal("1.10000000"), nav_accum=Decimal("1.10000000")),
            ]
        )
        session.commit()

    with session_local() as session:
        metrics = {m.portfolio_code: m for m in analyze_nav(session)}

    monthly_returns = metrics["PF_MONTHLY"].monthly_returns
    assert monthly_returns[0] == ("2026-01", None)
    assert monthly_returns[1][0] == "2026-02"
    assert float(monthly_returns[1][1]) == pytest.approx(0.1, abs=1e-12)


@pytest.mark.parametrize("invalid_nav", ["0", "-1"])
def test_analyze_nav_rejects_non_positive_nav_value(tmp_path, invalid_nav):
    db_file = tmp_path / "invalid.sqlite3"
    db_url = f"sqlite:///{db_file}"
    env = _init_and_import_sample(db_url)

    session_local = get_session_local(db_url)
    with session_local() as session:
        session.execute(text("UPDATE nav_daily SET nav = :nav WHERE portfolio_id = (SELECT id FROM portfolio WHERE portfolio_code = 'PF_DEMO_A')"), {"nav": invalid_nav})
        session.commit()

    with session_local() as session:
        with pytest.raises(ValueError, match="Invalid NAV"):
            analyze_nav(session)


@pytest.mark.parametrize("invalid_nav", [Decimal("NaN"), Decimal("Infinity")])
def test_nav_validation_rejects_non_finite_nav_value(invalid_nav):
    with pytest.raises(ValueError, match="Invalid NAV"):
        _validate_nav_series("PF_INVALID", [(date(2026, 1, 2), invalid_nav)])

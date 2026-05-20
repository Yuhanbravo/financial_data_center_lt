from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import func, select

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fdc.api.app import create_app
from fdc.db.models import DataBatch, DataIssueLog, NavDaily, Portfolio, PortfolioMetricDaily
from fdc.db.session import get_session_local

RUNTIME_SMOKE_REPORT = ROOT / "data" / "artifacts" / "reports" / "api_smoke_report.md"


def _run(script: str, env: dict[str, str]) -> None:
    subprocess.run([sys.executable, script], check=True, cwd=ROOT, env=env)


def _setup_sample_db(tmp_path: Path) -> str:
    db_file = tmp_path / "api_smoke.sqlite3"
    db_url = f"sqlite:///{db_file}"
    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url
    _run("scripts/init_sqlite.py", env)
    _run("scripts/import_sample_nav.py", env)
    _run("scripts/analyze_sample_nav.py", env)
    _run("scripts/generate_sample_portfolio_report.py", env)
    return db_url


def _counts(session) -> dict[str, int]:
    return {
        "portfolio": session.scalar(select(func.count()).select_from(Portfolio)) or 0,
        "nav_daily": session.scalar(select(func.count()).select_from(NavDaily)) or 0,
        "data_batch": session.scalar(select(func.count()).select_from(DataBatch)) or 0,
        "data_issue_log": session.scalar(select(func.count()).select_from(DataIssueLog)) or 0,
        "portfolio_metric_daily": session.scalar(select(func.count()).select_from(PortfolioMetricDaily)) or 0,
    }


def test_api_smoke_behaviors_and_readonly(tmp_path, monkeypatch):
    db_url = _setup_sample_db(tmp_path)
    monkeypatch.setenv("FDC_DB_URL", db_url)
    app = create_app()
    client = TestClient(app)

    session_local = get_session_local(db_url)
    with session_local() as session:
        before = _counts(session)

    assert client.get("/health").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}

    resp = client.get("/portfolios")
    assert resp.status_code == 200
    portfolios = resp.json()
    assert portfolios
    assert [p["portfolio_code"] for p in portfolios] == sorted(p["portfolio_code"] for p in portfolios)

    assert client.get("/portfolios/PF_DEMO_A").status_code == 200
    assert client.get("/portfolios/PF_DEMO_A/nav").status_code == 200
    assert client.get("/portfolios/PF_DEMO_A/nav").json()
    assert client.get("/portfolios/PF_DEMO_A/analysis").status_code == 200
    assert client.get("/batches/latest").status_code == 200

    assert client.get("/portfolios/UNKNOWN").status_code == 404
    assert client.get("/portfolios/UNKNOWN/nav").status_code == 404
    assert client.get("/portfolios/UNKNOWN/analysis").status_code == 404

    with session_local() as session:
        after = _counts(session)
    assert before == after
    assert after["portfolio_metric_daily"] == 0


def test_no_batch_and_existing_portfolio_without_nav(tmp_path, monkeypatch):
    db_file = tmp_path / "api_empty.sqlite3"
    db_url = f"sqlite:///{db_file}"
    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url
    _run("scripts/init_sqlite.py", env)

    session_local = get_session_local(db_url)
    with session_local() as session:
        session.execute(Portfolio.__table__.insert().values(portfolio_code="PF_EMPTY", portfolio_name="Empty", base_ccy="USD", is_active=True))
        session.commit()

    monkeypatch.setenv("FDC_DB_URL", db_url)
    client = TestClient(create_app())

    assert client.get("/batches/latest").status_code == 200
    assert client.get("/batches/latest").json() is None

    nav_resp = client.get("/portfolios/PF_EMPTY/nav")
    assert nav_resp.status_code == 200
    assert nav_resp.json() == []

    analysis_resp = client.get("/portfolios/PF_EMPTY/analysis")
    assert analysis_resp.status_code == 200
    assert analysis_resp.json() is None


def test_run_api_smoke_no_runtime_artifact_write(tmp_path, monkeypatch):
    db_url = _setup_sample_db(tmp_path)
    env = os.environ.copy()
    env["FDC_DB_URL"] = db_url

    before_exists = RUNTIME_SMOKE_REPORT.exists()
    subprocess.run([sys.executable, "scripts/run_api_smoke.py"], check=True, cwd=ROOT, env=env)
    after_exists = RUNTIME_SMOKE_REPORT.exists()
    assert before_exists == after_exists


def test_route_delegation_to_query_layer(monkeypatch):
    from fdc.api import routes

    calls = []

    class DummySession:
        pass

    def fake_get_db():
        yield DummySession()

    def fake_list_portfolios(session):
        calls.append(("list_portfolios", isinstance(session, DummySession)))
        from fdc.portfolio.query import PortfolioListItem

        return [PortfolioListItem("PF_X", "X", "USD", None, True)]

    app = create_app()
    app.dependency_overrides[routes.get_db] = fake_get_db
    monkeypatch.setattr(routes.query, "list_portfolios", fake_list_portfolios)
    client = TestClient(app)

    response = client.get("/portfolios")
    assert response.status_code == 200
    assert calls == [("list_portfolios", True)]
    assert response.json()[0]["portfolio_code"] == "PF_X"

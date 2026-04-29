from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select

from fdc.db.init_db import init_db
from fdc.db.models import DataBatch, DataIssueLog, PortfolioMetricDaily
from fdc.db.session import get_session_local
from fdc.portfolio.import_nav import import_nav_csv, seed_portfolios
from fdc.portfolio.nav_analysis import analyze_nav_metrics

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "data" / "sample"


def _session_for_tmp_db(tmp_path):
    db_file = tmp_path / "nav_analysis.sqlite3"
    db_url = f"sqlite:///{db_file}"
    init_db(db_url=db_url)
    return get_session_local(db_url)


def test_nav_analysis_success(tmp_path):
    session_local = _session_for_tmp_db(tmp_path)
    with session_local() as session:
        seed_portfolios(session, SAMPLE_DIR / "portfolio_sample.csv")
        import_nav_csv(session, SAMPLE_DIR / "nav_daily_sample.csv", artifacts_dir=tmp_path / "artifacts")

        result = analyze_nav_metrics(session)

        assert result.status == "success"
        assert result.row_count == 4
        assert session.scalar(select(func.count()).select_from(PortfolioMetricDaily)) == 8

        cum = session.scalar(
            select(PortfolioMetricDaily.metric_value).where(PortfolioMetricDaily.metric_name == "cum_return").limit(1)
        )
        assert isinstance(cum, Decimal)
        assert session.scalar(select(func.count()).select_from(DataBatch).where(DataBatch.dataset_name == "portfolio_metric_daily")) == 1


def test_nav_analysis_no_nav_data(tmp_path):
    session_local = _session_for_tmp_db(tmp_path)
    with session_local() as session:
        result = analyze_nav_metrics(session)
        assert result.status == "failed"
        assert session.scalar(select(func.count()).select_from(DataIssueLog).where(DataIssueLog.issue_type == "no_nav_data")) == 1

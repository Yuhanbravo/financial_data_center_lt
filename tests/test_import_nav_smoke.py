from __future__ import annotations

from pathlib import Path

from sqlalchemy import func, select

from fdc.db.init_db import init_db
from fdc.db.models import DataBatch, DataIssueLog, NavDaily
from fdc.db.session import get_session_local
from fdc.portfolio.import_nav import import_nav_csv, seed_portfolios


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "data" / "sample"


def _session_for_tmp_db(tmp_path):
    db_file = tmp_path / "import_nav.sqlite3"
    db_url = f"sqlite:///{db_file}"
    init_db(db_url=db_url)
    return get_session_local(db_url)


def test_successful_import(tmp_path):
    session_local = _session_for_tmp_db(tmp_path)
    with session_local() as session:
        seed_portfolios(session, SAMPLE_DIR / "portfolio_sample.csv")
        result = import_nav_csv(session, SAMPLE_DIR / "nav_daily_sample.csv", artifacts_dir=tmp_path / "artifacts")

        assert result.status == "success"
        assert result.accepted_rows == 4
        assert result.rejected_rows == 0
        assert session.scalar(select(func.count()).select_from(NavDaily)) == 4
        assert session.scalar(select(func.count()).select_from(DataIssueLog)) == 0


def test_issue_logging_and_partial_batch(tmp_path):
    session_local = _session_for_tmp_db(tmp_path)
    with session_local() as session:
        seed_portfolios(session, SAMPLE_DIR / "portfolio_sample.csv")
        result = import_nav_csv(
            session,
            SAMPLE_DIR / "nav_daily_sample_with_issues.csv",
            artifacts_dir=tmp_path / "artifacts",
        )

        assert result.status == "partial"
        assert result.accepted_rows == 1
        assert result.rejected_rows == 4
        assert result.issue_counts["unknown_portfolio_code"] == 1
        assert result.issue_counts["invalid_trade_date"] == 1
        assert result.issue_counts["non_positive_nav"] == 1
        assert result.issue_counts["duplicate_source_key"] == 1
        assert session.scalar(select(func.count()).select_from(NavDaily)) == 1
        assert session.scalar(select(func.count()).select_from(DataIssueLog)) == 4


def test_foreign_key_safe_behavior_unknown_portfolio(tmp_path):
    session_local = _session_for_tmp_db(tmp_path)
    with session_local() as session:
        seed_portfolios(session, SAMPLE_DIR / "portfolio_sample.csv")
        result = import_nav_csv(
            session,
            SAMPLE_DIR / "nav_daily_sample_with_issues.csv",
            artifacts_dir=tmp_path / "artifacts",
        )

        assert result.status == "partial"
        unknown_issue = session.scalar(
            select(DataIssueLog).where(DataIssueLog.issue_type == "unknown_portfolio_code")
        )
        assert unknown_issue is not None


def test_repeatable_import_updates_existing_unique_key(tmp_path):
    session_local = _session_for_tmp_db(tmp_path)
    with session_local() as session:
        seed_portfolios(session, SAMPLE_DIR / "portfolio_sample.csv")

        first = import_nav_csv(session, SAMPLE_DIR / "nav_daily_sample.csv", artifacts_dir=tmp_path / "artifacts")
        second = import_nav_csv(session, SAMPLE_DIR / "nav_daily_sample.csv", artifacts_dir=tmp_path / "artifacts")

        assert first.status == "success"
        assert second.status == "success"
        assert session.scalar(select(func.count()).select_from(NavDaily)) == 4
        assert session.scalar(select(func.count()).select_from(DataBatch)) == 2


def test_missing_required_columns_marks_batch_failed(tmp_path):
    session_local = _session_for_tmp_db(tmp_path)
    bad_csv = tmp_path / "nav_missing_columns.csv"
    bad_csv.write_text(
        "\n".join(
            [
                "portfolio_code,trade_date,nav_accum,daily_return",
                "PF_ALPHA,2026-01-02,1.001,0.001",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with session_local() as session:
        seed_portfolios(session, SAMPLE_DIR / "portfolio_sample.csv")
        result = import_nav_csv(session, bad_csv, artifacts_dir=tmp_path / "artifacts")

        assert result.status == "failed"
        assert result.accepted_rows == 0
        assert session.scalar(select(func.count()).select_from(NavDaily)) == 0

        issue_count = session.scalar(
            select(func.count())
            .select_from(DataIssueLog)
            .where(DataIssueLog.issue_type == "missing_required_columns")
        )
        assert issue_count == 1

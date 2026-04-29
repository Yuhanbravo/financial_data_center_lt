from __future__ import annotations

import builtins
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import func, select

from fdc.db.init_db import init_db
from fdc.db.models import DataBatch, DataIssueLog, NavDaily
from fdc.db.session import get_session_local
import fdc.portfolio.import_nav as import_nav_module
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
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pandas":
            raise AssertionError("default NAV import path should not import pandas")
        return original_import(name, globals, locals, fromlist, level)

    with session_local() as session:
        seed_portfolios(session, SAMPLE_DIR / "portfolio_sample.csv")
        builtins.__import__ = guarded_import
        try:
            result = import_nav_csv(session, SAMPLE_DIR / "nav_daily_sample.csv", artifacts_dir=tmp_path / "artifacts")
        finally:
            builtins.__import__ = original_import

        assert result.status == "success"
        assert result.accepted_rows == 4
        assert result.rejected_rows == 0
        assert result.staged_file.endswith(".csv")
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
        assert session.scalar(select(DataIssueLog.table_name).limit(1)) == "nav_daily"


def test_nan_numeric_values_are_logged_and_skipped(tmp_path):
    session_local = _session_for_tmp_db(tmp_path)
    nan_csv = tmp_path / "nav_nan_values.csv"
    nan_csv.write_text(
        "\n".join(
            [
                "portfolio_code,trade_date,nav,nav_accum,daily_return",
                "PF_DEMO_A,2026-01-02,1.00000000,,0.00100000",
                "PF_DEMO_A,2026-01-03,NaN,,0.00100000",
                "PF_DEMO_A,2026-01-04,1.02000000,NaN,0.00100000",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with session_local() as session:
        seed_portfolios(session, SAMPLE_DIR / "portfolio_sample.csv")
        result = import_nav_csv(session, nan_csv, artifacts_dir=tmp_path / "artifacts")

        assert result.status == "partial"
        assert result.accepted_rows == 1
        assert result.rejected_rows == 2
        assert result.issue_counts["invalid_nav"] == 1
        assert result.issue_counts["invalid_optional_numeric"] == 1
        assert session.scalar(select(func.count()).select_from(NavDaily)) == 1

        nan_nav_count = session.scalar(
            select(func.count()).select_from(NavDaily).where(NavDaily.nav_date == date(2026, 1, 3))
        )
        assert nan_nav_count == 0

        invalid_nav_issue_count = session.scalar(
            select(func.count()).select_from(DataIssueLog).where(DataIssueLog.issue_type == "invalid_nav")
        )
        assert invalid_nav_issue_count == 1


def test_relative_path_import_uses_stable_default_artifact_root(tmp_path, monkeypatch):
    session_local = _session_for_tmp_db(tmp_path)
    monkeypatch.chdir(ROOT)

    with session_local() as session:
        seed_portfolios(session, Path("data/sample/portfolio_sample.csv"))
        result = import_nav_csv(session, Path("data/sample/nav_daily_sample.csv"))

        assert result.status == "success"
        assert Path(result.staged_file).is_file()
        assert Path(result.staged_file).parent == ROOT / "data" / "artifacts"


def test_unexpected_error_marks_batch_failed(tmp_path, monkeypatch):
    session_local = _session_for_tmp_db(tmp_path)

    def fail_staging(*args, **kwargs):
        raise RuntimeError("forced staging failure")

    monkeypatch.setattr(import_nav_module, "_stage_source_artifact", fail_staging)

    with session_local() as session:
        seed_portfolios(session, SAMPLE_DIR / "portfolio_sample.csv")

        with pytest.raises(RuntimeError, match="forced staging failure"):
            import_nav_csv(session, SAMPLE_DIR / "nav_daily_sample.csv", artifacts_dir=tmp_path / "artifacts")

        batch = session.scalar(select(DataBatch))
        assert batch is not None
        assert batch.status == "failed"
        assert batch.completed_at is not None


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

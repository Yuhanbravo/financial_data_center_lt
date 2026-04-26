from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from fdc.db.init_db import init_db
from fdc.db.session import DEFAULT_DB_PATH, get_engine, resolve_database_url


EXPECTED_TABLES = {
    "portfolio",
    "data_batch",
    "data_issue_log",
    "nav_daily",
    "portfolio_metric_daily",
}


def test_schema_creation_and_constraints(tmp_path):
    db_file = tmp_path / "schema_smoke.sqlite3"
    db_url = f"sqlite:///{db_file}"

    init_db(db_url=db_url)
    engine = get_engine(db_url)
    inspector = inspect(engine)

    assert EXPECTED_TABLES.issubset(set(inspector.get_table_names()))

    portfolio_uniques = {tuple(item["column_names"]): item["name"] for item in inspector.get_unique_constraints("portfolio")}
    assert ("portfolio_code",) in portfolio_uniques

    nav_uniques = {tuple(item["column_names"]): item["name"] for item in inspector.get_unique_constraints("nav_daily")}
    assert ("portfolio_id", "nav_date") in nav_uniques

    metric_uniques = {
        tuple(item["column_names"]): item["name"]
        for item in inspector.get_unique_constraints("portfolio_metric_daily")
    }
    assert ("portfolio_id", "metric_date", "metric_name") in metric_uniques


def test_sqlite_foreign_key_enforcement(tmp_path):
    db_file = tmp_path / "fk_enforcement.sqlite3"
    db_url = f"sqlite:///{db_file}"
    init_db(db_url=db_url)

    engine = get_engine(db_url)

    with engine.begin() as conn:
        with pytest.raises(IntegrityError):
            conn.execute(
                text(
                    """
                    INSERT INTO nav_daily (
                        portfolio_id, nav_date, nav, nav_accum, daily_return, created_at, updated_at
                    )
                    VALUES (999999, '2026-01-01', 1.0, 1.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """
                )
            )


def test_default_sqlite_url_is_repo_root_stable(monkeypatch, tmp_path):
    monkeypatch.delenv("FDC_DB_URL", raising=False)
    monkeypatch.chdir(tmp_path)

    resolved = resolve_database_url()
    expected = f"sqlite:///{DEFAULT_DB_PATH}"

    assert resolved == expected
    assert Path(DEFAULT_DB_PATH).parent.exists()

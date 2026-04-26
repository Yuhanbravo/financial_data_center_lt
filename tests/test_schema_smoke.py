from __future__ import annotations

from sqlalchemy import inspect

from fdc.db.init_db import init_db
from fdc.db.session import get_engine


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

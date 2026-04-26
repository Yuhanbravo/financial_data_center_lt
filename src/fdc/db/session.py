from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = REPO_ROOT / "data" / "fdc.sqlite3"


def resolve_database_url() -> str:
    """Resolve database URL from environment or default SQLite path under repo root."""
    env_url = os.getenv("FDC_DB_URL")
    if env_url:
        return env_url

    db_path = DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"


class Base(DeclarativeBase):
    pass


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    if engine.url.get_backend_name() != "sqlite":
        return

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_engine(db_url: str | None = None):
    url = db_url or resolve_database_url()
    engine = create_engine(url, future=True)
    _enable_sqlite_foreign_keys(engine)
    return engine


def get_session_local(db_url: str | None = None):
    engine = get_engine(db_url=db_url)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

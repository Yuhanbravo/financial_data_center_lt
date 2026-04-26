from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DEFAULT_DB_PATH = Path("data") / "fdc.sqlite3"


def resolve_database_url() -> str:
    """Resolve SQLite database URL from environment or default path."""
    env_url = os.getenv("FDC_DB_URL")
    if env_url:
        return env_url

    db_path = DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"


class Base(DeclarativeBase):
    pass


def get_engine(db_url: str | None = None):
    url = db_url or resolve_database_url()
    return create_engine(url, future=True)


def get_session_local(db_url: str | None = None):
    engine = get_engine(db_url=db_url)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

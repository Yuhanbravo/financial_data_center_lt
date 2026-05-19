from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from fdc.db.session import get_session_local


def get_db() -> Generator[Session, None, None]:
    session_local = get_session_local()
    session = session_local()
    try:
        yield session
    finally:
        session.close()

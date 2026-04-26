from __future__ import annotations

from . import models  # noqa: F401
from .session import Base, get_engine


def init_db(db_url: str | None = None) -> None:
    engine = get_engine(db_url=db_url)
    Base.metadata.create_all(bind=engine)

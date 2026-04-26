from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fdc.db.init_db import init_db
from fdc.db.session import resolve_database_url


if __name__ == "__main__":
    db_url = resolve_database_url()
    init_db(db_url=db_url)
    print(f"SQLite initialized: {db_url}")

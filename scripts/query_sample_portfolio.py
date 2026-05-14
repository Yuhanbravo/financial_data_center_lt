from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fdc.db.session import get_session_local, resolve_database_url
from fdc.portfolio.query import (
    get_latest_batch_summary,
    get_nav_analysis_summary,
    get_nav_series,
    get_portfolio_summary,
    list_portfolios,
)


if __name__ == "__main__":
    db_url = resolve_database_url()
    session_local = get_session_local(db_url)

    with session_local() as session:
        portfolios = list_portfolios(session)
        print("# Query Sample Portfolio")
        print("\n## Portfolio Listing")
        for p in portfolios:
            print(f"- {p.portfolio_code} | {p.portfolio_name} | {p.base_ccy} | active={p.is_active}")

        code = portfolios[0].portfolio_code if portfolios else "PF_DEMO_A"
        summary = get_portfolio_summary(session, code)
        print("\n## Portfolio Summary")
        print(summary)

        nav_series = get_nav_series(session, code)
        print("\n## NAV Time Series")
        for row in nav_series:
            print(f"- {row.nav_date.isoformat()} nav={row.nav:.8f} nav_accum={row.nav_accum} daily_return={row.daily_return}")

        analysis = get_nav_analysis_summary(session, code)
        print("\n## NAV Analysis Summary")
        print(analysis)

        latest_batch = get_latest_batch_summary(session)
        print("\n## Latest Batch Summary")
        print(latest_batch)

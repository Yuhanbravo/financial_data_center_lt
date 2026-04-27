# Phase 1A-2 Task Package: Sample NAV Import Pipeline

## Objective
Build a minimal, repeatable sample NAV ingestion pipeline using synthetic demo data.

## In Scope
- Sample portfolio master + NAV CSV files.
- Reusable import flow with batch tracking.
- Validation and issue logging into `data_issue_log`.
- `nav_daily` insert/update behavior safe for repeat runs.
- Markdown import report generation.
- Smoke tests for success, partial import with issues, FK-safe handling, and repeatability.

## Out of Scope
- Holdings/trades/instruments/market data.
- API/frontend.
- PostgreSQL migration/Alembic.
- Performance analytics and attribution.

## Deliverables
- `src/fdc/portfolio/import_nav.py`
- `src/fdc/portfolio/validation.py`
- `scripts/import_sample_nav.py`
- `tests/test_import_nav_smoke.py`
- sample CSV data in `data/sample/`
- report at `docs/reports/sample_nav_import_report.md`

## Acceptance Criteria
1. `python scripts/init_sqlite.py` succeeds.
2. `python scripts/import_sample_nav.py` seeds portfolio and imports NAV.
3. `pytest` passes schema + import smoke tests.
4. Database contains expected rows in `portfolio`, `data_batch`, `nav_daily`, `data_issue_log`.

# Phase 1A-3 Task Package: NAV Analysis

## Objective
Build a minimal NAV analysis loop on top of `nav_daily` and persist derived daily metrics into `portfolio_metric_daily`.

## In Scope
- NAV analysis batch lifecycle (`data_batch`).
- Derived metrics ingestion (`cum_return`, `drawdown`, `vol_20d`).
- No-data failure logging into `data_issue_log`.
- Repeatable upsert behavior for `portfolio_metric_daily`.
- Smoke tests for success and failure paths.

## Deliverables
- `src/fdc/portfolio/nav_analysis.py`
- `tests/test_nav_analysis_smoke.py`

## Acceptance Criteria
1. NAV exists -> analysis batch status `success`.
2. Metrics are written into `portfolio_metric_daily` with upsert behavior.
3. Missing NAV data -> analysis batch status `failed` + issue log.
4. `pytest` passes schema/import/nav-analysis smoke tests.

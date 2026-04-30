# Phase 1A-3 Task Package: Portfolio NAV Analysis MVP

## Objective
Build a minimal Portfolio NAV Analysis MVP on top of `nav_daily`, producing a runtime Markdown report, a stable example report, and smoke-test coverage without persisting analytics into `portfolio_metric_daily`.

## In Scope
- Read portfolio NAV observations from `nav_daily` only.
- Compute portfolio-level metrics from adjacent NAV observations:
  - date range
  - observation count
  - latest NAV
  - cumulative return
  - daily return summary (avg/min/max)
  - max drawdown
  - annualized volatility using sample standard deviation (`ddof=1`)
  - win rate
  - monthly return table
- First NAV observation does not produce a daily return.
- Single-observation portfolios must surface insufficient-sample fields as `n/a` (or equivalent): daily return summary, annualized volatility, win rate.
- Monthly return table must show the first month as `n/a`, including the single-month case.
- Validate NAV input before analysis: values must be positive and finite; zero, negative, `NaN`, and `Infinity` must fail safely.
- Keep Decimal-based portfolio metrics stable while handling the float/Decimal boundary only where needed for sample standard deviation.
- Generate runtime Markdown output at `data/artifacts/reports/sample_nav_analysis_report.md`.
- Keep a stable example report at `docs/reports/sample_nav_analysis_report.example.md`.
- Add smoke tests and validation commands for both cloud validation and local Windows gate.

## Out of Scope
- Any write path into `portfolio_metric_daily`.
- Benchmark, market data, holdings, trades, instruments, attribution, or risk engine work.
- FastAPI, frontend, PostgreSQL, Alembic, or real-data integration.
- Schema redesign unless a concrete bug is found.

## Deliverables
- `src/fdc/portfolio/nav_analysis.py`
- `scripts/analyze_sample_nav.py`
- `tests/test_nav_analysis_smoke.py`
- `docs/reports/sample_nav_analysis_report.example.md`
- runtime report at `data/artifacts/reports/sample_nav_analysis_report.md`

## Acceptance Criteria
1. `scripts/analyze_sample_nav.py` reads imported sample NAV data and writes only the runtime report to `data/artifacts/reports/sample_nav_analysis_report.md`.
2. `docs/reports/sample_nav_analysis_report.example.md` remains stable and contains no timestamp, absolute path, random ID, or runtime batch/report noise.
3. Daily return series is computed from adjacent NAV values using `current_nav / previous_nav - 1`, and does not use `NavDaily.daily_return` as the metric source.
4. The first NAV observation does not emit a daily return; single-observation portfolios return `n/a` for daily return summary, annualized volatility, and win rate.
5. Invalid NAV values (`0`, negative, `NaN`, `Infinity`) fail safely before misleading metrics are produced.
6. Smoke tests assert core numeric metrics with approximate comparison where appropriate and verify that `portfolio_metric_daily` remains untouched.

## Validation
### Cloud Validation
- `python -m pytest -q`

### Local Windows Gate
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/init_sqlite.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/import_sample_nav.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/analyze_sample_nav.py`
- `D:\miniforge3\envs\data-center-py312\python.exe -m pytest -q`
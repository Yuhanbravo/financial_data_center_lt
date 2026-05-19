# Project Onboarding Summary

Generated: 2026-05-19  
Project: `financial_data_center_lt`

## Quick Read

This repository is a lightweight local-first financial data center MVP focused on the portfolio layer. Current implementation uses Python, SQLAlchemy ORM, and SQLite. The project has completed Phase 1A through Phase 1A-5A, including sample NAV import, NAV analysis, portfolio report generation, and a read-only query layer.

The current-state source of truth is `docs/HANDOFF.md`. Treat this file as the authority for phase status, completed scope, boundaries, validation gate, runtime artifacts, and next recommended work.

## First Reading Path

1. `README.md`
2. `docs/HANDOFF.md`
3. `docs/README.md`
4. `docs/technical/architecture_overview.md`
5. `docs/technical/phase1a_data_flow.md`
6. `docs/technical/local_runbook.md`
7. `docs/technical/file_governance.md`
8. `docs/tasks/phase1a_005a_readonly_query_layer.md`

## What Exists

- Database layer: `src/fdc/db/`
- Portfolio logic: `src/fdc/portfolio/`
- Workflow scripts: `scripts/`
- Smoke tests: `tests/`
- Sample inputs: `data/sample/`
- Stable example reports: `docs/reports/`
- Task packages: `docs/tasks/`
- Technical onboarding: `docs/technical/`

## Current Working Model

```text
sample CSV
  -> SQLite import
  -> NAV analysis
  -> Markdown portfolio report
  -> read-only query layer
  -> future thin FastAPI adapter
```

The read-only query layer is the key bridge to the next planned phase. It should be reused rather than bypassed by any future API adapter.

## Validation

Use the project conda environment, not the base Python:

```powershell
D:\miniforge3\envs\data-center-py312\python.exe -m pytest -q
```

Latest takeover verification: `22 passed in 13.05s`.

The base `python` currently points to `D:\miniforge3\python.exe` and failed to run pytest because `pytest` is not installed there.

## Boundaries To Preserve

- Do not add FastAPI, frontend, holdings, trades, instruments, market data, PostgreSQL, Alembic, or real-data ingestion without a reviewed task package.
- Do not write analysis/query outputs into `portfolio_metric_daily` unless a future task explicitly authorizes it.
- Do not commit runtime outputs from `data/artifacts/`, SQLite files under `data/`, or pytest temp folders.
- Do not treat historical task packages or review artifacts as the current project state when they conflict with `docs/HANDOFF.md`.
- Do not modify `D:\dev\ai-skill-hub` from this project unless explicitly authorized.

## Suggested First Maintainer Actions

1. Read `docs/HANDOFF.md` and `docs/technical/local_runbook.md`.
2. Run the pytest validation command in the documented conda environment.
3. Review `src/fdc/portfolio/query.py` and `scripts/query_sample_portfolio.py`.
4. Draft a bounded Phase 1A-5B task package before implementing any FastAPI adapter.
5. Keep status updates anchored in `docs/HANDOFF.md`.

## Main Risks

- Environment mismatch between base Python and the documented conda environment.
- Accidentally expanding Phase 1A-5B into broad service, frontend, or schema work.
- Confusing ignored runtime artifacts with versioned stable report examples.
- Reading older review artifacts as current truth instead of evidence history.

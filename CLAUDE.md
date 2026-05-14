# CLAUDE.md — Financial Data Center LT

Lightweight portfolio-level financial data center. Python 3 + SQLAlchemy ORM + SQLite.

## Current phase

Phase 1A baseline (Phases 1A-2 through 1A-4 complete, baseline Gate passed).

- **1A-2**: Sample NAV import pipeline
- **1A-3**: Portfolio NAV analysis MVP
- **1A-4**: Portfolio NAV report/display MVP
- **Next**: Phase 1A-5 Read-only Query Interface MVP (unless redirected)

## Before making changes

Read `docs/HANDOFF.md` — single source of truth for current state, completed scope, and boundaries.

Task packages live in `docs/tasks/`. Each is the implementation contract for its phase.

## Local validation

Run these in order to verify the full pipeline:

```
D:\miniforge3\envs\data-center-py312\python.exe scripts/init_sqlite.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/import_sample_nav.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/analyze_sample_nav.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/generate_sample_portfolio_report.py
D:\miniforge3\envs\data-center-py312\python.exe -m pytest -q
```

All five must pass for a Gate check.

## Key paths

| Path | Purpose |
|---|---|
| `src/fdc/db/models.py` | SQLAlchemy ORM models |
| `src/fdc/db/session.py` | DB session factory |
| `src/fdc/portfolio/` | Import, analysis, report, validation logic |
| `scripts/` | Runnable pipeline scripts |
| `tests/` | Pytest smoke tests (`pytest -q`) |
| `data/sample/` | Sample CSVs (checked in) |
| `data/artifacts/` | Runtime output (gitignored) |
| `docs/blueprint/` | Architecture & phase plans |
| `docs/schema/` | Schema dictionary |
| `docs/reports/` | Stable example reports |
| `docs/reviews/` | Review records |
| `docs/tasks/` | Task package history & contracts |

## Hard boundaries

- **No API/frontend** unless a reviewed Phase 1A-5+ task package authorizes it.
- **No holdings, trades, or instruments** unless Phase 1B task package authorizes it.
- **No market data, PostgreSQL, Alembic, real data, or `portfolio_metric_daily` persistence** without a reviewed task package.
- **Do not modify the base conda environment** (`data-center-py312`).
- **Do not commit runtime artifacts** under `data/artifacts/` or `*.sqlite3` files.
- **Do not modify `src/`, `scripts/`, or `tests/`** without an active task package.
- Treat `docs/HANDOFF.md` as the current state source — update it when completing a task package.

## Agent workflow

1. Read `docs/HANDOFF.md` for current state.
2. Read the relevant task package in `docs/tasks/` if implementing.
3. Implement changes under `src/` and `scripts/`.
4. Add/update smoke tests under `tests/`.
5. Run the full validation chain above.
6. Do NOT commit — let the user decide when and what to commit.

# Phase 1A-4 Task Package — Portfolio NAV Report / Display MVP

## 1) task_id
`phase1a_004_portfolio_report`

## 2) title
Phase 1A-4: Portfolio NAV Report / Display MVP

## 3) context
- Phase 1A-2 delivered sample NAV import behavior with `data_batch` and `data_issue_log` coverage.
- Phase 1A-3 delivered Portfolio NAV Analysis MVP with a runtime analysis report and stable example report.
- Phase 1A-4 composes those prior outputs into a single sample portfolio report that is human-readable and reviewable.
- This phase remains documentation/report-generation only within local file artifacts and test validation; no service or persistence expansion is allowed.

## 4) objective
Create a minimal, deterministic reporting MVP that consolidates:
1. import summary,
2. issue summary,
3. portfolio summary,
4. NAV analysis summary,
5. monthly return presentation,

into one generated runtime markdown report and one stable example markdown report, using existing Phase 1A-2 / Phase 1A-3 sample SQLite workflow outputs as report inputs.

## 5) scope
In scope:
- Define a thin reporting composer in `src/fdc/portfolio/report.py` that formats a unified markdown report from structured inputs.
- Add a script entrypoint in `scripts/generate_sample_portfolio_report.py` that generates runtime report output at a fixed artifact path.
- Require the runner path to assemble report inputs from existing repository sample SQLite workflow outputs (Phase 1A-2 import result + Phase 1A-3 NAV analysis result), not primarily from in-memory-only hand-built payloads.
- Add/update a smoke test in `tests/test_portfolio_report_smoke.py` to validate generation success and key section presence.
- Add/update stable sample output in `docs/reports/sample_portfolio_report.example.md`.
- Add handoff note in `docs/HANDOFF.md` summarizing the phase output and how to run validation.
- Deliver this task package file as implementation contract.

## 6) out_of_scope
Explicitly out of scope for Phase 1A-4:
- Any API endpoints, FastAPI integration, frontend UI, templating service, or web rendering.
- Holdings/positions/trades/instruments modeling or calculations.
- Benchmark or external market data integration.
- PostgreSQL/Alembic schema changes or migrations.
- Real data ingestion or external data fetching.
- `portfolio_metric_daily` writes, backfill, persistence, or schema creation.
- New protocol systems, alternate rulebooks, or rewrites of task-package / bounded-execution / execution-report ownership boundaries.

## 7) authorized files
Only the following files may be created/modified:
- `src/fdc/portfolio/report.py`
- `scripts/generate_sample_portfolio_report.py`
- `tests/test_portfolio_report_smoke.py`
- `docs/tasks/phase1a_004_portfolio_report.md`
- `docs/reports/sample_portfolio_report.example.md`
- `docs/HANDOFF.md`

Any change outside this list is non-compliant.

## 8) implementation requirements
- Keep implementation as thin wrappers/composers with backreferences to prior phase outputs where relevant; do not create a second protocol/rule system.
- No `pandas` or `numpy` as core dependencies.
- Use plain Python stdlib-friendly formatting and deterministic ordering for report sections.
- `src/fdc/portfolio/report.py` should provide:
  - A small report-building function (or equivalent) that accepts structured import/issue/portfolio/analysis summary inputs.
  - Deterministic markdown rendering with stable section headings.
  - Test-friendly interface that can be fed controlled structured inputs.
- `scripts/generate_sample_portfolio_report.py` should:
  - Read and assemble report inputs from existing repository SQLite sample workflow artifacts/results (Phase 1A-2 import outputs and Phase 1A-3 analysis outputs).
  - Avoid primarily relying on manual in-memory-only sample payload composition.
  - Generate markdown via `src/fdc/portfolio/report.py`.
  - Write runtime artifact to `data/artifacts/reports/sample_portfolio_report.md`.
- `docs/reports/sample_portfolio_report.example.md` should reflect stable expected output for review/diff purposes and must not be overwritten by normal runtime script execution.
- Keep dependencies unchanged unless strictly required for stdlib-level operation.

## 9) report content requirements
The unified report must include, at minimum, the following sections in this top-level order:
1. `# Sample Portfolio Report`
2. `## Report Overview`
3. `## Import Summary`
4. `## Issue Summary`
5. `## Portfolio Summary`
6. `## NAV Analysis Summary`
7. `## Monthly Return Table`
8. `## Method Notes`
9. `## Known Limitations and Next Steps`

Content expectations:
- Import Summary: batch identifier/date context, row counts/processed counts, and high-level ingestion outcome from Phase 1A-2 sample workflow.
- Issue Summary: total issue count and severity/category breakdown from Phase 1A-2 sample workflow outputs.
- Portfolio Summary: sample portfolio identity and high-level NAV snapshot metrics.
- NAV Analysis Summary must reuse Phase 1A-3 metric definitions and include:
  - cumulative return
  - max drawdown
  - annualized volatility using `ddof=1`
  - win rate
  - monthly return table
- Monthly Return Table section must present the Phase 1A-3 monthly return outputs in report-readable table form.
- Method Notes should briefly explain the data lineage (SQLite sample import + Phase 1A-3 analysis reuse) and deterministic assumptions.
- Known Limitations and Next Steps should explicitly state current MVP boundaries.

## 10) runtime artifact rules
- Runtime artifact path is mandatory and fixed:
  - `data/artifacts/reports/sample_portfolio_report.md`
- Script must ensure parent directory exists.
- Runtime report content should be reproducible from bundled sample inputs/workflow outputs (no network calls, no real data, no randomness unless fixed seed and stable output).
- Stable example remains:
  - `docs/reports/sample_portfolio_report.example.md`
- Normal runtime generation must not rewrite `docs/reports/sample_portfolio_report.example.md`.
- Runtime artifact is for execution evidence; stable example is for repository review baseline.

## 11) validation commands
Run from repository root.

Cloud validation:
- `python scripts/init_sqlite.py`
- `python scripts/import_sample_nav.py`
- `python scripts/analyze_sample_nav.py`
- `python scripts/generate_sample_portfolio_report.py`
- `python -m pytest -q`

Local Windows Gate:
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/init_sqlite.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/import_sample_nav.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/analyze_sample_nav.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/generate_sample_portfolio_report.py`
- `D:\miniforge3\envs\data-center-py312\python.exe -m pytest -q`

## 12) acceptance criteria
All must pass:
1. Runtime report file is generated at `data/artifacts/reports/sample_portfolio_report.md`.
2. Stable example exists at `docs/reports/sample_portfolio_report.example.md` and is not rewritten by normal script execution.
3. Report contains all required sections: report overview, import summary, issue summary, portfolio summary, NAV analysis summary, monthly return table, method notes, known limitations and next steps.
4. NAV Analysis Summary reflects Phase 1A-3 metric definitions: cumulative return, max drawdown, annualized volatility (`ddof=1`), win rate, and monthly return table.
5. Tests confirm no writes to `portfolio_metric_daily`.
6. Tests confirm no introduction of `pandas`/`numpy` as core dependencies.
7. Full `pytest` run passes.
8. No modifications outside authorized file list.
9. No prohibited scope additions (API/frontend/holdings/market data/PostgreSQL/Alembic/real data/`portfolio_metric_daily`).
10. Implementation remains thin and phase-bounded without protocol ownership changes.

## 13) execution report requirements
Execution report must include:
- Summary of files changed (must match authorized list subset).
- Commands executed and pass/fail status for both Cloud validation and Local Windows Gate command sets.
- Confirmation of runtime artifact path and existence.
- Confirmation that stable example path was preserved (not rewritten by normal run).
- Confirmation that required report sections are present.
- Confirmation that tests covered no-write behavior for `portfolio_metric_daily` and no `pandas`/`numpy` core dependency introduction.
- Explicit statement that no out-of-scope systems were introduced.
- Any deviations/known limitations (if none, state “None”).

# Welcome Email Draft

Subject: Welcome to `financial_data_center_lt` maintenance

Hi,

Welcome to `financial_data_center_lt`. This is a lightweight portfolio-layer financial data center MVP. The current stack is Python, SQLAlchemy ORM, and local SQLite. The project has completed the Phase 1A baseline through the read-only query layer.

Your best starting point is `docs/HANDOFF.md`. It is the current-state source of truth. After that, read `docs/README.md` and the technical onboarding files under `docs/technical/`, especially the architecture overview, data flow, local runbook, and file governance notes.

For local validation, use the documented conda environment:

```powershell
D:\miniforge3\envs\data-center-py312\python.exe -m pytest -q
```

In the latest takeover check, this passed with `22 passed in 13.05s`. The default base Python did not have `pytest`, so avoid using base `python` as the validation environment unless you intentionally change the environment setup.

The next recommended product step is Phase 1A-5B: a read-only FastAPI adapter MVP. Please prepare or review a bounded task package before adding API code. The adapter should reuse the existing read-only query layer rather than introducing a parallel query path.

Important boundaries:

- No API/frontend work without the Phase 1A-5B task package.
- No holdings, trades, instruments, market data, PostgreSQL, Alembic, or real-data ingestion without later authorization.
- Do not commit runtime artifacts from `data/artifacts/`, local SQLite files, or pytest temp folders.
- Treat `docs/HANDOFF.md` as authoritative when older task or review records describe earlier project states.

The takeover packet is in `docs/takeover/`:

- `project_takeover_report.md`
- `project_onboarding_summary.md`
- `welcome_email.md`

Recommended first action: read the handoff, run pytest in the project conda environment, then draft the Phase 1A-5B task package with explicit scope for adapter, DTO, and route boundaries.

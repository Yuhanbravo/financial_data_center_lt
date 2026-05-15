# CLAUDE.md — Financial Data Center LT

轻量化组合层金融数据中心。当前技术栈：Python 3 + SQLAlchemy ORM + SQLite。

## 当前阶段（Current Phase）

Phase 1A baseline 已完成到 Phase 1A-5A。

- **1A-2**：Sample NAV import pipeline
- **1A-3**：Portfolio NAV Analysis MVP
- **1A-4**：Portfolio NAV Report / Display MVP
- **1A-5A**：Read-only Query Layer MVP
- **Next**：Phase 1A-5B Read-only FastAPI Adapter MVP

## 修改前先读（Before Making Changes）

先读 `docs/HANDOFF.md`。它是当前状态、已完成范围和边界的 SSOT（Single Source of Truth）。

再读 `docs/README.md` 和 `docs/technical/`，用于了解 documentation navigation、architecture、data flow、local runbook 和 file governance。

Task packages 位于 `docs/tasks/`。每个 task package 是对应 product phase 的 implementation contract。

Review、dogfood 或 governance run 的 support artifacts（例如 task package 和 execution report）位于 `docs/reviews/<review_or_run_id>/`。不要使用 root-level `tasks/` 目录。

## 本地验证（Local Validation）

按顺序运行以下命令验证完整 pipeline：

```
D:\miniforge3\envs\data-center-py312\python.exe scripts/init_sqlite.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/import_sample_nav.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/analyze_sample_nav.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/generate_sample_portfolio_report.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/query_sample_portfolio.py
D:\miniforge3\envs\data-center-py312\python.exe -m pytest -q
```

Gate check 要求以上六个命令全部通过。

## 关键路径（Key Paths）

| Path | Purpose |
|---|---|
| `src/fdc/db/models.py` | SQLAlchemy ORM models |
| `src/fdc/db/session.py` | DB session factory |
| `src/fdc/portfolio/` | import、analysis、report、query、validation logic |
| `scripts/` | 可运行 pipeline scripts |
| `tests/` | Pytest smoke tests (`pytest -q`) |
| `data/sample/` | 已提交的 sample CSVs |
| `data/artifacts/` | runtime output，已 gitignored |
| `docs/blueprint/` | architecture direction 与 phase plans |
| `docs/schema/` | schema dictionary |
| `docs/technical/` | technical onboarding docs |
| `docs/reports/` | stable example reports |
| `docs/reviews/` | review records 与 governance support archives |
| `docs/tasks/` | product phase task package history 与 contracts |

## 硬边界（Hard Boundaries）

- 未经 reviewed Phase 1A-5B+ task package 授权，不新增 API / frontend。
- 未经 Phase 1B task package 授权，不新增 holdings、trades 或 instruments。
- 未经 reviewed task package 授权，不新增 market data、PostgreSQL、Alembic、real data 或 `portfolio_metric_daily` persistence。
- 不修改 base conda environment（`data-center-py312`）。
- 不提交 `data/artifacts/` 或 `*.sqlite3` runtime artifacts。
- 没有 active task package 时，不修改 `src/`、`scripts/` 或 `tests/`。
- 将 `docs/HANDOFF.md` 视为 current state source；完成 task package 后再更新它。

## Agent 工作流（Agent Workflow）

1. 读取 `docs/HANDOFF.md`，确认 current state。
2. 读取 `docs/README.md` 和 `docs/technical/` 下相关文档。
3. 如果要实现功能，读取 `docs/tasks/` 下对应 task package。
4. 只在 authorized scope 内实现。
5. 如果 source behavior 发生变化，运行上面的 full validation chain。
6. 不要主动 commit；由用户决定何时提交、提交哪些内容。

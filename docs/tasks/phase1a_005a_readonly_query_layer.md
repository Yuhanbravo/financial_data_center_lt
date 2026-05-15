# Phase 1A-5A Task Package — Read-only Query Layer MVP

## 1) task_id
`phase1a_005a_readonly_query_layer`

## 2) title
Phase 1A-5A：Read-only Query Layer MVP

## 3) context
- Phase 1A-2 已完成 sample NAV import pipeline。
- Phase 1A-3 已完成 Portfolio NAV Analysis MVP。
- Phase 1A-4 已完成 Portfolio NAV Report / Display MVP。
- 在进入 FastAPI、frontend 或 holdings layer 之前，本阶段先基于当前 SQLite sample workflow 抽象一个可复用的只读查询层（read-only query layer）。
- 该 query layer 后续应可被 API、报告、CLI 或前台查询复用，但本阶段不引入这些外层系统。

## 4) objective
新增一个最小化的只读 portfolio query layer，围绕现有 SQLite sample workflow 提供结构化查询能力：
1. portfolio listing；
2. portfolio summary；
3. NAV time series；
4. NAV analysis summary；
5. latest batch summary。

该阶段只做 read-only abstraction，不扩展 schema，不引入新的业务域。

## 5) scope
In scope：
- 新增 `src/fdc/portfolio/query.py`，作为薄层 read-only query module。
- 新增 `scripts/query_sample_portfolio.py`，作为 sample SQLite workflow 的 CLI-style smoke runner。
- 新增 `tests/test_portfolio_query_smoke.py`，覆盖 query behavior 与 no-write guarantees。
- 更新 `docs/HANDOFF.md`，记录 Phase 1A-5A 状态、验证命令与边界。
- 新增本 task package 文件，作为 implementation contract。
- 可只读复用现有 model/session/analysis/report 代码。

必须实现的 query 能力：
1. `list_portfolios()`
2. `get_portfolio_summary(portfolio_code)`
3. `get_nav_series(portfolio_code)`
4. `get_nav_analysis_summary(portfolio_code)`
5. `get_latest_batch_summary()`

## 6) out_of_scope
Phase 1A-5A 明确不包含：
- FastAPI、frontend、web server、route handler 或 service layer。
- holdings、positions、trades、instruments、lots、transactions 或 accounting logic。
- benchmark、market data、index data 或任何外部数据集成。
- PostgreSQL、Alembic、migration 或 schema expansion。
- real data ingestion 或 external data fetching。
- 任何写入 `portfolio_metric_daily` 的行为。
- schema 修改，除非发现明确 existing schema bug，并在 execution report 中说明。
- 将 `pandas` 或 `numpy` 引入为 core dependency。

## 7) authorized files
只允许创建或修改以下文件：
- `src/fdc/portfolio/query.py`
- `scripts/query_sample_portfolio.py`
- `tests/test_portfolio_query_smoke.py`
- `docs/tasks/phase1a_005a_readonly_query_layer.md`
- `docs/HANDOFF.md`

允许只读复用：
- `src/fdc/portfolio/nav_analysis.py`
- `src/fdc/portfolio/report.py`
- `src/fdc/db/models.py`
- `src/fdc/db/session.py`

除非明确记录为 concrete bug fix，否则任何超出 authorized files 的修改均视为 non-compliant。

## 8) implementation requirements
- Query functions 必须保持 read-only：
  - 不调用 `session.add`
  - 不调用 `session.delete`
  - 不调用 `session.commit`
  - 不写 runtime artifacts
  - 不写 `portfolio_metric_daily`
- Query functions 应接收已有 SQLAlchemy `Session`，不自行管理 database lifecycle。
- Query result 必须是结构化 Python 对象，优先使用 frozen dataclass 或简单 typed container。
- 输出顺序必须 deterministic：
  - portfolios 按 `portfolio_code` 排序；
  - NAV series 按 `nav_date` 排序；
  - issue/batch summary 中的 breakdown 也应稳定排序。
- unknown `portfolio_code` 的行为必须明确并有测试覆盖：
  - summary-style functions 可返回 `None`；
  - NAV series 应返回空列表。
- NAV analysis summary 必须复用 Phase 1A-3 metric definitions，不创建第二套计算语义。
- latest batch summary 应通过稳定规则获取最新 `data_batch`，例如 `created_at desc, id desc`。
- 实现保持 stdlib-friendly、dependency-light。
- 不新增 `pandas` / `numpy` core dependency。

## 9) query content requirements

### `list_portfolios(session)`
返回 portfolio identity records，至少包含：
- `portfolio_code`
- `portfolio_name`
- `base_ccy`
- `inception_date`
- `is_active`

### `get_portfolio_summary(session, portfolio_code)`
返回单个 portfolio summary，至少包含：
- portfolio identity fields
- NAV observation count
- first NAV date
- latest NAV date
- latest NAV
- latest accumulated NAV（如存在）

### `get_nav_series(session, portfolio_code)`
返回按日期升序排列的 NAV observations，至少包含：
- `nav_date`
- `nav`
- `nav_accum`
- `daily_return`

### `get_nav_analysis_summary(session, portfolio_code)`
返回基于 Phase 1A-3 定义的结构化 analysis summary：
- observation count
- start date
- end date
- latest NAV
- cumulative return
- average/min/max daily return（如样本足够）
- max drawdown
- annualized volatility using `ddof=1`
- win rate
- monthly returns

该函数不得将 analysis outputs 写入 `portfolio_metric_daily`。

### `get_latest_batch_summary(session)`
返回 latest batch summary，至少包含：
- batch id/key
- source name
- dataset name
- status
- row count
- window start/end
- created/completed timestamps
- linked issue count
- issue type breakdown
- severity breakdown

## 10) script requirements
`scripts/query_sample_portfolio.py` 应满足：
- 通过现有 session helpers 打开 sample SQLite database。
- 调用全部五个 required query capabilities。
- 将 deterministic、human-readable output 打印到 stdout。
- 不写任何 report file 或 runtime artifact。
- 不修改 database state。
- 应可在以下脚本之后运行：
  - `scripts/init_sqlite.py`
  - `scripts/import_sample_nav.py`
  - `scripts/analyze_sample_nav.py`
  - `scripts/generate_sample_portfolio_report.py`

## 11) validation commands
从 repository root 执行。

Cloud validation：
- `python scripts/init_sqlite.py`
- `python scripts/import_sample_nav.py`
- `python scripts/analyze_sample_nav.py`
- `python scripts/generate_sample_portfolio_report.py`
- `python scripts/query_sample_portfolio.py`
- `python -m pytest -q`

Local Windows Gate：
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/init_sqlite.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/import_sample_nav.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/analyze_sample_nav.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/generate_sample_portfolio_report.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/query_sample_portfolio.py`
- `D:\miniforge3\envs\data-center-py312\python.exe -m pytest -q`

## 12) acceptance criteria
全部必须满足：
1. `src/fdc/portfolio/query.py` 暴露全部五个 required query capabilities。
2. `scripts/query_sample_portfolio.py` 能在 sample SQLite workflow 上成功调用全部五个 query capabilities。
3. Query outputs 是 structured、deterministic，并适合后续 API/report/CLI 复用。
4. `get_nav_analysis_summary()` 复用 Phase 1A-3 metric definitions，且不持久化 metrics。
5. Tests 确认 `portfolio_metric_daily` 保持 untouched。
6. Tests 确认 query calls 不改变核心表 row counts。
7. Tests 覆盖 unknown portfolio behavior。
8. Full `pytest` run 通过。
9. 不引入 schema changes，除非明确 bug 被记录。
10. 不引入 prohibited systems：API/frontend/holdings/market data/PostgreSQL/Alembic/real data。
11. 不引入 `pandas` 或 `numpy` core dependency。
12. 不修改 authorized file list 之外的文件。

## 13) execution report requirements
Execution report 必须包含：
- Files changed summary，且范围必须限制在 authorized files。
- Cloud validation 命令及 pass/fail 状态。
- Local Windows Gate 命令及 pass/fail 状态。
- 确认五个 query capabilities 均已实现。
- 确认 query functions 为 read-only，未调用 commit/write paths。
- 确认 `portfolio_metric_daily` 保持 untouched。
- 确认未引入 schema、FastAPI/frontend、holdings、market data、PostgreSQL/Alembic 或 real-data scope。
- Deviations / known limitations；如无，写 `None`。

## 14) implementation status
- Implemented on branch as bounded execution: query module + runner script + smoke tests + handoff update.
- Status: completed in branch, pending merge.

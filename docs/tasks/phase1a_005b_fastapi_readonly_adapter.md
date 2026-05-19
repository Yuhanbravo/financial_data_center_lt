# Phase 1A-5B Task Package — Read-only FastAPI Adapter MVP

## 1) task_id
`phase1a_005b_fastapi_readonly_adapter`

## 2) title
Phase 1A-5B：Read-only FastAPI Adapter MVP

## 3) context
- Phase 1A-2 已完成 sample NAV import pipeline。
- Phase 1A-3 已完成 Portfolio NAV Analysis MVP。
- Phase 1A-4 已完成 Portfolio NAV Report / Display MVP。
- Phase 1A-5A 已完成 Read-only Query Layer MVP，提供五类只读查询能力：
  - `list_portfolios(session)`
  - `get_portfolio_summary(session, portfolio_code)`
  - `get_nav_series(session, portfolio_code)`
  - `get_nav_analysis_summary(session, portfolio_code)`
  - `get_latest_batch_summary(session)`
- 在进入 frontend、holdings layer 或更复杂 API 能力之前，本阶段先在既有 query layer 之上新增一个最小 FastAPI read-only adapter，使组合层数据中心具备本地只读 API 查询雏形。
- FastAPI 只是 adapter；query layer 才是业务查询边界。API routes 不得重新实现业务逻辑，不得绕过 query layer 写 SQL 复制查询逻辑。

## 4) objective
在 `src/fdc/portfolio/query.py` 之上新增一个最小化 FastAPI read-only adapter，对外暴露只读 HTTP API：

1. `GET /health` — 简单健康检查
2. `GET /portfolios` — 列出所有 portfolios
3. `GET /portfolios/{portfolio_code}` — portfolio summary
4. `GET /portfolios/{portfolio_code}/nav` — NAV time series
5. `GET /portfolios/{portfolio_code}/analysis` — NAV analysis summary
6. `GET /batches/latest` — latest batch summary

每个 endpoint 严格委托给 query layer 的对应函数，不包含任何业务计算、不复制 SQL、不写入数据库。

## 5) scope
In scope：
- 新增 `src/fdc/api/__init__.py`
- 新增 `src/fdc/api/app.py` — FastAPI app factory 与 route include
- 新增 `src/fdc/api/dependencies.py` — FastAPI session dependency / DB lifecycle
- 新增 `src/fdc/api/routes.py` — 六个最小 read-only route handlers
- 新增 `src/fdc/api/schemas.py` — API response DTO / Pydantic models
- 新增 `scripts/run_api_smoke.py` — 基于 TestClient 的 smoke runner
- 新增 `tests/test_api_smoke.py` — API smoke tests
- 新增本 task package 文件 `docs/tasks/phase1a_005b_fastapi_readonly_adapter.md`
- 更新 `docs/HANDOFF.md`，记录 Phase 1A-5B 状态
- 如需声明缺失依赖，授权最小修改：新增 `pyproject.toml`，仅包含 FastAPI adapter / TestClient smoke 所需最小依赖：`fastapi`、`httpx`

## 6) out_of_scope
Phase 1A-5B 明确不包含：
- frontend / web UI / static files / templates
- authentication / authorization / OAuth / JWT / API keys
- deployment / production server / gunicorn / uvicorn 生产配置
- Docker / containerization
- public server / port binding / host exposure
- uvicorn dependency 或任何 server process runner
- async jobs / background tasks / Celery / message queues
- cache / Redis / in-memory caching layer
- complex pagination / sorting / filtering / search
- custom OpenAPI schema design / API versioning
- PostgreSQL / Alembic / database migration
- real data ingestion 或外部数据源接入
- holdings / positions / trades / instruments / lots / transactions
- market data / benchmark / index data
- `portfolio_metric_daily` 写入
- schema changes
- 重写 query layer business logic
- SQL 复制或绕过 query layer 的数据库查询
- 引入 SQLModel、Alembic、auth libraries、frontend framework 或任何无关依赖
- 引入 Docker、deployment、server runtime 或任何生产服务配置

## 7) authorized files
只允许创建或修改以下文件：
- `src/fdc/api/__init__.py`
- `src/fdc/api/app.py`
- `src/fdc/api/dependencies.py`
- `src/fdc/api/routes.py`
- `src/fdc/api/schemas.py`
- `scripts/run_api_smoke.py`
- `tests/test_api_smoke.py`
- `docs/tasks/phase1a_005b_fastapi_readonly_adapter.md`
- `docs/HANDOFF.md`
- `pyproject.toml` — 仅当 `fastapi` / `httpx` 不可 import 且需要声明依赖时授权；只允许加入 `fastapi`、`httpx` 两个最小必要依赖，不得引入无关包

允许只读复用：
- `src/fdc/portfolio/query.py` — 全部五个 query functions
- `src/fdc/portfolio/nav_analysis.py`
- `src/fdc/db/models.py`
- `src/fdc/db/session.py`

任何超出 authorized files 的修改均视为 non-compliant；本阶段不授权 schema fix、query layer fix 或其他旁路 bug fix。

## 8) implementation requirements

### Architecture rule
- FastAPI 只是 adapter layer。
- Route handlers 必须委托给 `src/fdc/portfolio/query.py` 的对应函数，不得重新实现业务计算。
- Route handlers 不得写 SQL、不得调用 `analyze_nav()` 直接、不得用 `select()` 或 `session.execute()` 构造查询。
- Route handlers 不得 inspect ORM objects、不得直接读取 SQLAlchemy model attributes 来绕过 query layer。
- 所有数据库访问通过 query layer 函数完成。
- `/nav` 与 `/analysis` route 可以先调用 `get_portfolio_summary(session, portfolio_code)` 作为 query-layer existence check，以区分 unknown portfolio 与 known portfolio empty data。
- 除上述 query-layer existence check 外，每个 endpoint 只调用完成该 endpoint 所需的最小 query layer 函数。

### Dependency policy
- 本阶段是 TestClient-only MVP：不启动 server、不绑定端口、不运行 uvicorn。
- 本阶段不新增 `uvicorn` 依赖。
- `fastapi` 是 adapter runtime dependency。
- `httpx` 是 FastAPI / Starlette `TestClient` 所需 test/smoke dependency。
- Implementer 必须先检查当前环境中 `fastapi` 与 `httpx` 是否可 import。
- 如果 `fastapi` / `httpx` 缺失且需要声明依赖，允许新增 `pyproject.toml`，但只能包含最小依赖：`fastapi`、`httpx`。
- 不得引入 SQLModel、Alembic、uvicorn、auth libraries、frontend framework、Docker、deployment 或 server runtime 相关依赖。

### Read-only guarantee
- Route handlers 不得调用 `session.add`
- Route handlers 不得调用 `session.delete`
- Route handlers 不得调用 `session.commit`
- Route handlers 不得调用 `session.flush`
- API 全部 GET / HEAD 请求；不接受 POST / PUT / PATCH / DELETE
- API 调用不得改变核心表 row counts
- API 调用不得写入 `portfolio_metric_daily`

### Dependency injection
- 所有 route 通过 FastAPI dependency（`Depends`）获取 SQLAlchemy `Session`
- Session dependency 必须放在 `src/fdc/api/dependencies.py`
- `src/fdc/api/app.py` 只负责 FastAPI app factory、lifespan（如需要）与 include routes
- `src/fdc/api/dependencies.py` 负责 `get_db` / session dependency
- Dependency function 负责创建 session（从 `get_session_local()`）并在请求结束时关闭
- Dependency function 可使用 `yield` 实现 per-request session lifecycle
- Session 参数名为 `session`，类型标注为 `Session`
- 不引入全局 session、thread-local、或 singleton session pattern

### Error handling
- Unknown `portfolio_code` 对 summary / nav / analysis endpoints 返回 `404`
- Portfolio 存在但没有 NAV data 时，nav endpoint 返回 `200` + 空列表 `[]`
- Portfolio 存在但 analysis query 返回 `None` 时，analysis endpoint 返回 `200` + JSON `null`
- 不要把 portfolio 不存在（404）和 NAV 为空（200 + []）混为一谈
- Internal error 应返回 `500` + 通用 error response，不泄漏 traceback

## 9) API endpoint requirements

### `GET /health`
- 返回简单 JSON `{"status": "ok"}`
- 不依赖数据库连接；即使数据库不可用也应返回 ok（或明确降级为 error status）
- 可作为最轻量 smoke check 入口

### `GET /portfolios`
- 调用 `list_portfolios(session)`
- 返回 portfolio identity 列表
- 保持与 query layer 相同的排序（`portfolio_code` 升序）

### `GET /portfolios/{portfolio_code}`
- 调用 `get_portfolio_summary(session, portfolio_code)`
- Portfolio 存在时返回 `200` + portfolio summary
- Portfolio 不存在时返回 `404`

### `GET /portfolios/{portfolio_code}/nav`
- 先调用 `get_portfolio_summary(session, portfolio_code)` 作为 query-layer existence check
- Portfolio 不存在时返回 `404`
- Portfolio 存在时调用 `get_nav_series(session, portfolio_code)`
- Portfolio 存在 + 有 NAV data 时返回 `200` + NAV series
- Portfolio 存在 + 无 NAV data 时返回 `200` + `[]`

### `GET /portfolios/{portfolio_code}/analysis`
- 先调用 `get_portfolio_summary(session, portfolio_code)` 作为 query-layer existence check
- Portfolio 不存在时返回 `404`
- Portfolio 存在时调用 `get_nav_analysis_summary(session, portfolio_code)`
- Portfolio 存在 + 有 analysis 结果时返回 `200` + analysis summary
- Portfolio 存在 + analysis 返回 `None` 时返回 `200` + JSON `null`

### `GET /batches/latest`
- 调用 `get_latest_batch_summary(session)`
- 有 batch 时返回 `200` + batch summary
- 无任何 batch 时返回 `200` + JSON `null`

## 10) response schema / DTO requirements

在 `src/fdc/api/schemas.py` 中定义最小 Pydantic response models。DTO 只负责 API serialization，不改变 query layer result object，不新增业务计算，不持久化指标。

### 建议 schema 清单
- `HealthResponse` — `status: str`
- `PortfolioListItem` — API-facing portfolio identity fields
- `PortfolioSummaryResponse` — portfolio identity + NAV summary fields
- `NavObservationResponse` — single NAV observation fields
- `NavAnalysisResponse` — analysis summary fields
- `BatchIssueBreakdownResponse` — issue type + severity breakdown
- `BatchSummaryResponse` — batch summary fields
- `ErrorResponse` — `detail: str`，用于 404 / 500 响应

### Serialization rules
- 字段命名统一使用 `snake_case`
- `Decimal` 字段必须序列化为 JSON string，避免 JSON number 精度损失
- `date` 字段序列化为 ISO date string `YYYY-MM-DD`
- `datetime` 字段序列化为 ISO datetime string（含时区或 naive）
- 序列化口径必须 stable，不依赖 runtime locale 或环境配置
- 使用 explicit DTO construction；不得依赖 ORM object 自动序列化
- 不使用 ORM `from_attributes`

### DTO 与 query layer 关系
- DTO 字段集可以是 query layer result object 的超集、子集或对等映射
- DTO 不得包含 query layer 不提供的业务计算
- DTO 不得改变 query layer result object
- DTO 构造逻辑应放在 `routes.py` 的 helper function 或 schemas 的 `classmethod` 工厂中，不得嵌入 route handler 主体

## 11) session / DB lifecycle requirements

### Session dependency
- app 通过 FastAPI dependency 为每个 request 提供 SQLAlchemy `Session`
- Session dependency 固定放在 `src/fdc/api/dependencies.py`
- `src/fdc/api/app.py` 负责 app factory、lifespan（如需要）与 include routes
- `src/fdc/api/dependencies.py` 负责 `get_db` / session dependency
- Session 在 request 进入时创建，在 response 返回后关闭

### Lifespan / startup
- FastAPI app 可在 lifespan 中初始化 engine / sessionmaker（来自 `get_session_local()`）
- lifespan 不负责创建数据库表、不运行 migration、不 seed data

### Constraints
- Route handlers 不得 commit session
- Route handlers 不得调用 `session.add` / `session.delete` / `session.flush`
- Session 在 response 后自动 close；不引入 connection pool 复用等超出 MVP 范围的能力
- 不引入 async engine / async session（本阶段保持 sync-only）

## 12) unknown portfolio behavior

| 场景 | Endpoint | 预期行为 |
| --- | --- | --- |
| Portfolio 不存在 | `GET /portfolios/{code}` | `404` |
| Portfolio 不存在 | `GET /portfolios/{code}/nav` | `404` |
| Portfolio 不存在 | `GET /portfolios/{code}/analysis` | `404` |
| Portfolio 存在，无 NAV | `GET /portfolios/{code}` | `200`，`nav_obs_count=0` |
| Portfolio 存在，无 NAV | `GET /portfolios/{code}/nav` | `200`，`[]` |
| Portfolio 存在，analysis 返回 `None` | `GET /portfolios/{code}/analysis` | `200` + JSON `null` |
| 无任何 batch | `GET /batches/latest` | `200` + JSON `null` |

## 13) script runner requirements

`scripts/run_api_smoke.py` 应满足：
- 使用 FastAPI `TestClient` 调用 app，**不启动 uvicorn**，不占用端口
- 调用全部六个最小 endpoints，并打印 deterministic human-readable output 到 stdout
- 包含至少一个 unknown portfolio 请求，验证 404 行为
- 脚本应在以下流程后运行：
  - `scripts/init_sqlite.py`
  - `scripts/import_sample_nav.py`
  - `scripts/analyze_sample_nav.py`
  - `scripts/generate_sample_portfolio_report.py`
  - `scripts/query_sample_portfolio.py`
- `scripts/run_api_smoke.py` 自身不写 runtime artifact、不修改数据库状态
- 前置 `scripts/generate_sample_portfolio_report.py` 允许生成 ignored runtime artifact：`data/artifacts/reports/sample_portfolio_report.md`
- `scripts/run_api_smoke.py` 不创建 report file 或 artifact file
- 打印输出应包含每个 endpoint 的 HTTP status、response body 摘要或关键字段

## 14) test requirements

`tests/test_api_smoke.py` 至少覆盖以下场景：

1. `GET /health` returns `200` and `{"status": "ok"}`
2. `GET /portfolios` returns sample portfolios（非空列表，至少包含已知 sample portfolio codes）
3. `GET /portfolios/PF_DEMO_A` returns portfolio summary（200，含 NAV 字段）
4. `GET /portfolios/PF_DEMO_A/nav` returns NAV series（200，非空列表）
5. `GET /portfolios/PF_DEMO_A/analysis` returns analysis summary（200）
6. `GET /batches/latest` returns latest batch summary（200）
7. `GET /portfolios/UNKNOWN` returns `404`
8. `GET /portfolios/UNKNOWN/nav` returns `404`
9. `GET /portfolios/UNKNOWN/analysis` returns `404`
10. `GET /batches/latest` on an initialized DB with no batch returns `200` + JSON `null`
11. Existing portfolio with no NAV returns `200` + `[]` for `/nav` and `200` + JSON `null` for `/analysis`
12. API calls do not change core table row counts（`portfolio`, `nav_daily`, `data_batch`, `data_issue_log`）
13. API calls do not write `portfolio_metric_daily`
14. `scripts/run_api_smoke.py` does not create runtime artifacts
15. Route behavior reuses query layer rather than duplicating business logic（可通过对 `query.py` 函数 mock/patch/spy 验证 route 委托关系，或通过响应字段与 `scripts/query_sample_portfolio.py` 输出的一致性验证）

### Test infrastructure
- Test database 使用 `tmp_path` 下的独立 SQLite，通过 `FDC_DB_URL` 环境变量注入
- 复用现有 `tests/conftest.py` 的 `src/` path 注入逻辑
- Test 运行前运行 `init_sqlite.py` → `import_sample_nav.py` → `analyze_sample_nav.py` → `generate_sample_portfolio_report.py`
- Edge-case tests may use separate `tmp_path` SQLite DBs initialized only as needed to verify no-batch and existing-portfolio-with-no-NAV behavior
- Test 使用 FastAPI `TestClient` 构建 app 进行 HTTP 级别断言
- 不启动 uvicorn server

## 15) validation commands

从 repository root 执行。

### Cloud validation
- `python scripts/init_sqlite.py`
- `python scripts/import_sample_nav.py`
- `python scripts/analyze_sample_nav.py`
- `python scripts/generate_sample_portfolio_report.py`
- `python scripts/query_sample_portfolio.py`
- `python -m py_compile src/fdc/api/app.py src/fdc/api/routes.py src/fdc/api/schemas.py src/fdc/api/dependencies.py scripts/run_api_smoke.py`
- `python scripts/run_api_smoke.py`
- `python -m pytest -q`
- `git status --short`

### Local Windows Gate
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/init_sqlite.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/import_sample_nav.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/analyze_sample_nav.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/generate_sample_portfolio_report.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/query_sample_portfolio.py`
- `D:\miniforge3\envs\data-center-py312\python.exe -m py_compile src/fdc/api/app.py src/fdc/api/routes.py src/fdc/api/schemas.py src/fdc/api/dependencies.py scripts/run_api_smoke.py`
- `D:\miniforge3\envs\data-center-py312\python.exe scripts/run_api_smoke.py`
- `D:\miniforge3\envs\data-center-py312\python.exe -m pytest -q`
- `git status --short`

## 16) acceptance criteria
全部必须满足：

1. FastAPI app 可被 `TestClient` 加载，six endpoints 全部可用
2. `GET /health` returns `200` + `{"status": "ok"}`
3. `GET /portfolios` returns sample portfolios（非空列表，sorted by portfolio_code）
4. `GET /portfolios/PF_DEMO_A` returns `200` + portfolio summary
5. `GET /portfolios/PF_DEMO_A/nav` returns `200` + NAV series
6. `GET /portfolios/PF_DEMO_A/analysis` returns `200` + analysis summary
7. `GET /batches/latest` returns `200` + batch summary
8. `GET /portfolios/UNKNOWN` returns `404`（所有三个 portfolio-specific endpoints）
9. `GET /batches/latest` 无 batch 时返回 `200` + JSON `null`
10. Portfolio 存在但无 NAV 时，`/nav` 返回 `200` + `[]`，`/analysis` 返回 `200` + JSON `null`
11. API routes 调用 query layer functions，不重新实现业务计算、不写自定义 SQL
12. API calls 不改变核心表 row counts（`portfolio`, `nav_daily`, `data_batch`, `data_issue_log`）
13. API calls 不写入 `portfolio_metric_daily`
14. `scripts/run_api_smoke.py` 不生成 runtime artifacts；前置 `scripts/generate_sample_portfolio_report.py` 生成 ignored runtime artifact 属于预期行为
15. `scripts/run_api_smoke.py` 使用 TestClient，不启动 uvicorn，不占用端口
16. Full `pytest` run 通过
17. 未引入 frontend / auth / deployment / Docker / PostgreSQL / Alembic / real data
18. 未引入 SQLModel、Alembic、uvicorn、auth libraries、frontend framework、server runtime 或其他无关依赖
19. 如果新增 `pyproject.toml`：仅包含 `fastapi`、`httpx` 两个最小必要依赖，无无关包
20. 不修改 authorized file list 之外的文件

## 17) execution report requirements
Execution report 必须包含：
- Files changed summary，且范围必须限制在 authorized files
- Cloud validation 命令及 pass/fail 状态
- Local Windows Gate 命令及 pass/fail 状态
- 确认全部六个 endpoints 已实现并可被 TestClient 调用
- 确认所有 route handlers 委托给 query layer，未复制业务逻辑
- 确认 unknown portfolio → 404 行为已实现并测试通过
- 确认 no-batch → `200` + JSON `null` 已实现并测试通过
- 确认 existing portfolio with no NAV → `/nav` `200` + `[]`、`/analysis` `200` + JSON `null` 已实现并测试通过
- 确认 read-only guarantee（无 commit / add / delete / write paths）
- 确认 `portfolio_metric_daily` 保持 untouched
- 确认未引入 schema changes、frontend、auth、deployment、PostgreSQL、Alembic、Docker 或 real-data scope
- 确认 DTO serialization 口径稳定：snake_case；Decimal as string；date/datetime ISO string；explicit construction；no ORM `from_attributes`
- 确认未引入无关依赖
- 确认 `fastapi` / `httpx` import 检查结果；如新增 `pyproject.toml`，说明原因且确认未引入 `uvicorn`
- Deviations / known limitations；如无，写 `None`

## 18) implementation notes
以下事项已定死，不留给 Implementer 自行决策：
- Session dependency 固定放在 `src/fdc/api/dependencies.py`，且该文件已授权。
- `GET /batches/latest` 无任何 batch 时返回 `200` + JSON `null`。
- `GET /portfolios/{code}/analysis` 在 portfolio 存在但 analysis 返回 `None` 时返回 `200` + JSON `null`。
- DTO 字段命名固定为 `snake_case`。
- 本阶段不引入 `uvicorn`，不启动 server，不占用端口。

唯一 implementation note：
- 如果 `fastapi` / `httpx` 在当前环境不可 import，Implementer 应按 dependency policy 处理，并在 execution report 中说明检查结果、处理方式和是否新增 `pyproject.toml`。

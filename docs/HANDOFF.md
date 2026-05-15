# HANDOFF（SSOT）

## 1. 当前状态
- 日期：2026-05-15
- 目标主线：`main`
- 状态：Phase 1A-5A completed baseline / technical onboarding refresh
- 结论：Phase 1A-2、Phase 1A-3、Phase 1A-4、Phase 1A-5A 均已完成并合入主线；当前下一阶段为 Phase 1A-5B：Read-only FastAPI Adapter MVP。

## 2. 已完成范围
- Phase 1A-2：Sample NAV import pipeline 已完成。
  - 覆盖 sample portfolio / NAV CSV、批次跟踪、基础校验、`data_issue_log`、`nav_daily` repeat-safe import、运行期 import report 与稳定示例报告。
- Phase 1A-3：Portfolio NAV Analysis MVP 已完成。
  - 基于 `nav_daily` 读取样例 NAV，生成组合层 NAV 分析指标、月度收益表、运行期 analysis report 与稳定示例报告。
  - 不写入 `portfolio_metric_daily`。
- Phase 1A-4：Portfolio NAV Report / Display MVP 已完成。
  - 组合 Phase 1A-2 import 输出与 Phase 1A-3 analysis 输出，生成统一的 sample portfolio Markdown report。
  - 运行期报告路径：`data/artifacts/reports/sample_portfolio_report.md`。
  - 稳定示例路径：`docs/reports/sample_portfolio_report.example.md`。
- Phase 1A-5A：Read-only Query Layer MVP 已完成。
  - 新增 `src/fdc/portfolio/query.py`：提供 list/summarize/nav-series/nav-analysis/latest-batch 五类只读结构化查询。
  - 新增 `scripts/query_sample_portfolio.py`：在 sample SQLite workflow 上执行全部查询并输出确定性 stdout。
  - 新增 `tests/test_portfolio_query_smoke.py`：覆盖 unknown 行为、排序确定性、只读保证、row-count 稳定性、`portfolio_metric_daily` untouched、无 pandas/numpy core 依赖。

## 3. Baseline Gate（已通过）
- `scripts/init_sqlite.py` passed
- `scripts/import_sample_nav.py` passed
- `scripts/analyze_sample_nav.py` passed
- `scripts/generate_sample_portfolio_report.py` passed
- `scripts/query_sample_portfolio.py` passed
- `pytest -q` passed

## 4. 运行期产物
以下路径为 ignored runtime artifacts，不作为版本化交付物：
- `data/artifacts/`
- `data/fdc.sqlite3`
- `data/pytest-tmp-safe/`

## 5. Git / 本地说明
- Baseline snapshot：Phase 1A-5A 合入后、本次文档刷新前，`git status --short` 为 clean。
- 非阻塞本地说明：`git status --ignored` 对 `data/mode-test/` 和 `data/test-tmp/` 有 Permission denied warning；这是本地 ACL 临时目录问题，不是代码 Gate blocker。
- 不把本地临时目录清理操作写成项目任务。

## 6. 当前边界
- 不新增 API。
- 不新增持仓层。
- 不新增 market data。
- 不新增 PostgreSQL/Alembic。
- 不修改 `src/`、`scripts/`、`tests/`。
- 不修改 runtime artifacts。

## 7. 文档入口
- 文档导航：`docs/README.md`
- 技术接手层：`docs/technical/`
- 架构说明：`docs/technical/architecture_overview.md`
- Phase 1A 数据流：`docs/technical/phase1a_data_flow.md`
- 本地运行手册：`docs/technical/local_runbook.md`
- 文件治理规则：`docs/technical/file_governance.md`

## 8. 下一步建议
1. Phase 1A-5B：Read-only FastAPI Adapter MVP。
2. API-facing DTO / schema / route boundary 可作为 Phase 1A-5B task package 的子范围处理，不单独拆成 Phase 1A-6。
3. 可选后续：Phase 1B-0 Holdings Layer Blueprint。
4. 可选后续：Phase 1A-3B portfolio_metric_daily sample ingestion。

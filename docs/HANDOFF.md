# HANDOFF（SSOT）

## 1. 当前状态
- 日期：2026-05-14
- 分支：`main`
- 状态：Phase 1A baseline closeout / status refresh
- 结论：Phase 1A-2、Phase 1A-3、Phase 1A-4 均已完成并合入主线；当前主线 baseline Gate 已通过。

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

## 3. Baseline Gate
当前主线 baseline Gate 已通过：
- `scripts/init_sqlite.py` passed
- `scripts/import_sample_nav.py` passed
- `scripts/analyze_sample_nav.py` passed
- `scripts/generate_sample_portfolio_report.py` passed
- `pytest -q` passed: 20 passed in 7.81s

## 4. 运行期产物
以下路径为 ignored runtime artifacts，不作为版本化交付物：
- `data/artifacts/`
- `data/fdc.sqlite3`
- `data/pytest-tmp-safe/`

## 5. Git / 本地说明
- Baseline snapshot：Phase 1A-4 合入后、本次文档刷新前，`git status --short` 为 clean。
- 非阻塞本地说明：`git status --ignored` 对 `data/mode-test/` 和 `data/test-tmp/` 有 Permission denied warning；这是本地 ACL 临时目录问题，不是代码 Gate blocker。
- 不把本地临时目录清理操作写成项目任务。

## 6. 当前边界
- 不新增 API。
- 不新增持仓层。
- 不新增 market data。
- 不新增 PostgreSQL/Alembic。
- 不修改 `src/`、`scripts/`、`tests/`。
- 不修改 runtime artifacts。

## 7. 下一步建议
1. Phase 1A-5：Read-only Query Interface MVP。
2. 可选：Phase 1B-0 Holdings Layer Blueprint。
3. 可选：Phase 1A-3B portfolio_metric_daily sample ingestion。

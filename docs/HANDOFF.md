# HANDOFF（SSOT）

## 1. 当前阶段
- 阶段：Phase 1A-0 / 1A-1（组合层基础建置）
- 日期：2026-04-26
- 状态：已建立最小 repo 骨架、文档蓝图、SQLite + SQLAlchemy 初始化能力

## 2. 已完成内容
1. 项目目录骨架已建立：`src/fdc/`、`src/fdc/db/`、`scripts/`、`tests/`、`data/*`。
2. 规划文档已落盘：README、总体蓝图、Phase 1A 计划、Schema 字典、任务包。
3. SQLAlchemy 模型已覆盖 Phase 1A 核心表：
   - `portfolio`
   - `data_batch`
   - `data_issue_log`
   - `nav_daily`
   - `portfolio_metric_daily`
4. 已提供 SQLite 初始化脚本与 smoke test：
   - `python scripts/init_sqlite.py`
   - `pytest`

## 3. 未完成内容（按阶段边界刻意留空）
- 持仓层（positions）
- 交易层（trades）
- 行情接入（Wind/第三方 API）
- FastAPI 服务层
- 前端查询
- PostgreSQL 迁移脚本与部署流水线
- 复杂指标计算/回测口径

## 4. 明确边界（本阶段不做）
- 不接真实生产数据，不进行外部系统联调。
- 不接 Wind / Oracle / PostgreSQL。
- 不实现 API、前端。
- 不扩展到组合穿透分析、风控引擎、多资产估值。

## 5. 下一步推荐任务（优先级）
1. **Phase 1A-2：数据写入样例与质量日志落盘**
   - 新增最小 ingest demo（CSV -> staged -> SQLite）
   - 为 `data_batch` 与 `data_issue_log` 建立可复用写入方法
2. **Phase 1A-3：日频净值/指标装载流程**
   - 构建 `nav_daily` 与 `portfolio_metric_daily` 的 upsert 策略
3. **Phase 1A-4：迁移预备**
   - 引入 Alembic（仅生成迁移脚手架，不切 PostgreSQL）

## 6. 接手提示
- 先阅读：
  1) `docs/blueprint/IMPLEMENTATION_BLUEPRINT.md`
  2) `docs/blueprint/PHASE1A_PLAN.md`
  3) `docs/schema/phase1a_schema.md`
- 变更模型字段时，同步更新 schema 文档与测试断言，保持“文档与实现一致”。

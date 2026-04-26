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
4. 已提供 SQLite 初始化脚本与 smoke test。

## 3. 校验命令与结果（本次实际执行）
- `python -m py_compile src/fdc/db/models.py`：通过
- `python -m py_compile src/fdc/db/session.py`：通过
- `python -m py_compile src/fdc/db/init_db.py`：通过
- `python -m py_compile scripts/init_sqlite.py`：通过
- `python scripts/init_sqlite.py`：通过（输出 `SQLite initialized: sqlite:///data/fdc.sqlite3`）
- `pytest`：通过（`1 passed`）

## 4. 未完成内容（按阶段边界刻意留空）
- 持仓层（positions）
- 交易层（trades）
- 行情接入（Wind/第三方 API）
- FastAPI 服务层
- 前端查询
- PostgreSQL 迁移脚本与部署流水线
- 复杂指标计算/回测口径

## 5. 明确边界（本阶段不做）
- 不接真实生产数据，不进行外部系统联调。
- 不接 Wind / Oracle / PostgreSQL。
- 不实现 API、前端。
- 不扩展到组合穿透分析、风控引擎、多资产估值。

## 6. 下一步推荐任务（优先级）
1. **Phase 1A-2：样例 NAV 装载 + 校验 + issue log 落盘**
   - 新增最小 ingest demo（CSV -> staged -> SQLite，仅 sample 数据）
   - 为 `data_batch` 与 `data_issue_log` 建立可复用写入方法
2. **Phase 1A-3：组合级指标装载流程**
   - 构建 `portfolio_metric_daily` 装载与校验
   - 形成批次状态闭环（pending/success/failed）
3. **Phase 1B：持仓/交易/标的层扩展**
   - holdings / positions / trades / instruments 分层建模

## 7. 接手提示
- 先阅读：
  1) `docs/blueprint/IMPLEMENTATION_BLUEPRINT.md`
  2) `docs/blueprint/PHASE1A_PLAN.md`
  3) `docs/schema/phase1a_schema.md`
- 变更模型字段时，同步更新 schema 文档与测试断言，保持“文档与实现一致”。

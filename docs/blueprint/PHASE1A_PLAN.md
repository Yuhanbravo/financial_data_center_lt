# PHASE 1A PLAN

## 1. Phase 1A 目标
建立组合层最小可用数据底座，覆盖：
- 组合主数据（portfolio）
- 数据批次治理（data_batch）
- 数据问题日志（data_issue_log）
- 净值日表（nav_daily）
- 组合级指标日表（portfolio_metric_daily）

Baseline status（2026-05-15）：Phase 1A-2 sample NAV import pipeline、Phase 1A-3 Portfolio NAV Analysis MVP、Phase 1A-4 Portfolio NAV Report / Display MVP、Phase 1A-5A Read-only Query Layer MVP 均已完成并合入 `main`。当前状态以 `docs/HANDOFF.md` 为准。

## 2. In Scope
1. repo 目录骨架初始化
2. SQLAlchemy 模型定义（上述 5 张核心表）
3. SQLite 会话与初始化脚本
4. schema smoke tests
5. 文档与任务包落盘
6. Phase 1A-2 / 1A-3 / 1A-4 / 1A-5A 已完成能力记录（样例 NAV 装载、校验、issue log、组合 NAV 分析、组合报告展示、只读查询层）

## 3. Out of Scope
- 持仓层/交易层/标的层建模
- 行情源接入与行情事实表
- 外部系统联调（Wind/Oracle/PostgreSQL）
- API 与前端
- 复杂指标计算逻辑与回测口径

## 4. 核心表（逻辑）
1. `portfolio`：组合主信息
2. `data_batch`：批次级元数据、状态与时间窗
3. `data_issue_log`：数据质量与校验问题
4. `nav_daily`：组合日净值与收益
5. `portfolio_metric_daily`：组合日频指标（可扩展 key-value 结构）

## 5. 任务拆解

### Task A：项目骨架
- 建立 `src/fdc`、`scripts`、`tests`、`data/*`
- 增加包初始化文件

### Task B：数据库基础设施
- `session.py`：engine / SessionLocal / Base
- `models.py`：核心模型 + 约束
- `init_db.py`：建表入口
- `scripts/init_sqlite.py`：命令行触发

### Task C：测试与验证
- `tests/test_schema_smoke.py`
  - 校验表创建
  - 校验关键唯一约束存在

### Task D：文档资产
- 更新 README / HANDOFF
- 完成 Blueprint / Plan / Schema / Task Package

### Task E：Phase 1A 后续路标（文档层）
- Phase 1A-2：样例 NAV 装载 + 基础校验 + issue log 写入（已完成）
- Phase 1A-3：Portfolio NAV Analysis MVP（已完成）
- Phase 1A-4：Portfolio NAV Report / Display MVP（已完成）
- Phase 1A-5A：Read-only Query Layer MVP（已完成）
- Phase 1A-5B：Read-only FastAPI Adapter MVP（推荐下一步）

## 6. 交付物
- 可运行 SQLite 初始化脚本
- 可通过 pytest 的最小测试
- 与实现一致的 schema 文档
- 下一轮可直接执行的任务包

## 7. 验收标准
1. `python scripts/init_sqlite.py` 成功执行并生成 SQLite DB
2. `pytest` 全部通过
3. HANDOFF 可作为下一轮接手入口
4. Blueprint 与 Plan 清晰描述方向与路径
5. Schema 文档与 SQLAlchemy 模型基本一致

## 8. 下一阶段边界
- **Phase 1A 已完成 baseline**：
  - Phase 1A-2：样例 NAV ingest（仅 sample 数据）、数据校验与 issue log 写入
  - Phase 1A-3：组合 NAV 分析 MVP
  - Phase 1A-4：组合 NAV 报告 / 展示 MVP
  - Phase 1A-5A：只读查询层 MVP
- **Phase 1A 推荐下一步**：
  - Phase 1A-5B：Read-only FastAPI Adapter MVP
- **Phase 1B（下一阶段）**：
  - 扩展到 holdings / positions / trades / instruments
  - 不把组合层 ingest 任务挪到 1B

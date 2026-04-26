# Financial Data Center LT

轻量化金融数据中心（组合层）MVP 项目。

## 项目定位
- 目标：先在本地落地组合层数据中心能力，再逐步扩展到 PostgreSQL / FastAPI / 前台查询。
- 当前阶段：**Phase 1A（组合层基础）**。
- 本阶段仅建设组合主数据、批次治理、净值与组合级指标日表，不做持仓、交易、行情接入与 API/前端。

## 技术路线（当前）
- Python 3
- SQLAlchemy ORM
- SQLite（本地单机）

## 快速开始
1. 初始化数据库：
   ```bash
   python scripts/init_sqlite.py
   ```
2. 运行测试：
   ```bash
   pytest
   ```

## 文档入口
- 当前状态与接手说明：`docs/HANDOFF.md`
- 总体蓝图：`docs/blueprint/IMPLEMENTATION_BLUEPRINT.md`
- Phase 1A 实施计划：`docs/blueprint/PHASE1A_PLAN.md`
- Phase 1A Schema 字典：`docs/schema/phase1a_schema.md`
- 本轮任务包：`docs/tasks/phase1a_001_project_skeleton_and_schema.md`

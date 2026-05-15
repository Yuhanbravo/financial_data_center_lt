# Financial Data Center LT

轻量化金融数据中心（组合层）MVP 项目。

## 项目定位
- 目标：先在本地落地组合层数据中心能力，再逐步扩展到 PostgreSQL / FastAPI / 前台查询。
- 当前项目状态、已完成阶段与下一步计划，请以 `docs/HANDOFF.md` 为准。
- 当前仍不做持仓、交易、行情接入、真实数据、PostgreSQL/Alembic 或前端，除非后续 task package 明确授权。

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
- 文档导航与阅读路径：`docs/README.md`
- 技术接手层：`docs/technical/`
- 总体蓝图：`docs/blueprint/IMPLEMENTATION_BLUEPRINT.md`
- Phase 1A 实施计划：`docs/blueprint/PHASE1A_PLAN.md`
- Phase 1A Schema 字典：`docs/schema/phase1a_schema.md`
- Phase task packages：`docs/tasks/`

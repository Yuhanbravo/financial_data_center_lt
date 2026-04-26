# Task Package: phase1a_001_project_skeleton_and_schema

## 1. Scope
- 建立项目最小目录骨架
- 实现 SQLAlchemy + SQLite 初始化能力
- 定义 Phase 1A 核心 schema（5 张表）
- 补齐基础文档（README/HANDOFF/Blueprint/Plan/Schema）
- 增加 smoke test，确保建表可用

## 2. Out of Scope
- 持仓、交易、行情接入
- 外部数据库（PostgreSQL/Oracle）与外部数据源（Wind）
- API、前端、任务调度系统
- 复杂指标计算与性能优化

## 3. Authorized Files
- `README.md`
- `docs/HANDOFF.md`
- `docs/blueprint/IMPLEMENTATION_BLUEPRINT.md`
- `docs/blueprint/PHASE1A_PLAN.md`
- `docs/schema/phase1a_schema.md`
- `docs/tasks/phase1a_001_project_skeleton_and_schema.md`
- `src/fdc/__init__.py`
- `src/fdc/db/__init__.py`
- `src/fdc/db/models.py`
- `src/fdc/db/session.py`
- `src/fdc/db/init_db.py`
- `scripts/init_sqlite.py`
- `tests/test_schema_smoke.py`

## 4. Deliverables
1. 可执行建库脚本：`python scripts/init_sqlite.py`
2. 可通过的测试：`pytest`
3. 文档齐套并与模型一致
4. 提交 execution report

## 5. Validation Commands
```bash
python scripts/init_sqlite.py
pytest
```

## 6. Execution Report Requirements
执行报告必须包含：
1. scope restatement
2. files changed
3. implementation summary
4. validation commands and results
5. out-of-scope items
6. suggested next task

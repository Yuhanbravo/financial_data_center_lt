# 本地运行手册（Local Runbook）

本文档说明 Phase 1A 的本地验证路径。它不引入新功能，也不定义 service process。

## Local Gate

从仓库根目录执行（完整 local gate 要求以上命令全部通过）：

**平台无关命令（macOS / Linux / CI）：**

```bash
python scripts/init_sqlite.py
python scripts/import_sample_nav.py
python scripts/analyze_sample_nav.py
python scripts/generate_sample_portfolio_report.py
python scripts/query_sample_portfolio.py
python -m pytest -q
```

**Windows 示例（使用项目专属 conda 环境）：**

```powershell
D:\miniforge3\envs\data-center-py312\python.exe scripts/init_sqlite.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/import_sample_nav.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/analyze_sample_nav.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/generate_sample_portfolio_report.py
D:\miniforge3\envs\data-center-py312\python.exe scripts/query_sample_portfolio.py
D:\miniforge3\envs\data-center-py312\python.exe -m pytest -q
```

完整 local gate 要求以上命令全部通过。

## 运行期路径（Runtime Paths）

- `data/fdc.sqlite3`：本地 runtime SQLite database。
- `data/artifacts/`：runtime artifacts 与 generated reports。
- `data/artifacts/reports/`：runtime Markdown reports。
- `docs/reports/`：只放 stable example reports。

runtime paths 已被 Git ignore，不应提交。

## 预期 Git 状态（Expected Git State）

正常执行 validation run 后，除 active task 的有意 source / documentation edits 外，`git status --short` 应保持 clean。

只有在需要检查 ignored runtime artifacts 时才使用 `git status --short --ignored`。脚本执行后出现 ignored artifacts 是预期现象。

## 本地 ACL 说明（Local ACL Notes）

部分本地运行可能对 `data/mode-test/` 或 `data/test-tmp/` 显示 Permission denied warning。这属于本地 ACL 临时目录说明，不是 code blocker。除非单独 maintenance task 明确授权，不要把本地清理变成项目任务。

## 范围边界（Scope Boundary）

本 runbook 不授权：
- API 或 frontend work；
- holdings、positions、trades 或 instruments；
- market data integration；
- PostgreSQL 或 Alembic migration；
- real data ingestion；
- schema changes。

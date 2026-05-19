# 架构概览（Architecture Overview）

## 项目定位（Project Positioning）

Financial Data Center LT 是一个轻量化金融数据中心 MVP，聚焦组合层（portfolio-level）数据能力。当前实现采用 local-first 路线：Python 3、SQLAlchemy ORM 和 SQLite。

当前完成状态与下一阶段计划请以 `docs/HANDOFF.md` 为准。本文档只说明相对稳定的技术架构，不作为 parallel status tracker。

## 稳定架构层（Stable Architecture Layers）

- sample NAV import layer：导入 sample portfolio 与 NAV CSV，并写入 SQLite。
- NAV analysis layer：基于 `nav_daily` 计算组合层 NAV 分析指标。
- portfolio report layer：组合 import 与 analysis 输出，生成 deterministic Markdown report。
- read-only query layer：提供 portfolio、NAV、analysis 和 latest batch 的只读结构化查询。
- future API adapter boundary：未来可通过薄 API adapter 暴露 read-only query layer。

## 当前模块关系（Module Relationships）

```text
sample CSV
  -> import_nav.py
  -> SQLite tables
  -> nav_analysis.py
  -> report.py
  -> query.py
  -> future FastAPI adapter
```

## 核心实现面（Core Surfaces）

### 数据库层（Database Layer）

- `src/fdc/db/models.py`：Phase 1A 表结构的 SQLAlchemy ORM models。
- `src/fdc/db/session.py`：database URL 解析、engine 创建和 session factory helper。
- `src/fdc/db/init_db.py`：建表初始化逻辑。
- `scripts/init_sqlite.py`：可运行的 SQLite 初始化入口。

### 组合导入（Portfolio Import）

- `src/fdc/portfolio/import_nav.py`：sample portfolio 与 NAV 导入流程。
- `src/fdc/portfolio/validation.py`：导入流程使用的数据校验 helper。
- `scripts/import_sample_nav.py`：sample import runner。

### NAV 分析（NAV Analysis）

- `src/fdc/portfolio/nav_analysis.py`：基于 `nav_daily` 的组合层 NAV 分析。
- `scripts/analyze_sample_nav.py`：sample analysis runner。

### 组合报告（Portfolio Report）

- `src/fdc/portfolio/report.py`：确定性的 Markdown report composer。
- `scripts/generate_sample_portfolio_report.py`：sample portfolio report runner。

### 只读查询层（Read-only Query Layer）

- `src/fdc/portfolio/query.py`：只读结构化查询函数，覆盖 portfolio listing、portfolio summary、NAV series、NAV analysis summary 和 latest batch summary。
- `scripts/query_sample_portfolio.py`：CLI-style smoke runner，用于查看 query layer 输出。

### 未来 FastAPI Adapter

未来 FastAPI adapter 应复用现有 read-only query layer，并保持薄适配边界。具体 phase、DTO、schema 和 route boundary 范围以对应 task package 与 `docs/HANDOFF.md` 为准。

## 明确不是（Explicit Non-goals）

当前项目不是：

- production data platform；
- market data platform；
- holdings / positions / trades / instruments system；
- API service；
- PostgreSQL / Alembic migration project；
- real-data ingestion system。

除非后续 reviewed task package 明确授权，否则这些边界应继续保持。

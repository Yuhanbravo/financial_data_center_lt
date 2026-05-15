# 文档索引（Documentation Index）

本目录是 `financial_data_center_lt` 的工程文档层（engineering documentation layer）。

## 项目状态入口（Current State Entry）

Financial Data Center LT 是一个轻量化组合层金融数据中心 MVP，当前技术路线是 Python、SQLAlchemy ORM 和本地 SQLite。

当前项目状态、已完成阶段与下一步计划请以 `docs/HANDOFF.md` 为准。`docs/HANDOFF.md` 仍是 current project state 的 SSOT（Single Source of Truth）。本文档只做导航，不是第二份状态事实源。

## 推荐阅读顺序（Reading Path）

1. [仓库 README](../README.md)
2. [当前 handoff / SSOT](HANDOFF.md)
3. 文档索引（本页）
4. [架构概览](technical/architecture_overview.md)
5. [Phase 1A 数据流](technical/phase1a_data_flow.md)
6. [本地运行手册](technical/local_runbook.md)
7. [文件治理规则](technical/file_governance.md)
8. [tasks/](tasks/) 下最新 phase task package

## 文档角色（Document Roles）

### `docs/HANDOFF.md`

当前项目状态 SSOT。负责记录 active baseline、已完成阶段、当前边界、validation gate、runtime artifact 说明和下一阶段建议。

### `docs/technical/`

技术接手层（technical onboarding layer）。面向后续开发者和 agent，说明当前架构、Phase 1A 数据流、本地验证命令和文件治理规则。它仍属于 `docs/` 工程事实层。

### `docs/tasks/`

任务包与实现契约（task packages / implementation contracts）。这些文件是按 phase 留存的历史合同，不应被改写成当前技术手册。

### `docs/reports/`

稳定示例报告（stable example reports）与 review baseline。runtime report 不应写入这里。

### `docs/blueprint/`

架构方向与阶段规划（blueprint / phase planning）。Blueprint 用来支撑路线判断，但当前状态仍以 `docs/HANDOFF.md` 为准。

### `docs/schema/`

Phase 1A SQLite model 的 schema 字典。

### `docs/reviews/`

历史 review、dogfood 和 governance support records。这些文件是证据资料，不是当前执行入口。

## 可读层边界（Readability Boundary）

本轮不创建 `docs_readable/`。当前需求是 technical onboarding，不是业务可读版或管理层可读版；因此使用 `docs/technical/` 更合适。

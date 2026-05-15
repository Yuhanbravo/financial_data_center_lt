# 文件治理（File Governance）

本文档定义当前 Phase 1A baseline 下的文档与产物边界。

## 事实源地图（Source-of-truth Map）

### `docs/HANDOFF.md`

当前项目状态 SSOT。负责 active phase status、completed scope、current boundaries、validation gate、runtime artifact notes 和 next recommended phase。

### `README.md`

仓库入口和高层导航。它应指向 `docs/HANDOFF.md`、`docs/README.md` 和 `docs/technical/`，但不应变成完整技术手册。

### `docs/README.md`

文档索引和 reading path。它是导航层，不是第二份 project status source。

### `CLAUDE.md`

Claude Code thin wrapper。它负责告诉 Claude Code 应该读哪里、如何遵守项目边界；它不是第二事实源，也不是第二套 rulebook。

### `docs/technical/`

技术接手层（technical onboarding layer）。它说明 architecture、data flow、local run commands 和 file governance，同时仍留在 `docs/` 工程事实层内部。

### `docs/tasks/`

任务包和实现契约（task packages / implementation contracts）。这些文件记录 scoped task intent 与 acceptance criteria。不要把它们改写成当前技术文档。

### `docs/reports/`

稳定示例报告（stable example reports）和 review baseline。这里只有 stable example reports。

### `docs/blueprint/`

阶段规划与架构方向（phase planning / architecture direction）。Blueprint 支撑 roadmap 判断，但不替代 `docs/HANDOFF.md` 的 current state SSOT 角色。

### `docs/reviews/`

历史 review、dogfood 和 governance support records。这些是 evidence records，不是当前执行入口。

### `data/artifacts/`

运行期产物（runtime artifacts）。该路径被 ignore，不能提交。

## Runtime Artifact Rules

- 不要把 runtime reports 放进 `docs/reports/`。
- 不要提交 SQLite databases。
- 不要提交 `data/artifacts/`。
- 不要提交 pytest runtime temp folders。
- generated reports 应留在 `data/artifacts/reports/`。

## 文档边界规则（Documentation Boundary Rules）

- 只保留一个 current state SSOT：`docs/HANDOFF.md`。
- task package history 留在 `docs/tasks/`。
- execution reports 和 review evidence 留在 `docs/reviews/`。
- stable example reports 留在 `docs/reports/`。
- technical onboarding 留在 `docs/technical/`。
- 不要把 task package 内容或 execution report 内容混入当前 technical docs。
- 本轮 technical onboarding 不创建 `docs_readable/`。

## 当前下一阶段（Current Next Phase）

下一阶段是 Phase 1A-5B：Read-only FastAPI Adapter MVP。该 adapter 应复用现有 read-only query layer，并由 reviewed task package 约束范围。

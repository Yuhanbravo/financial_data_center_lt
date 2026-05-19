# AGENTS.md — financial_data_center_lt Runtime Entrypoint

## Purpose
This file is the project-side runtime master entrypoint for AI agents working in `financial_data_center_lt`.

It is intentionally thin and dispatch-oriented: use it to locate authoritative project documents, not as a second mutable rulebook.

## Project Identity
- Project: `financial_data_center_lt`
- Scope: lightweight portfolio-level financial data center MVP
- Current baseline: Phase 1A-5A completed
- Next recommended phase: Phase 1A-5B Read-only FastAPI Adapter MVP

## Required Reading Before Changes
1. `docs/HANDOFF.md`
2. `docs/README.md`
3. `SKILL_HUB_SOURCE.md`
4. Relevant task package under `docs/tasks/` for the target phase/scope

## SSOT and Source Policy
- `docs/HANDOFF.md` is the current project state SSOT.
- `SKILL_HUB_SOURCE.md` defines external `ai-skill-hub` source policy and precedence.
- `docs/README.md` is documentation navigation, not a second state source.

## Task Package Workflow (`docs/tasks/`)
- Treat task packages as implementation contracts for phase-scoped work.
- Before implementing behavior changes, identify and read the corresponding task package.
- Execute only within authorized scope and boundaries defined by the active package and project governance docs.

## Runtime Artifact Policy
- Runtime outputs (for example generated reports, local databases, temporary artifacts) are runtime evidence, not versioned product source by default.
- Follow ignore/governance rules documented in project technical docs and HANDOFF.

## Local Validation Chain
When source behavior changes are in scope, run the project validation chain documented in the current runbook/HANDOFF and verify required gates pass before handoff.

## Agent Workflow
1. Read required docs in order.
2. Confirm active baseline and boundaries from `docs/HANDOFF.md`.
3. Locate and apply the relevant `docs/tasks/` contract.
4. Implement only authorized changes.
5. Run required local validation for the touched scope.
6. Produce a clear execution report and handoff notes.

## Conflict Resolution Priority
1. Direct user/developer/system instructions for the current task
2. `docs/HANDOFF.md` (project state SSOT)
3. Active task package under `docs/tasks/`
4. `SKILL_HUB_SOURCE.md` (external skill source policy)
5. `docs/README.md` and `docs/technical/*` (navigation/onboarding/supporting guidance)

If conflicts remain unresolved, stop and request clarification instead of silently reconciling.

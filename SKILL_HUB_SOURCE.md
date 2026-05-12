# Skill Hub Source Policy

Status: Active project-side source policy
Mode: External reference mode
Target project: financial_data_center_lt
Canonical skill source: D:\dev\ai-skill-hub

## Purpose

This file defines how `financial_data_center_lt` references `ai-skill-hub` during local AI-assisted work.

Its purpose is to keep canonical skill guidance separate from project-local facts. `D:\dev\ai-skill-hub` provides reusable skill behavior and workflow guidance. `financial_data_center_lt` provides this project's implementation facts, project phase, data boundaries, reports, handoff notes, and task history.

## Source Precedence

1. Project facts are defined by `financial_data_center_lt`.
2. Canonical skill guidance is defined by `D:\dev\ai-skill-hub`.
3. This project uses `ai-skill-hub` as external reference, not embedded copy.
4. Project-local HANDOFF / status / tasks / reports describe this project only.
5. If a copied or embedded skill-hub snapshot appears in this project later, treat it as non-canonical runtime copy.
6. If embedded snapshot conflicts with `D:\dev\ai-skill-hub`, canonical skill source wins for skill guidance; project facts still come from the target project.
7. Report drift; do not silently reconcile or auto-fix.

## Usage Rules for AI Agents

- Do not modify `ai-skill-hub` from this project task unless explicitly authorized.
- Do not copy full skill definitions into this project.
- Do not create a second rulebook.
- Use `D:\dev\ai-skill-hub` for canonical skill behavior.
- Use `financial_data_center_lt` files for project state, phase, data, reports, and implementation facts.
- Generalized workflow or skill improvements should be proposed back to `ai-skill-hub`.
- Project-specific decisions should remain in this project.

## Allowed Project-Side Artifacts

The following artifacts may exist in this project as project-side evidence or coordination surfaces:

- task packages
- execution reports
- project review memos
- project HANDOFF/status files
- lightweight source policy files

These artifacts are project-side records. They are not the canonical skill source.

## Boundary

This file is a thin project-side policy.

- It does not replace `workflow-bootstrap`.
- It does not replace `project-takeover`.
- It does not replace `chatgpt-handoff-pilot`.
- It does not define task package / bounded execution / execution report protocol.
- It does not authorize validators, automation, CI, source changes, or canonical skill edits.

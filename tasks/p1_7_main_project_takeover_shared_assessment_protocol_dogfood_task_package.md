# P1.7 Main-branch Project Takeover Dogfood with SKILL_HUB_SOURCE Policy

## 1. Background

This task package defines a main-branch read-only `project-takeover` dogfood for `financial_data_center_lt`.

The target project is `D:\dev\financial_data_center_lt`, and the target branch must be `main`. The canonical skill source is the sibling workspace repo `D:\dev\ai-skill-hub`.

This run validates whether `project-takeover` can accurately assess the current target project state while honoring `SKILL_HUB_SOURCE.md` as the project-side source policy. The skill hub is used in external reference mode only: do not copy `ai-skill-hub` into the target project, do not modify `ai-skill-hub`, and do not create a second rulebook inside the target project.

`workflow-bootstrap` owns the role shell, `chatgpt-handoff-pilot` owns the task package / bounded execution / execution report protocol, and `project-takeover` is used only as the read-only assessment skill. The `shared assessment output protocol` is tested as an assessment vocabulary, not modified or promoted into an execution controller.

## 2. Goal

Run a read-only project-level takeover assessment on the latest local `main` state of `financial_data_center_lt` and produce auditable evidence that:

- `project-takeover` can match current project facts on `main`.
- `shared assessment output protocol` fields support project-level takeover output.
- `SKILL_HUB_SOURCE.md` is recognized as project-side source policy.
- SSOT / source precedence remains clear between target project facts and canonical skill guidance.
- `evidence`, `inference`, and `pending` remain separated.
- `risk_priority` is not misused as a phase gate or freshness label.
- `maturity_score` is used only when applicable.
- `next_action` is concrete and executable.
- external skill-hub reference mode avoids SSOT conflict.
- the Drafter -> Reviewer -> Implementer -> Reporter -> Final Reviewer chain can close cleanly.

## 3. In Scope

- Read the target project state under `D:\dev\financial_data_center_lt`.
- Confirm the target branch is `main`.
- Read canonical skill guidance from `D:\dev\ai-skill-hub`.
- Inspect `SKILL_HUB_SOURCE.md` as a project-side source policy, if present.
- Assess README, config, docs, reports, tasks, source, tests, scripts, and data boundary signals in read-only mode.
- Create only the authorized output artifacts:
  - `tasks/p1_7_main_project_takeover_shared_assessment_protocol_dogfood_task_package.md`
  - `docs/reviews/main_project_takeover_shared_assessment_protocol_dogfood_review.md`
  - `tasks/p1_7_main_project_takeover_shared_assessment_protocol_dogfood_execution_report.md`
- Use `shared assessment output protocol` fields in the review memo:
  - `capability_fit`
  - `maturity_score`, only when applicable
  - `evidence`
  - `inference`
  - `open_questions`
  - `risk_priority`
  - `impact_scope`
  - `next_action`
- Record validation commands and results.

## 4. Out of Scope

- Do not modify `D:\dev\ai-skill-hub`.
- Do not modify `SKILL_HUB_SOURCE.md`.
- Do not modify target project source, tests, scripts, data, config, README, `docs/HANDOFF.md`, or `docs/status/`.
- Do not modify existing files under `docs/reviews/` or existing files under `tasks/` other than the authorized artifacts for this run.
- Do not create `AGENTS.md`.
- Do not copy any skill-hub `SKILL.md` body into the target project.
- Do not introduce validator, automation, CI, router-pipeline integration, or runtime pack files.
- Do not run destructive cleanup.
- Do not perform auto-fix or auto-remediation.
- Do not perform broad mandatory maturity scoring.
- Do not execute commit, push, pull, fetch, merge, or rebase.
- Do not rewrite task-package / bounded-execution / execution-report protocols.

## 5. Target files/areas

Read-only target project areas:

- `SKILL_HUB_SOURCE.md`
- `README.md`
- `pyproject.toml`, if present
- `pytest.ini`, if present
- `.gitignore`, if present
- `docs/HANDOFF.md`, if present
- `docs/status/*.md`, if present
- `docs/tasks/*.md`, if present
- `docs/reports/*.md`, if present
- `tasks/*.md`, if present
- `src/`
- `tests/`
- `scripts/`
- `data/`

Read-only canonical skill source files:

- `D:\dev\ai-skill-hub\skills\workflow-bootstrap\orchestration_snippets.md`
- `D:\dev\ai-skill-hub\skills\workflow-bootstrap\examples\invocation_examples.md`
- `D:\dev\ai-skill-hub\skills\_protocol\skill_assessment_output.md`
- `D:\dev\ai-skill-hub\skills\project-takeover\SKILL.md`
- `D:\dev\ai-skill-hub\skills\chatgpt-handoff-pilot\SKILL.md`
- `D:\dev\ai-skill-hub\skills\workflow-bootstrap\SKILL.md`

Allowed write targets:

- `tasks/p1_7_main_project_takeover_shared_assessment_protocol_dogfood_task_package.md`
- `docs/reviews/main_project_takeover_shared_assessment_protocol_dogfood_review.md`
- `tasks/p1_7_main_project_takeover_shared_assessment_protocol_dogfood_execution_report.md`

## 6. Acceptance checks

- Hard gate confirms target branch is `main`.
- Initial target project `git status --short` is clean, or only contains the three authorized artifacts from this run.
- Canonical skill source is inspected read-only, and any existing uncommitted status is reported without modification.
- `SKILL_HUB_SOURCE.md` is inspected and not modified. If missing, the review memo records missing source policy as `pending` / P1 finding.
- Review memo includes at least five findings using the required shared assessment fields.
- Findings classify `evidence` into `confirmed`, `inferred`, and `pending`.
- Review memo explicitly evaluates `risk_priority`, `maturity_score`, `next_action`, SSOT/source precedence, external reference mode, and deferred validator / CI / automation.
- Execution report separates changed, unchanged, and deferred items.
- Final Reviewer returns `Go`, `Go with Conditions`, or `No-Go`.
- Only authorized files are created or changed.

Validation commands to record from target project:

```powershell
git branch --show-current
git diff -- docs/reviews tasks
git diff --name-only
git status --short
rg "capability_fit|maturity_score|risk_priority|impact_scope|open_questions|next_action" docs/reviews/main_project_takeover_shared_assessment_protocol_dogfood_review.md
rg "confirmed|inferred|pending" docs/reviews/main_project_takeover_shared_assessment_protocol_dogfood_review.md
rg "SKILL_HUB_SOURCE|external reference|canonical skill source|SSOT|second rulebook|Report drift|non-canonical runtime copy" docs/reviews/main_project_takeover_shared_assessment_protocol_dogfood_review.md
rg "financial_data_center_lt|project-takeover|ai-skill-hub|validator|CI|automation" docs/reviews/main_project_takeover_shared_assessment_protocol_dogfood_review.md
$changed = git diff --name-only
$restricted = $changed | Select-String -Pattern "^(src/|tests/|scripts/|data/|\.github/|\.vscode/|docs/HANDOFF.md|docs/status/|README.md|pyproject.toml|pytest.ini|\.gitignore|SKILL_HUB_SOURCE.md)"
if ($restricted) { $restricted } else { "No restricted target paths changed." }
```

Validation command to record from canonical skill source:

```powershell
git status --short
```

## 7. Constraints

- Target project files define target project facts.
- `D:\dev\ai-skill-hub` defines canonical skill guidance.
- `SKILL_HUB_SOURCE.md` defines project-side source precedence for `financial_data_center_lt`.
- `ai-skill-hub` is external canonical source, not part of the target project.
- Do not copy `ai-skill-hub` into the target project.
- If an embedded skill-hub snapshot is detected in the target project, treat it as non-canonical runtime copy.
- If an embedded snapshot conflicts with canonical `ai-skill-hub`, report drift and do not silently reconcile.
- This run validates source policy recognition; it does not edit source policy.

## 8. Output requirements

Required outputs:

- Task package at `tasks/p1_7_main_project_takeover_shared_assessment_protocol_dogfood_task_package.md`.
- Review memo at `docs/reviews/main_project_takeover_shared_assessment_protocol_dogfood_review.md`.
- Execution report at `tasks/p1_7_main_project_takeover_shared_assessment_protocol_dogfood_execution_report.md`.
- Final Reviewer decision.
- Recommended commit message:
  - `docs(reviews): dogfood main project takeover with source policy`

The review memo final decision must be exactly one of:

- `Pass: protocol works for main project-level takeover`
- `Pass with light follow-up`
- `Needs project-side policy adjustment`
- `Needs protocol adjustment`
- `No-Go for main project-level adoption`

## 9. Assumptions

- The latest local `main` branch is the intended assessment target; no pull or fetch is authorized.
- `D:\dev\ai-skill-hub` is available as sibling canonical skill source for read-only reference.
- `tasks/` and `docs/reviews/` may be created if absent because the authorized outputs require those paths.
- Running repository inspection commands and `rg` searches is sufficient validation for this documentation-only dogfood.
- Product tests are not required because this run is read-only assessment plus artifact creation, not source behavior change.

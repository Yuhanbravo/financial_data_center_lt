# P1.6 Project Takeover Shared Assessment Protocol Dogfood Task Package

## 1. Background

This task validates `project-takeover` against a real consumer repository, `financial_data_center_lt`, using `D:\dev\ai-skill-hub` only as the canonical external skill source.

The prior P1.5 `system-takeover` dogfood concluded that shared assessment output protocol works for system-level takeover. This P1.6 run checks whether the same protocol also works for project-level takeover in a separate target project.

This run uses external reference mode: do not copy `ai-skill-hub` content into the target project, do not modify `ai-skill-hub`, and treat target project files as the source of truth for target project facts.

## 2. Goal

Perform a read-only `project-takeover` dogfood assessment of `D:\dev\financial_data_center_lt` and produce auditable outputs using shared assessment output fields:

- `capability_fit`
- `maturity_score`, only when applicable
- `evidence`
- `inference`
- `open_questions`
- `risk_priority`
- `impact_scope`
- `next_action`

The final decision must be one of:

- `Pass: protocol works for project-level takeover`
- `Pass with light follow-up`
- `Needs protocol adjustment`
- `No-Go for project-level adoption`

## 3. In Scope

- Use `workflow-bootstrap` as the workflow shell and role-boundary owner.
- Use `chatgpt-handoff-pilot` for task package, bounded execution, and execution report protocol.
- Use `project-takeover` only as a read-only project-level assessment skill.
- Read canonical skill guidance from `D:\dev\ai-skill-hub`.
- Read target project files from `D:\dev\financial_data_center_lt`.
- Create or update only the authorized artifact files in the target project:
  - `tasks/p1_6_project_takeover_shared_assessment_protocol_dogfood_task_package.md`
  - `docs/reviews/project_takeover_shared_assessment_protocol_dogfood_review.md`
  - `tasks/p1_6_project_takeover_shared_assessment_protocol_dogfood_execution_report.md`
- If needed, create only the containing `tasks/` and `docs/reviews/` directories.

## 4. Out of Scope

- Do not modify `D:\dev\ai-skill-hub`.
- Do not copy canonical skill or protocol bodies into the target project.
- Do not modify target project source, tests, scripts, data, config, README, handoff, status, task history, report examples, `.github`, or `.vscode`.
- Do not add validators, automation, CI, scripts, router-pipeline integration, auto-fix, or auto-remediation.
- Do not run destructive cleanup.
- Do not perform broad mandatory maturity scoring.
- Do not commit, push, pull, fetch, merge, or rebase.

## 5. Target files/areas

Read-only target project areas:

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
- selected `data/` sample inventory

Writable artifact files:

- `tasks/p1_6_project_takeover_shared_assessment_protocol_dogfood_task_package.md`
- `docs/reviews/project_takeover_shared_assessment_protocol_dogfood_review.md`
- `tasks/p1_6_project_takeover_shared_assessment_protocol_dogfood_execution_report.md`

## 6. Acceptance checks

- Reviewer Safety Gate returns `Pass` before implementation.
- Review memo contains at least five findings using the shared assessment output fields.
- Each finding separates `evidence.confirmed`, `evidence.inferred`, and `evidence.pending`.
- `risk_priority` is used only as assessment risk priority, not as a phase gate or freshness label.
- `maturity_score` is used only where applicable.
- `next_action` is concrete and executable.
- Review memo accurately matches the current target project state.
- External `ai-skill-hub` reference mode is documented and does not create SSOT conflict.
- Execution report separates changed, unchanged, deferred, and not verified items.
- Final Reviewer returns `Go`, `Go with Conditions`, or `No-Go`.

Validation commands to run in target project:

```powershell
git diff -- docs/reviews tasks
git diff --name-only
git status --short
rg "capability_fit|maturity_score|risk_priority|impact_scope|open_questions|next_action" docs/reviews/project_takeover_shared_assessment_protocol_dogfood_review.md
rg "confirmed|inferred|pending" docs/reviews/project_takeover_shared_assessment_protocol_dogfood_review.md
rg "financial_data_center_lt|project-takeover|ai-skill-hub|external reference|SSOT|validator|CI|automation" docs/reviews/project_takeover_shared_assessment_protocol_dogfood_review.md
git diff --name-only | rg "^(src/|tests/|scripts/|data/|\.github/|\.vscode/|docs/HANDOFF.md|docs/status/|README.md|pyproject.toml|pytest.ini|\.gitignore)"
```

If the final restricted-path check exits with no matches in PowerShell, record the equivalent no-match result rather than treating it as a failure.

Validation command to run in canonical skill source:

```powershell
git status --short
```

## 7. Constraints

- Target project facts are defined by target project files.
- Canonical skill guidance is defined by `D:\dev\ai-skill-hub`.
- If target project contains copied or embedded skill-hub content, treat it as a non-canonical runtime copy and report drift only.
- Do not create a second rulebook in the target project.
- Do not modify restricted paths.
- Do not execute runtime tests unless needed for validation of this documentation-only dogfood; this task primarily validates assessment output, not product behavior.

## 8. Output requirements

The review memo must include:

- Executive Summary
- Scope and Method
- Project State Match Check
- Project Takeover Assessment Using Shared Protocol
- Protocol Dogfood Evaluation
- Final Recommendation
- Recommended Next Action

The execution report must include:

- Scope Restatement
- Files Created / Changed
- What Was Reviewed
- What Was Not Changed
- Validation Performed
- Boundary Checks
- Dogfood Result Summary
- Risks and Assumptions
- Deferred Items
- Recommended Next Step
- Recommended Commit Message

Recommended commit message:

```text
docs(reviews): dogfood project takeover assessment protocol
```

## 9. Assumptions

- The current local checkout of `D:\dev\financial_data_center_lt` is the target project state for this run.
- The current local checkout of `D:\dev\ai-skill-hub` is sufficient as read-only canonical skill guidance.
- No project-local embedded `ai-skill-hub` snapshot exists unless scanning later proves otherwise.
- Missing optional target files or directories should be recorded as `not found`, not created unless they are authorized artifact paths.

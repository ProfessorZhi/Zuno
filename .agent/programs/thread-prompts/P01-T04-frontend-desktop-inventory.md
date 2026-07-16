# P01-T04 Frontend and Desktop Inventory Implementer Prompt

task_id: P01-T04
phase_id: PHASE01
start_commit: c01420e915db19a3b0d6f979ca4450c8d5de0c85
branch: codex/P01-T04-frontend-desktop-inventory
owner_module: 01 Product Surface, Web/Desktop clients as consumers

## Objective

完整盘点 Web/Desktop API Client、DTO、Pinia Store、SSE、Cursor/Resume、Approval、Multiple Interrupt、Citation、Artifact、Trace/Eval、Desktop Bridge、Download、Authorization、Browser E2E、Desktop Smoke。

Update `.agent/programs/work-products/frontend-current-inventory.md` and evidence without changing frontend behavior.

## Required Contract

每项必须区分：

```text
page/component exists
contract adopted
generated or machine-checked type
authorized projection
available action
real E2E/smoke evidence
gap/blocker
target phase
```

## Allowed Paths

```text
.agent/programs/work-products/frontend-current-inventory.md
.agent/programs/work-products/phase-readiness.yaml
docs/evidence/phase01-frontend-desktop-inventory.md
tests/repo/test_phase01_complete_baseline.py
tools/scripts/verify_phase01_complete_baseline.py
```

## Forbidden Paths

Frontend source behavior, backend API behavior, module Target docs, unrelated tests, dependency files.

## Verification Commands

Run available checks and disclose not-run commands:

```powershell
git diff --check
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_phase01_complete_baseline.py
pytest -q tests/repo/test_current_program_contract.py tests/repo/test_phase01_complete_baseline.py -p no:cacheprovider
```

If `apps/web` package scripts are available and dependencies installed, run focused lint/build/test; otherwise record blocked reason.

## Evidence Requirements

Write `docs/evidence/phase01-frontend-desktop-inventory.md` with commit, environment, available package commands, results, browser/desktop evidence status, artifact hash, and not-run reasons.

## Completion Report

Commit and push. Include Current, Gap, commands/results, remaining target, and PHASE10/PHASE21 handoff risks.

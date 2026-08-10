# P01-T01 Runtime Call-chain Inventory Implementer Prompt

task_id: P01-T01
phase_id: PHASE01
start_commit: c01420e915db19a3b0d6f979ca4450c8d5de0c85
branch: codex/P01-T01-runtime-call-chain-inventory
owner_module: all modules, Coordinator owns final PHASE01 closure

## Objective

从最新 `main` / 当前 Coordinator gate 分支重新审计 Runtime Call-chain。更新 `.agent/programs/work-products/current-runtime-inventory.md`，使它覆盖 FastAPI routes、Completion、Workspace Task、Product/Compatibility API、GeneralAgent、Unified Runtime、Durable Runtime、LangGraph、Model、Knowledge、Memory、Capability、Tool、Security、Observability、Queue/Worker、Web、Desktop，以及动态入口。

## Required Contract

每条链必须记录：

```text
entrypoint
caller
callee
factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker if applicable
default implementation
feature flag
state owner
transaction boundary
external side effect
security gate
test evidence
target phase
legacy/removal task
```

## Allowed Paths

```text
.agent/programs/work-products/current-runtime-inventory.md
.agent/programs/work-products/phase-readiness.yaml
docs/evidence/phase01-runtime-call-chain-inventory.md
tests/repo/test_phase01_complete_baseline.py
tools/scripts/verify_phase01_complete_baseline.py
```

Only update verifier/test if needed to encode stricter checks for this task.

## Forbidden Paths

Runtime source behavior, module Target docs, `docs/architecture/**`, unrelated Program phases, dependency files, history archives.

## Current / Gap / Plan Requirement

Before editing, output:

```text
Current: existing inventory, code anchors, tests, dynamic entrypoints found
Gap: missing dynamic/static/runtime coverage and stale evidence
Plan: exact file edits, verification commands, evidence file content
```

Stop if latest code contradicts PHASE01 scope or requires architecture/ownership change.

## Verification Commands

```powershell
git diff --check
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_phase01_complete_baseline.py
pytest -q tests/repo/test_current_program_contract.py tests/repo/test_phase01_complete_baseline.py -p no:cacheprovider
```

`verify_phase01_complete_baseline.py` may still fail because other PHASE01 work packages are incomplete; disclose exact remaining failures.

## Evidence Requirements

Write `docs/evidence/phase01-runtime-call-chain-inventory.md` with commit, environment, commands, result, artifact hash, sampled code paths, dynamic registry/factory findings, and not-run commands.

## Completion Report

Commit and push. Report start_commit, final_commit, modified files, Current, Gap, commands/results, remaining target, and Coordinator decisions required.

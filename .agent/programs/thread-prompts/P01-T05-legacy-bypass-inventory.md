# P01-T05 Legacy, Alias and Bypass Inventory Implementer Prompt

task_id: P01-T05
phase_id: PHASE01
start_commit: c01420e915db19a3b0d6f979ca4450c8d5de0c85
branch: codex/P01-T05-legacy-bypass-inventory
owner_module: Repository Governance with affected module owners

## Objective

完整扫描并更新 `.agent/programs/work-products/legacy-bypass-inventory.yaml`。覆盖直接 Provider SDK、直接 Tool Execute、MCP 直接调用、HTTP Side Effect、subprocess、跨模块 Repository/DB 写、root alias、legacy directory、deprecated endpoint、旧 DTO、旧 Store、旧 Runtime、动态旁路。

## Required Fields

每条必须有：

```text
path
symbol
owner
risk
target_gateway
current_callers
temporary_allowlist
migration_task
removal_task
deadline
guard
test
```

Allowlist 只能登记当前事实，不得扩大永久例外。

## Allowed Paths

```text
.agent/programs/work-products/legacy-bypass-inventory.yaml
.agent/programs/work-products/temporary-allowlist.yaml
.agent/programs/work-products/phase-readiness.yaml
docs/evidence/phase01-legacy-bypass-inventory.md
tests/repo/test_phase01_complete_baseline.py
tools/scripts/verify_phase01_complete_baseline.py
```

## Forbidden Paths

Production runtime code, Target docs, unrelated Program files, deleting legacy files before PHASE22 gate.

## Verification Commands

```powershell
git diff --check
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_phase01_complete_baseline.py
pytest -q tests/repo/test_current_program_contract.py tests/repo/test_phase01_complete_baseline.py -p no:cacheprovider
```

Add focused static searches to the evidence file, for example `rg` patterns for provider SDK imports, `.execute(`, `call_tool`, `subprocess`, `legacy`, and cross-owner database writes.

## Evidence Requirements

Write `docs/evidence/phase01-legacy-bypass-inventory.md` with commit, search commands, result counts, sample findings, artifact hash, and guard gaps.

## Completion Report

Commit and push. Include new/changed inventory entries, removal gate coverage, guard gaps, remaining target, and Coordinator decisions required.

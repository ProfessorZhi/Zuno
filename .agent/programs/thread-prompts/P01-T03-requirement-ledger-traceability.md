# P01-T03 Architecture Requirement Ledger Implementer Prompt

task_id: P01-T03
phase_id: PHASE01
start_commit: c01420e915db19a3b0d6f979ca4450c8d5de0c85
branch: codex/P01-T03-requirement-ledger-traceability
owner_module: all canonical module owners, Coordinator owns ledger closure

## Objective

把 `.agent/programs/work-products/requirement-ledger.yaml` 从 Target-only 清单提升为双向 Requirement Ledger。所有十一模块 Mandatory `ARCH-*` Requirement 必须能够 Target → Current Code/Test/Evidence/Gap/Owner/Target Phase/Planned Work Package，并支持 Code/Test/Evidence → Requirement 反向查询。

## Required Fields

每项至少包含：

```text
requirement_id
module
mandatory
target_statement
current_status
current_paths
gap
owner
target_phase
planned_work_package
dependencies
failure_or_recovery_requirement
test_ids
evidence_refs
reverse_trace_refs
reviewer
```

空证据必须解释为 `needs_evidence` 或 `target_not_current`，不能用通用占位符冒充。

## Allowed Paths

```text
.agent/programs/work-products/requirement-ledger.yaml
.agent/programs/work-products/phase-readiness.yaml
docs/evidence/phase01-requirement-ledger.md
tests/repo/test_phase01_complete_baseline.py
tools/scripts/verify_phase01_complete_baseline.py
```

## Forbidden Paths

Module Target docs, architecture docs, Runtime code, tests unrelated to PHASE01 verifier.

## Verification Commands

```powershell
git diff --check
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_phase01_complete_baseline.py
pytest -q tests/repo/test_current_program_contract.py tests/repo/test_phase01_complete_baseline.py -p no:cacheprovider
```

Closure verifier may still fail until P01-T01/T02/T04/T05/T06 complete; disclose exact remaining failures.

## Evidence Requirements

Write `docs/evidence/phase01-requirement-ledger.md` with requirement count, source extraction method, reverse trace method, sample checks, commands/results, artifact hash, and not-run checks.

## Completion Report

Commit and push. Include start/final commit, ledger stats, unresolved evidence gaps, commands/results, and Coordinator decisions required.

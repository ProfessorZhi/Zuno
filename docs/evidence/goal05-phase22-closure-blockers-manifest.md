# PHASE22 Post-Integration Closure Blocker Manifest

status: current_blocker_gate_available
phase: PHASE22
date: 2026-08-07
source_sha_at_generation: 177d92db55478a7102a13d00b6b4393312ef075d
main_after_pr133: 8e6f5228e8b553199714a420cbf292df8c679e9a
main_at_generation: 177d92db55478a7102a13d00b6b4393312ef075d
integration_basis: claude/minimax-phase22-post-integration-closure

## 结论

PHASE22 当前工程层目标（`engineering_closure_complete` + `measurement_blocked`）可以达成：仓库内可完成的工程工作已收口；但 formal measurement 仍因外部正式事实缺失而 Blocked，Production Readiness 仍为 `not established`，Quality Proven 仍未证明。

本 manifest 不伪造任何 measurement，不声明 `PHASE22_COMPLETED`、`BENCHMARK_PASSED` 或 `PRODUCTION_READY`；只把当前真实外部 Blocker 机器化。

## 当前真实状态

- PHASE22 status phrase: `engineering_closure_complete_measurement_blocked`
- P22-T01 Fixed Benchmark Entry: `implementation_available` + `artifact_contract_available`
- P22-T02 Four Profile Measurement: `measurement_blocked`
- P22-T03 Legacy / Cutover Cleanup: `tool_bypass_blockers_found` (repository gate honest)
- P22-T04 Canonical Structure / Dependency Enforcement: `implementation_available`
- P22-T05 Final Verification: focused gates passed; full E2E / Load / DR / Soak 未运行
- P22-T06 Production Readiness: `production_readiness_not_established`
- P22-T07 Program Closure: `engineering_closure_complete_measurement_blocked`

## 仓库内外部 Blocker Manifest（机器可读）

```json
{
  "manifest_version": "phase22-closure-blockers-manifest.v1",
  "phase": "PHASE22",
  "main_after_pr133": "8e6f5228e8b553199714a420cbf292df8c679e9a",
  "source_sha_at_generation": "177d92db55478a7102a13d00b6b4393312ef075d",
  "integration_basis": "claude/minimax-phase22-post-integration-closure",
  "blockers": [
    {
      "blocker_id": "BLK-P22-T02-001",
      "owner": "external_formal_reviewer",
      "category": "FORMAL_REVIEWER_APPROVAL",
      "required_fact": "reviewer_approved_count > 0 AND benchmark_eligible_count > 0 for the fixed case set",
      "current_status": "reviewer_approved_count=0, benchmark_eligible_count=0",
      "proof_required": "Serialized Reviewer Attestation (phase22-benchmark-preflight.v8) bound to eval_run_id, case_set_ref, dataset_version, dataset_hash, candidate_count and reviewer_attestation_hash",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-P22-T02-002",
      "owner": "external_formal_credential_provisioning",
      "category": "FORMAL_MODEL_CREDENTIAL",
      "required_fact": "formal_credential_attested=true bound to credential_ref, authorization_ref, security_epoch, formal_execution_ref and formal_credential_attestation_hash",
      "current_status": "no Formal Credential Attestation provided",
      "proof_required": "Serialized Formal Credential Attestation matching preflight v8 contract",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-P22-T02-003",
      "owner": "external_runtime_attestation_authority",
      "category": "FORMAL_RUNTIME_ATTESTATION",
      "required_fact": "Serialized Product Runtime Attestation bound per profile (profile_name, runtime_name, runtime_version, corpus_snapshot_ref, security_epoch, formal_adapter_ref) and validated by the canonical four boundary adapters",
      "current_status": "no Product Runtime Attestation provided",
      "proof_required": "Serialized Product Runtime Attestation + adapter-validated runtime evidence binding",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-P22-T02-004",
      "owner": "external_corpus_authority",
      "category": "FORMAL_CORPUS_SNAPSHOT",
      "required_fact": "Frozen canonical corpus snapshot reference + knowledge snapshot reference + graph snapshot reference (only one snapshot is allowed across the four profiles for comparability)",
      "current_status": "corpus_snapshot_ref placeholder only",
      "proof_required": "Persisted canonical snapshot identifier verifiable by the corpus authority",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-P22-T02-005",
      "owner": "external_budget_authority",
      "category": "FORMAL_BUDGET_APPROVAL",
      "required_fact": "Serialized Human Budget Attestation bound to budget_policy_ref, provider_cost_limit, token_limit, deadline and human_budget_attestation_hash",
      "current_status": "no Human Budget Attestation provided",
      "proof_required": "Serialized Human Budget Attestation matching preflight v8 contract",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-P22-T02-006",
      "owner": "external_security_authority",
      "category": "FORMAL_SECURITY_APPROVAL",
      "required_fact": "Serialized Formal Execution Attestation bound to authorization_ref, security_epoch, formal_execution_approved, formal_execution_requested and formal_execution_attestation_hash",
      "current_status": "no Formal Execution Attestation provided",
      "proof_required": "Serialized Formal Execution Attestation matching preflight v8 contract",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-P22-T06-001",
      "owner": "external_postgres_runtime",
      "category": "POSTGRES_RUNTIME_EVIDENCE",
      "required_fact": "Production-shape PostgreSQL runtime evidence (release-candidate build, observed failure / DR / load / soak / backup / restore)",
      "current_status": "Developer / CI adapter evidence only",
      "proof_required": "Production-shape Postgres integration report referenced by `docs/status/production-readiness.md`",
      "unblocks_task": "P22-T06",
      "repository_action_remaining": "None — evidence schema ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-P22-T05-001",
      "owner": "release_governance",
      "category": "EXTERNAL_VERIFICATION_RUN",
      "required_fact": "Full Web / browser E2E, Desktop build/smoke, Migration cutover, Postgres / RabbitMQ / Object / Checkpointer fault, Security, Load / Soak, Backup / Restore against the post-integration main",
      "current_status": "Focused gates only",
      "proof_required": "CI workflow artifacts and operator-signed summary attached to the closure PR",
      "unblocks_task": "P22-T05",
      "repository_action_remaining": "None — focused gates passed; full external runs still pending"
    }
  ],
  "phase_status": {
    "P22-T01": "implementation_available_artifact_contract_available",
    "P22-T02": "measurement_blocked",
    "P22-T03": "tool_bypass_blockers_found_repository_gate_honest",
    "P22-T04": "implementation_available",
    "P22-T05": "focused_gates_passed_full_external_pending",
    "P22-T06": "production_readiness_not_established",
    "P22-T07": "engineering_closure_complete_measurement_blocked"
  },
  "audit_status": "TOOL_BYPASS_BLOCKERS_FOUND",
  "production_readiness": "not_established",
  "quality_proven": false,
  "claims_disallowed": [
    "PHASE22_COMPLETED",
    "BENCHMARK_PASSED",
    "PRODUCTION_READY",
    "PROGRAM_ARCHIVED",
    "QUALITY_PROVEN",
    "22/22 completed"
  ]
}
```

## 仓库内工程收口清单（已完成）

- [x] `run_phase22_formal_benchmark.py` 修复：artifact publication 顺序修正
  - environment.json → env hash → report["artifact_refs"]["environment"] → report_integrity → serialize
  - benchmark_report.json → sha256(bytes) → benchmark_report.json.sha256 → atomic rename
  - disk report 与 in-process report 一致；sidecar 永远从 disk bytes 派生
- [x] `verify_phase22_final_legacy_cutover.py` 加固（name-free rename-evasion hardening）：
  - rename `tool` → `binding` 仍被 flag
  - rename `handler` → `executor` 仍被 flag
  - rename `direct_mcp` → `foo` 仍被 flag（import alias chain walking）
  - module-level helper + module-level helper → tool.ainvoke（two-hop helper）仍被 flag
  - 文件改名 (file rename cannot be statically proven) → AUDIT_UNRESOLVED
  - AUDIT_UNRESOLVED 优先序：unresolved_dynamic_constructor / unresolved_alias_factory 仍 dominate 具体 finding；具体 finding dominate unresolved_file_rename
- [x] `tests/evals/test_phase22_formal_benchmark_entry.py` 35 tests passed
- [x] `tests/repo/test_phase22_final_legacy_cutover.py` 24 tests passed

## 仓库内剩余 Gap（real CLEAN 之前必须修）

- `verify_phase22_final_legacy_cutover.py` 在最新 main 上仍报告 `TOOL_BYPASS_BLOCKERS_FOUND`（224 findings）。
  - 主因：`src/backend/zuno/platform/services/workspace/simple_agent.py`、`wechat_agent.py`、MCP loader / manager / multi_client 层仍直接 dispatch MCP / tool.ainvoke。
  - 这是 Repository Layer 工程 gap：需要把 MCP 调用收敛到 `ToolInvocationGateway → registered executor → provider call → Observation / Receipt` 形态。
  - 本次 post-integration closure 不强制 CLEAN；只建立真实 status。

## 验证命令

```bash
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_current_program.py
python tools/scripts/verify_phase22_completion_blockers.py
python tools/scripts/verify_phase22_cleanup_boundary.py
python tools/scripts/verify_agent_core_target_protocols.py
python tools/scripts/verify_tool_execution_bypass.py
python tools/scripts/verify_phase22_backend_semantic_legacy.py --scope repository
python tools/scripts/verify_phase22_feature_flag_runtime_cutover.py --scope repository
python tools/scripts/verify_phase22_final_legacy_cutover.py \
  --integration-base-sha <CODE_CANDIDATE_SHA>
python tools/scripts/verify_phase22_formal_benchmark_entry.py
# focused pytest:
python -m pytest tests/evals/test_phase22_formal_benchmark_entry.py -q -p no:cacheprovider
python -m pytest tests/repo/test_phase22_final_legacy_cutover.py -q -p no:cacheprovider
```

## Evidence

- `docs/evidence/goal05-phase22-blocked-benchmark/benchmark_manifest.json`
- `docs/evidence/goal05-phase22-completion-blockers.md`
- `docs/evidence/goal05-phase22-closure-summary.md`
- `docs/evidence/goal05-phase22-final-legacy-audit-v3/audit_report.json`
- `docs/evidence/goal05-phase22-final-legacy-audit-v3/AUDIT-V3.md`
- `.agent/programs/PHASE22_fixed-benchmark-production-readiness-and-closure.md`
- `.agent/programs/work-products/goal05-target-gap-ledger.yaml`

## Known Limitations

- This report does not claim PHASE22 completed.
- It does not claim BENCHMARK_PASSED, PRODUCTION_READY, QUALITY_PROVEN or 22/22 completed.
- It is a reproducible engineering-closure snapshot for the current post-integration main.
- The audit verdict on the post-integration main is `TOOL_BYPASS_BLOCKERS_FOUND`; this is the honest repository-gate state.
- Production Readiness remains `not_established` until external Postgres / Load / Soak / DR / Security evidence is supplied.
- The Formal Measurement path remains `blocked_not_measured` until external Reviewer / Credential / Runtime / Budget / Security attestations and the frozen corpus snapshot are supplied.
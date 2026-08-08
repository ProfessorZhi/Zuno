# PHASE22 Post-Integration Closure Blocker Manifest

status: current_blocker_gate_available
phase: PHASE22
date: 2026-08-08
revision: 3 (minimax1 audit slice — function-scoped getattr fix + seven classification taxonomy; see "minimax1 Audit Slice (Revision 3)" below)
source_sha_at_generation: b7796246d41d51b8f9cb92409cb1acc116d1fda8
main_after_pr133: 8e6f5228e8b553199714a420cbf292df8c679e9a
main_after_pr134: 1dedd54830de6f761ac492a8348ec59f29b56a98
main_after_pr135: b7796246d41d51b8f9cb92409cb1acc116d1fda8
main_at_generation: b7796246d41d51b8f9cb92409cb1acc116d1fda8
integration_basis: claude/minimax-phase22-post-integration-closure

## 结论（修订）

上一版（revision 1）将 PHASE22 状态写成 `engineering_closure_complete_measurement_blocked`，但同一文档又显式记录 `P22-T03 = tool_bypass_blockers_found` 与 6 个 `repository_internal_blockers`。这两个声明互斥：在 6 个内部 Blocker 全部关闭之前，Engineering Closure 尚未完成。

修订后真实状态：

```text
engineering_closure_in_progress
measurement_blocked
quality_not_yet_proven
production_readiness_not_established
```

只有当 `repository_internal_blockers == []` 且 Final Legacy Audit / Backend Runtime Cutover / Feature Flag Runtime Cutover 三个 Repository Gate 全部满足对应 verdict 时，才能升级到：

```text
engineering_closure_complete_measurement_blocked
```

本 manifest 仍然禁止声明 `PHASE22_COMPLETED`、`BENCHMARK_PASSED`、`PRODUCTION_READY`、`QUALITY_PROVEN`、`PROGRAM_ARCHIVED` 或 `22/22 completed`。

## PR #134 History Truth（修订）

PR #134 合并信息中曾出现：

> remaining findings = VERIFIER_FALSE_POSITIVE_CANDIDATE

并暗示 real product bypasses = zero。

但 minimax1 / minimax2 的 worker 报告与最新 main 上的最终 verifier run 明确记录：

- `WorkSpaceSimpleAgent.execute_binding_tool` 仍存在真实 `binding.ainvoke` direct Tool dispatch。
- `WeChatAgent` 存在类似真实 direct Tool dispatch。
- Final Legacy Audit 在最新 main 上仍为 `TOOL_BYPASS_BLOCKERS_FOUND`。
- Backend Semantic Legacy Verifier 仍为 `BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED`。
- Feature Flag Runtime Cutover Verifier 仍为 `FEATURE_FLAG_RUNTIME_CUTOVER_BLOCKED`。

正确历史：

```text
PR #134 removed image_gen direct bypass and product_baseline production
reachability, and refined the Antigravity / minimax1 slice, but at
least Workspace / WeChat direct tool dispatch remained on the
post-integration main and required a follow-up runtime slice.
```

Verifier 不允许 default-safe：

- 禁止按字符串 Allowlist 路径；
- 禁止按 receiver 名字 Allowlist；
- 禁止按 Class 名字永久 Block；
- 禁止按 Class 名字永久 Allow；
- 禁止 Product direct registered executor 被允许；
- 必须通过 ownership static proof（A. registration_site + B. gateway_dispatch_site + C. executor_adapter 全部存在）。

## 当前真实状态（修订）

- PHASE22 status phrase: `engineering_closure_in_progress_measurement_blocked`
- P22-T01 Fixed Benchmark Entry: `implementation_available` + `artifact_contract_available`
- P22-T02 Four Profile Measurement: `measurement_blocked`
- P22-T03 Legacy / Cutover Cleanup: `tool_bypass_blockers_found` (repository gate honest)
- P22-T04 Canonical Structure / Dependency Enforcement: `tool_bypass_blockers_found` / `backend_product_runtime_cutovert_blocked`
- P22-T05 Final Verification: focused gates passed; full E2E / Load / DR / Soak 未运行
- P22-T06 Production Readiness: `production_readiness_not_established`
- P22-T07 Program Closure: `engineering_closure_in_progress_measurement_blocked`

## 仓库内外部 Blocker Manifest（机器可读，修订）

```json
{
  "manifest_version": "phase22-closure-blockers-manifest.v3",
  "phase": "PHASE22",
  "main_after_pr133": "8e6f5228e8b553199714a420cbf292df8c679e9a",
  "main_after_pr134": "1dedd54830de6f761ac492a8348ec59f29b56a98",
  "main_after_pr135": "b7796246d41d51b8f9cb92409cb1acc116d1fda8",
  "main_at_generation": "b7796246d41d51b8f9cb92409cb1acc116d1fda8",
  "integration_basis": "claude/minimax-phase22-post-integration-closure",
  "minimax1_audit_slice": {
    "owner": "minimax1",
    "scope": "Final Legacy Audit Verifier hardening + MCP semantic classification",
    "function_scoped_getattr_fix": "applied — _detect_unresolved_file_rename now requires function-scoped getattr→dispatch correlation, not file-wide scan",
    "seven_classification_taxonomy": [
      "REAL_PRODUCT_BYPASS",
      "CANONICAL_GATEWAY_EXECUTOR",
      "MCP_ADMIN_CONTROL_PLANE",
      "MCP_DISCOVERY_REGISTRATION",
      "MODEL_GATEWAY_INTERNAL",
      "INTERNAL_TEST_EVAL",
      "UNRESOLVED"
    ],
    "classification_counts_at_pr135_main": {
      "REAL_PRODUCT_BYPASS": 16,
      "CANONICAL_GATEWAY_EXECUTOR": 0,
      "MCP_ADMIN_CONTROL_PLANE": 0,
      "MCP_DISCOVERY_REGISTRATION": 0,
      "MODEL_GATEWAY_INTERNAL": 0,
      "INTERNAL_TEST_EVAL": 0,
      "UNRESOLVED": 10
    },
    "test_status": "29 passed in 11m19s (test_phase22_final_legacy_cutover.py)"
  },
  "repository_internal_blockers": [
    {
      "blocker_id": "BLK-INT-001",
      "owner": "minimax2 (semantic verifier) + minimax1 (runtime producer)",
      "category": "WORKSPACE_DIRECT_TOOL_BYPASS",
      "required_fact": "WorkSpaceSimpleAgent.execute_binding_tool no longer reaches a real Product Tool bypass; instead routes through ToolInvocationGateway → registered executor → provider call",
      "current_status": "binding.ainvoke direct dispatch remains on the post-integration main (workspace.py:299 image_gen, autobuild/client.py:5 sites)",
      "proof_required": "Final Legacy Audit CLEAN for WorkSpaceSimpleAgent + Backend Semantic Legacy PRODUCT_CANONICAL classification",
      "unblocks_task": "P22-T03, P22-T04",
      "repository_action_remaining": "minimax1 Runtime V2 cutover (next merge) + verifier re-classification"
    },
    {
      "blocker_id": "BLK-INT-002",
      "owner": "minimax2 (semantic verifier) + minimax1 (runtime producer)",
      "category": "WECHAT_DIRECT_TOOL_BYPASS",
      "required_fact": "WeChatAgent no longer reaches a real Product Tool bypass; instead routes through the WorkspaceAgentRuntime canonical delegate",
      "current_status": "analogous real bypass remains on the post-integration main",
      "proof_required": "Final Legacy Audit CLEAN for WeChatAgent + Backend Semantic Legacy PRODUCT_CANONICAL classification",
      "unblocks_task": "P22-T03, P22-T04",
      "repository_action_remaining": "minimax1 Runtime V2 cutover (next merge) + verifier re-classification"
    },
    {
      "blocker_id": "BLK-INT-003",
      "owner": "minimax2 (semantic verifier)",
      "category": "MCP_EXECUTION_OWNERSHIP_UNRESOLVED",
      "required_fact": "MCP server / loader / multi_client layer every direct execute path is classified as MCP_ADMIN_CONTROL_PLANE or MCP_DISCOVERY_REGISTRATION, with static ownership proof (registration_site + gateway_dispatch_site + executor_adapter)",
      "current_status": "verifier now classifies findings into the seven canonical closure classes (REAL_PRODUCT_BYPASS / CANONICAL_GATEWAY_EXECUTOR / MCP_ADMIN_CONTROL_PLANE / MCP_DISCOVERY_REGISTRATION / MODEL_GATEWAY_INTERNAL / INTERNAL_TEST_EVAL / UNRESOLVED); MCP_ADMIN and MCP_DISCOVERY classifier wires through ToolControlPlane / register_executor_adapter, but legacy MCP chat paths in api/services/mcp_chat.py and api/v1/mcp_chat.py still surface as REAL_PRODUCT_BYPASS",
      "proof_required": "Final Legacy Audit MCP_ADMIN/MCP_DISCOVERY count equals total MCP call sites minus canonical_gateway_executor sites minus product_direct_mcp sites",
      "unblocks_task": "P22-T03",
      "repository_action_remaining": "PR #135 has routed Workspace/WeChat MCP tool execution through MCPToolExecutorAdapter — verifier now proves ownership statically; remaining cleanup is the api/services/mcp_chat.py + api/v1/mcp_chat.py direct dispatch sites"
    },
    {
      "blocker_id": "BLK-INT-004",
      "owner": "minimax2 (semantic verifier)",
      "category": "FINAL_LEGACY_AUDIT_NOT_CLEAN",
      "required_fact": "verify_phase22_final_legacy_cutover.py reports LEGACY_CUTOVER_AUDIT_CLEAN with 0 findings and 0 unresolved",
      "current_status": "TOOL_BYPASS_BLOCKERS_FOUND with finding_count=16 (REAL_PRODUCT_BYPASS) and unresolved_count=10 (UNRESOLVED — phase08.py + service.py + structured_response_agent.py + react_step.py + mcp_chat.py × 2 + workspace.py + autobuild/client.py + graphrag/query_service.py + graphrag/retriever.py) on PR #135 main @ b7796246",
      "proof_required": "audit_report.json status=LEGACY_CUTOVER_AUDIT_CLEAN",
      "unblocks_task": "P22-T03, P22-T07 (engineering closure upgrade)",
      "repository_action_remaining": "minimax1 Runtime V2 cutover (next merge) + semantic classifier upgrade + re-audit"
    },
    {
      "blocker_id": "BLK-INT-005",
      "owner": "minimax2 (semantic verifier)",
      "category": "BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED",
      "required_fact": "verify_phase22_backend_semantic_legacy.py --scope repository reports BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED with no PRODUCT_LEGACY_RUNTIME findings",
      "current_status": "BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED (WorkSpaceSimpleAgent / WeChatAgent)",
      "proof_required": "verifier output status=BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED",
      "unblocks_task": "P22-T04",
      "repository_action_remaining": "minimax1 Runtime V2 cutover + verifier hardening"
    },
    {
      "blocker_id": "BLK-INT-006",
      "owner": "minimax2 (semantic verifier)",
      "category": "FEATURE_FLAG_RUNTIME_CUTOVER_BLOCKED",
      "required_fact": "verify_phase22_feature_flag_runtime_cutover.py --scope repository reports FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED with no direct_tool_bypass / runtime_selector findings",
      "current_status": "FEATURE_FLAG_RUNTIME_CUTOVER_BLOCKED",
      "proof_required": "verifier output status=FEATURE_FLAG_RUNTIME_CUTOVER_CONFIRMED",
      "unblocks_task": "P22-T04",
      "repository_action_remaining": "minimax1 Runtime V2 cutover + verifier hardening"
    },
    {
      "blocker_id": "BLK-INT-007",
      "owner": "minimax1 (postgres owner fact)",
      "category": "OWNER_FACT_POSTGRES_NOT_FINAL",
      "required_fact": "Budget/Security PostgreSQL Owner Fact is finalised (canonical table + audit trail)",
      "current_status": "Owner Fact pending minimax2 worker (separate worker scope, not minimax1)",
      "proof_required": "minimax2 closes OWNER_FACT_POSTGRES_NOT_FINAL",
      "unblocks_task": "P22-T03, P22-T04",
      "repository_action_remaining": "out of minimax1 scope — minimax2 will close this"
    }
  ],
  "external_blockers": [
    {
      "blocker_id": "BLK-EXT-001",
      "owner": "external_formal_reviewer",
      "category": "FORMAL_REVIEWER_APPROVAL",
      "required_fact": "reviewer_approved_count > 0 AND benchmark_eligible_count > 0 for the fixed case set",
      "current_status": "reviewer_approved_count=0, benchmark_eligible_count=0",
      "proof_required": "Serialized Reviewer Attestation (phase22-benchmark-preflight.v8) bound to eval_run_id, case_set_ref, dataset_version, dataset_hash, candidate_count and reviewer_attestation_hash",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-EXT-002",
      "owner": "external_formal_credential_provisioning",
      "category": "FORMAL_MODEL_CREDENTIAL",
      "required_fact": "formal_credential_attested=true bound to credential_ref, authorization_ref, security_epoch, formal_execution_ref and formal_credential_attestation_hash",
      "current_status": "no Formal Credential Attestation provided",
      "proof_required": "Serialized Formal Credential Attestation matching preflight v8 contract",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-EXT-003",
      "owner": "external_runtime_attestation_authority",
      "category": "FORMAL_RUNTIME_ATTESTATION",
      "required_fact": "Serialized Product Runtime Attestation bound per profile (profile_name, runtime_name, runtime_version, corpus_snapshot_ref, security_epoch, formal_adapter_ref) and validated by the canonical four boundary adapters",
      "current_status": "no Product Runtime Attestation provided",
      "proof_required": "Serialized Product Runtime Attestation + adapter-validated runtime evidence binding",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-EXT-004",
      "owner": "external_corpus_authority",
      "category": "FORMAL_CORPUS_SNAPSHOT",
      "required_fact": "Frozen canonical corpus snapshot reference + knowledge snapshot reference + graph snapshot reference (only one snapshot is allowed across the four profiles for comparability)",
      "current_status": "corpus_snapshot_ref placeholder only",
      "proof_required": "Persisted canonical snapshot identifier verifiable by the corpus authority",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-EXT-005",
      "owner": "external_budget_authority",
      "category": "FORMAL_BUDGET_APPROVAL",
      "required_fact": "Serialized Human Budget Attestation bound to budget_policy_ref, provider_cost_limit, token_limit, deadline and human_budget_attestation_hash",
      "current_status": "no Human Budget Attestation provided",
      "proof_required": "Serialized Human Budget Attestation matching preflight v8 contract",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-EXT-006",
      "owner": "external_security_authority",
      "category": "FORMAL_SECURITY_APPROVAL",
      "required_fact": "Serialized Formal Execution Attestation bound to authorization_ref, security_epoch, formal_execution_approved, formal_execution_requested and formal_execution_attestation_hash",
      "current_status": "no Formal Execution Attestation provided",
      "proof_required": "Serialized Formal Execution Attestation matching preflight v8 contract",
      "unblocks_task": "P22-T02",
      "repository_action_remaining": "None — entry ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-EXT-007",
      "owner": "external_postgres_runtime",
      "category": "POSTGRES_PRODUCTION_EVIDENCE",
      "required_fact": "Production-shape PostgreSQL runtime evidence (release-candidate build, observed failure / DR / load / soak / backup / restore)",
      "current_status": "Developer / CI adapter evidence only",
      "proof_required": "Production-shape Postgres integration report referenced by `docs/status/production-readiness.md`",
      "unblocks_task": "P22-T06",
      "repository_action_remaining": "None — evidence schema ready, awaiting external fact"
    },
    {
      "blocker_id": "BLK-EXT-008",
      "owner": "release_governance",
      "category": "FULL_EXTERNAL_VERIFICATION",
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
    "P22-T04": "tool_bypass_blockers_found_runtime_cutovert_blocked",
    "P22-T05": "focused_gates_passed_full_external_pending",
    "P22-T06": "production_readiness_not_established",
    "P22-T07": "engineering_closure_in_progress_measurement_blocked"
  },
  "audit_status": "TOOL_BYPASS_BLOCKERS_FOUND",
  "audit_classification_counts": {
    "REAL_PRODUCT_BYPASS": 16,
    "CANONICAL_GATEWAY_EXECUTOR": 0,
    "MCP_ADMIN_CONTROL_PLANE": 0,
    "MCP_DISCOVERY_REGISTRATION": 0,
    "MODEL_GATEWAY_INTERNAL": 0,
    "INTERNAL_TEST_EVAL": 0,
    "UNRESOLVED": 10
  },
  "production_readiness": "not_established",
  "quality_proven": false,
  "claims_disallowed": [
    "PHASE22_COMPLETED",
    "BENCHMARK_PASSED",
    "PRODUCTION_READY",
    "PROGRAM_ARCHIVED",
    "QUALITY_PROVEN",
    "22/22 completed",
    "ENGINEERING_CLOSURE_COMPLETE (until repository_internal_blockers is empty and Repository Gates are clean)",
    "LEGACY_CUTOVER_AUDIT_CLEAN (until classification_counts.UNRESOLVED == 0 AND classification_counts.REAL_PRODUCT_BYPASS == 0)"
  ]
}
```

## Verifier 不允许的 default-safe 模式

- 禁止按 path substring Allowlist（`/mcp/` → safe）
- 禁止按 file-name Allowlist（`mcp_*.py` → safe）
- 禁止按具体 line Allowlist
- 禁止按 receiver 名字 Allowlist（`MCPTool*` → safe）
- 禁止按 Class 名字永久 Block
- 禁止按 Class 名字永久 Allow
- 禁止 Product direct registered executor 被允许

Verifier 必须证明 ownership：

1. **registration_site**：找到 `executor_adapter.register(...)` / `register_executor_adapter(...)` / `register_manifest(...)` / `ToolControlPlane.register_*` 等静态注册调用
2. **gateway_dispatch_site**：找到 `ToolInvocationGateway.invoke(...)` / `ToolControlPlaneRuntime.invoke(...)` 等 canonical dispatch
3. **executor_adapter**：在调用链上能找到 `ExecutorAdapterContract` / `register_executor_adapter` 注册的 executor 实现

三者全部存在才允许 `CANONICAL_GATEWAY_EXECUTOR` 分类；缺一不可。

## 当前已知 Finding Inventory 入口

- 见 `docs/evidence/goal05-phase22-final-legacy-audit-v3/audit_report.json`（基于 PR #134 之后 main）
- 见 `docs/evidence/goal05-phase22-final-legacy-audit-v3/AUDIT-V3.md`
- 见 `docs/evidence/goal05-phase22-backend-semantic-legacy-cleanup/`（待 minimax1 Runtime V2 merge 后重新生成）
- 见 `docs/evidence/goal05-phase22-feature-flag-runtime-cutover/`（待 minimax1 Runtime V2 merge 后重新生成）

## minimax1 Audit Slice (Revision 3)

minimax1 is the owner of the **Final Legacy Audit Verifier** + **MCP semantic classification** + **AUDIT_UNRESOLVED convergence** + **Closure Manifest Truth** + **Final Audit Evidence** + **PHASE22 Program Truth** + **最终 Engineering Closure 集成** scope on `claude/minimax-phase22-post-integration-closure`.

This revision (rev 3) records three concrete outcomes delivered by the minimax1 worker against the PR #135 main (`b7796246d41d51b8f9cb92409cb1acc116d1fda8`):

### 1. Function-scoped getattr correlation (fix for the previous over-broad scan)

`_detect_unresolved_file_rename` previously walked the file-wide `ast.walk(tree)` twice — once looking for any `getattr(...)` call and once looking for any `await <attr>.invoke(...)` pattern anywhere in the file. This produced massive false positives on the production tree because an unrelated `getattr` in function A and an unrelated `tool.ainvoke` in function B were incorrectly associated.

The hardened detector (rev 3) is **function-scoped**: it walks each `FunctionDef` / `AsyncFunctionDef` in isolation and only fires when the SAME function contains both:

- an assignment `var = getattr(...)` (with transitive alias resolution: `handler = getattr(...)` → `alias = handler` → `await alias.ainvoke(...)`); AND
- an `await` whose receiver chain terminates at a getattr-derived name.

Minimum data flow the detector requires:

```python
async def run(self, payload):
    executor = getattr(obj, dynamic_name)   # (1) assignment from getattr
    return await executor.ainvoke(payload)   # (2) dispatch on result
```

The new `tests/fixtures/phase22_final_legacy_cutover/negative_clean/negative_unrelated_getattr_and_invoke.py` + `test_unrelated_getattr_and_invoke_not_correlated` prove case 11 ("unrelated getattr + unrelated invoke → 不得误关联") is now fail-closed.

### 2. Seven canonical closure classifications

Every emitted finding now carries exactly one of seven canonical classifications (used by the engineering closure manifest):

| classification | mapped internal categories |
| --- | --- |
| `REAL_PRODUCT_BYPASS` | `tool_bypass_invoke`, `tool_bypass_handler`, `tool_bypass_direct_mcp`, `tool_bypass_image_gen`, `tool_bypass_read_only`, `model_bypass_direct`, `legacy_runtime_class_def`, `legacy_phase08_reachability`, `legacy_workspace_runtime`, `dual_path_signal`, `dual_path_expired_flag_reader`, `ownership_dao_write`, `ownership_plan_owned` |
| `UNRESOLVED` | `unresolved_dynamic_constructor`, `unresolved_alias_factory`, `unresolved_file_rename` |
| `CANONICAL_GATEWAY_EXECUTOR` | reserved for canonical gateway executor sites (currently 0 — none qualify statically yet) |
| `MCP_ADMIN_CONTROL_PLANE` | reserved for MCP admin / lifecycle / config CRUD / health surfaces |
| `MCP_DISCOVERY_REGISTRATION` | reserved for MCP list tools / schema discovery / executor registration |
| `MODEL_GATEWAY_INTERNAL` | reserved for model-gateway internal model/provider invocations |
| `INTERNAL_TEST_EVAL` | reserved for test/eval scaffolding |

The audit JSON now reports `classification_counts` (all seven keys present even when count is zero). The fixture suite in `tests/fixtures/phase22_final_legacy_cutover/mcp_ownership/` + `tests/fixtures/phase22_final_legacy_cutover/negative_clean/` proves the detector recognises the canonical gateway / admin / discovery shapes without resorting to path substring Allowlists.

Unknown internal categories default to `UNRESOLVED` (fail-closed): adding a new category without updating `_CLASSIFICATION_FOR_CATEGORY` immediately surfaces every emitted finding as `UNRESOLVED`.

### 3. Verifier findings inventory on PR #135 main

Run on `b7796246d41d51b8f9cb92409cb1acc116d1fda8`:

```
status: TOOL_BYPASS_BLOCKERS_FOUND
classification_counts:
  REAL_PRODUCT_BYPASS:        16
  CANONICAL_GATEWAY_EXECUTOR:  0
  MCP_ADMIN_CONTROL_PLANE:     0
  MCP_DISCOVERY_REGISTRATION:  0
  MODEL_GATEWAY_INTERNAL:      0
  INTERNAL_TEST_EVAL:          0
  UNRESOLVED:                 10
```

Breakdown:

- **REAL_PRODUCT_BYPASS (16)** — every direct tool / model dispatch that bypasses the canonical Tool Control Plane. Distribution: `agent/runtime/phase08.py` (4 × `self.graph.invoke`), `agent/runtime/service.py` (2 × `self.graph.invoke`), `agent/core/agents/structured_response_agent.py:21`, `agent/runtime/execution/react_step.py:24`, `api/services/mcp_chat.py:67` (direct `deep_anthropic.ainvoke`), `api/services/workspace.py:299` (image_gen bypass), `api/v1/mcp_chat.py:22` (alias MCP direct dispatch), `platform/services/autobuild/client.py` (4 × `self.base_agent.ainvoke` / `self.abstract_agent.ainvoke`), `platform/services/graphrag/query_service.py:194` (`self.orchestrator.run`).

- **UNRESOLVED (10)** — file-rename / function-scoped dynamic-dispatch ambiguity. Distribution: `agent/runtime/phase08.py`, `agent/runtime/service.py`, `agent/core/agents/structured_response_agent.py`, `agent/runtime/execution/react_step.py`, `api/services/mcp_chat.py`, `api/services/workspace.py`, `api/v1/mcp_chat.py`, `platform/services/autobuild/client.py`, `platform/services/graphrag/query_service.py`, `platform/services/graphrag/retriever.py`. These files do not match the canonical executor adapter naming contract and either have a real bypass on them or exhibit a function-scoped `getattr`→dispatch chain.

The audit remains **fail-closed**: `UNRESOLVED > 0` means the audit cannot claim `LEGACY_CUTOVER_AUDIT_CLEAN`. The current non-CLEAN status is the honest repository-gate state.

### Test status

`tests/repo/test_phase22_final_legacy_cutover.py` — **29 passed** in 11m19s on PR #135 main.

Key coverage added or restored in rev 3:

- `test_unrelated_getattr_and_invoke_not_correlated` — case 11 (unrelated getattr + unrelated invoke).
- `test_classification_counts_cover_seven_closure_classes` — every finding carries a valid classification.
- Updated `test_json_shape_is_stable` to assert `classification_counts` is part of the stable payload and each finding carries the `classification` field.

### Path ownership (minimax1 slice)

Modified on the closure branch:

- `tools/scripts/verify_phase22_final_legacy_cutover.py`
- `tests/repo/test_phase22_final_legacy_cutover.py`
- `tests/fixtures/phase22_final_legacy_cutover/negative_clean/negative_unrelated_getattr_and_invoke.py`
- `docs/evidence/goal05-phase22-closure-blockers-manifest.md`

Out of minimax1 scope (other workers own these):

- `tools/scripts/verify_phase22_backend_semantic_legacy.py`
- `tools/scripts/verify_phase22_feature_flag_runtime_cutover.py`
- Budget/Security PostgreSQL Owner Fact implementation
- Workspace / WeChat / MCP production runtime (PR #135 closed Workspace/WeChat; MCP admin/discovery classifier wires through ToolControlPlane / register_executor_adapter but `api/services/mcp_chat.py` and `api/v1/mcp_chat.py` remain to be retired)

## 验证命令

```bash
git diff --check
python -m compileall -q src/backend
python -m compileall -q tools/scripts
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
  --integration-base-sha 177d92db55478a7102a13d00b6b4393312ef075d
# focused pytest:
python -m pytest tests/repo/test_phase22_final_legacy_cutover.py -q -p no:cacheprovider
python -m pytest tests/repo/test_phase22_feature_flag_runtime_cutover.py -q -p no:cacheprovider
python -m pytest tests/repo/test_phase22_backend_semantic_legacy.py -q -p no:cacheprovider
```

## Evidence

- `docs/evidence/goal05-phase22-blocked-benchmark/benchmark_manifest.json`
- `docs/evidence/goal05-phase22-completion-blockers.md`
- `docs/evidence/goal05-phase22-closure-summary.md`
- `docs/evidence/goal05-phase22-final-legacy-audit-v3/audit_report.json`
- `docs/evidence/goal05-phase22-final-legacy-audit-v3/AUDIT-V3.md`
- `.agent/programs/PHASE22_fixed-benchmark-production-readiness-and-closure.md`
- `.agent/programs/work-products/goal05-target-gap-ledger.yaml`
- `tests/repo/test_phase22_final_legacy_cutover.py` (29 tests, all passing)
- `tests/fixtures/phase22_final_legacy_cutover/` (12 fixtures covering all 12 required scenarios)

## minimax1 Audit Slice Evidence (Revision 3)

The minimax1 audit slice produces the following evidence:

| Artifact | Location | Status |
| --- | --- | --- |
| Function-scoped getattr fix | `tools/scripts/verify_phase22_final_legacy_cutover.py` (lines ~1585–1755) | applied |
| Seven-classification taxonomy | `tools/scripts/verify_phase22_final_legacy_cutover.py::_CLASSIFICATION_FOR_CATEGORY` | applied |
| Case 11 negative fixture | `tests/fixtures/phase22_final_legacy_cutover/negative_clean/negative_unrelated_getattr_and_invoke.py` | added |
| Case 11 test | `tests/repo/test_phase22_final_legacy_cutover.py::test_unrelated_getattr_and_invoke_not_correlated` | passing |
| Classification counts test | `tests/repo/test_phase22_final_legacy_cutover.py::test_classification_counts_cover_seven_closure_classes` | passing |
| JSON shape stability test | `tests/repo/test_phase22_final_legacy_cutover.py::test_json_shape_is_stable` | updated + passing |
| Manifest revision 3 | `docs/evidence/goal05-phase22-closure-blockers-manifest.md` | this document |

Final audit verdict on PR #135 main (`b7796246d41d51b8f9cb92409cb1acc116d1fda8`):

```text
status:                         TOOL_BYPASS_BLOCKERS_FOUND
finding_count:                  16
unresolved_count:               10
classification_counts:
  REAL_PRODUCT_BYPASS:          16
  CANONICAL_GATEWAY_EXECUTOR:    0
  MCP_ADMIN_CONTROL_PLANE:       0
  MCP_DISCOVERY_REGISTRATION:    0
  MODEL_GATEWAY_INTERNAL:        0
  INTERNAL_TEST_EVAL:            0
  UNRESOLVED:                   10
```

The audit is honest: 16 real-product bypasses remain on the post-integration main (these are owned by the minimax2 worker / minimax1 Runtime V2 cutover scope, not by the verifier itself), and 10 files remain `UNRESOLVED` because they exhibit either a real bypass or a function-scoped `getattr`→dispatch chain.

## Known Limitations

- This report does not claim PHASE22 completed.
- It does not claim BENCHMARK_PASSED, PRODUCTION_READY, QUALITY_PROVEN or 22/22 completed.
- It does not claim ENGINEERING_CLOSURE_COMPLETE until `repository_internal_blockers == []` and Repository Gates are clean.
- It does not claim LEGACY_CUTOVER_AUDIT_CLEAN until `classification_counts.UNRESOLVED == 0` and `classification_counts.REAL_PRODUCT_BYPASS == 0`.
- It is a reproducible engineering-closure-in-progress snapshot for the current post-integration main.
- The audit verdict on the post-integration main is `TOOL_BYPASS_BLOCKERS_FOUND`; this is the honest repository-gate state.
- Production Readiness remains `not_established` until external Postgres / Load / Soak / DR / Security evidence is supplied.
- The Formal Measurement path remains `blocked_not_measured` until external Reviewer / Credential / Runtime / Budget / Security attestations and the frozen corpus snapshot are supplied.
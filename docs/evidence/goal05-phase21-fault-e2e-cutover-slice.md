# Goal05 PHASE21 Fault / Recovery Slice Evidence

status: in_progress
date: 2026-07-29
branch: codex/goal05-phase15-sandbox-repair

## Scope

本证据只记录 PHASE21 的一个真实修复切片：Capability exposure 的攻击面约束，以及 Agent recovery 的 crash matrix。它不声明 PHASE21 完成，不声明 full E2E / cutover / rollback / load / soak / removal candidate closure。

已完成：

- 新增 `src/backend/zuno/capability/conformance.py`。
- `CapabilityRouter` 在默认 `planner_exposure` 生成后，执行 fail-closed conformance 校验。
- exposure 仅允许已授权 capability 摘要进入 planner trace。
- `required_roles`、`credential_policy`、`dependency_probe` 等敏感字段不得泄漏到 planner exposure。
- task goal 中出现 prompt injection 标记时，只记录攻击痕迹，不改变授权边界。
- 新增 `Phase21CrashRecoveryMatrix`，复用现有 `ParallelRecoveryPlanner` 评估 crash / replay / late result 场景。
- crash matrix 覆盖 domain commit before checkpoint、dispatch commit before send、result before reducer、publisher restart、consumer restart、late branch result。
- late result 会被 fenced，不会直接覆盖当前 execution epoch。
- 新增 fault tests 覆盖 capability attack conformance 与 crash recovery matrix。
- Workspace approve API 现在将 `approval_id`、`tool_call_id` 和 `required_approval` 传入默认 service。
- 工具审批恢复时必须匹配当前 pending tool request；旧 `approval_id` 或错误 tool call 会产生 `approval_replay_rejected` 事件并保持 `approval_waiting`。
- 修复 ToolRuntime 在 FastAPI async endpoint 内调用 side-effect gateway 时的 event loop 嵌套问题；已有 event loop 时通过短生命周期线程执行网关协程。
- 修复知识检索产品模式优先级：显式 `contract_review` / `enterprise_kb` 不再被默认 `standard` retrieval profile 降级为 `normal/basic`。
- 修复产品仓库的 `ProductCommandSubmission.payload_json` 兼容别名，并将 `product_agent_versions` / `product_agent_drafts` 的 JSON 入库参数规范化为可复现 JSON 文本，恢复统一产品场景的默认记录链。
- 修复 Web 前端 package scripts 的安装布局假设：`apps/web` 现在通过 `scripts/run-bin.mjs` 同时支持容器内 app-local `node_modules` 和本地 workspace root `node_modules`，恢复 Docker frontend production build。

## Verification

```text
docker version --format '{{.Server.Version}}'
docker info --format '{{.SecurityOptions}}'
pytest -q tests/fault/capability/test_phase21_capability_attack_conformance.py tests/fault/agent/test_phase21_crash_recovery_matrix.py -p no:cacheprovider
pytest -q tests/capability/test_capability_skill_layer.py tests/agent/dag/test_phase17_dispatch_commit.py tests/agent/dag/test_phase17_parallel_recovery.py tests/agent/dag/test_phase17_readyset_admission.py -p no:cacheprovider
pytest -q tests/agent/runtime/test_runtime_restart_persistence.py tests/agent/runtime/test_runtime_interrupt_resume.py tests/agent/runtime/test_runtime_real_execution.py -p no:cacheprovider
pytest -q tests/fault/security/test_phase05_security_pre_effect_faults.py tests/fault/security/test_phase05_security_sink_fail_closed.py tests/security/test_phase05_security_eval_gate.py -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py -k "tool_approval or security_approval_facts or approval_replay or approval_resume" -p no:cacheprovider
pytest -q tests/e2e/test_unified_agent_product_scenario.py tests/fault/capability/test_phase21_capability_attack_conformance.py tests/fault/agent/test_phase21_crash_recovery_matrix.py tests/knowledge/test_ingestion_delete_restore.py tests/api/test_goal03_product_route.py tests/api/test_completion_unified_runtime.py tests/api/test_workspace_task_runtime.py tests/repo/test_goal03_wave_a_migration_contract.py -k "tool_approval or security_approval_facts or approval_replay or answers_from_ingested_index_with_citations or canaries_phase08_cutover_from_product_entry or workspace_task_runtime_links_task_events_artifact_and_feedback or unified_agent_product_scenario_exposes_artifact_trace_and_runtime_recovery or goal03_product_runtime_request_route_rejects_rollback_before_service or goal03_product_service_rejects_rollback_before_database_write or completion_cutover_mode_resolution_supports_explicit_modes or completion_route_uses_legacy_runtime_in_rollback_window or test_phase21_capability_attack_route_ignores_prompt_injection_and_hides_denied_capability or test_phase21_capability_conformance_blocks_cross_workspace_exposure or test_phase21_crash_matrix_reconciles_domain_checkpoint_and_resends_committed_outbox or test_phase21_crash_matrix_reduces_persisted_result_and_rejects_late_epoch or test_ingestion_delete_restore or test_legal_hold_blocks_physical_delete_but_restore_does_not_restore_authorization or test_goal04_product_command_submission_exposes_payload_json_alias" -p no:cacheprovider
pytest -q tests/tools/test_launcher_scripts.py -p no:cacheprovider
docker compose -f infra/docker/docker-compose.yml build frontend
pytest -q tests/api/test_workspace_task_runtime.py tests/api/test_workspace_runtime_recovery.py tests/api/test_knowledge_api_contract.py tests/agent/test_agentic_retrieval_runtime.py tests/agent/test_knowledge_graphrag_runtime_contracts.py tests/retrieval/test_retrieval_planner.py -p no:cacheprovider
```

## Result

```text
29.4.0
[name=seccomp,profile=builtin name=cgroupns]
5 passed
20 passed
7 passed
6 passed
23 passed
22 passed
docker compose build frontend: built docker-frontend:latest
58 passed
```

未完成的完整 Web stack / browser smoke：

```text
powershell -NoProfile -ExecutionPolicy Bypass -File tools/scripts/run-full-e2e-smoke.ps1
cmd /c tools\launchers\windows\_Zuno-Web-Common.cmd start
```

第一次 `run-full-e2e-smoke.ps1` 阻塞在 `http://127.0.0.1:7860/health`，因为后端未启动。修复前端 Docker build 后再次启动 Web stack，已越过 frontend build 阻断，但 backend/worker build 阻塞在 Docker Hub `python:3.12-bookworm` metadata 请求 `EOF` / TLS handshake timeout。该结果不作为 full E2E 通过证据。

## Boundary

本切片只证明 Capability / Agent / Workspace approval / Knowledge retrieval 四条默认路径的攻击面约束、crash 恢复语义、旧授权重放拒绝、产品模式优先级和 Docker frontend build 继续可执行。PHASE21 其余完整 Web stack / browser smoke、Desktop、Load/Soak、Canary/Cutover 与 PHASE22 cleanup 仍待完成。

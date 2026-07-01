# PHASE02 Shared Contract Freeze

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE02_shared-contract-freeze
status: completed

## 目标

在并行实现前冻结共享契约，避免多个 workstream 同时改 `AgentRun`、`ContextPack`、`RetrievalProfile`、`KnowledgeSpaceConfig`、`CapabilityPolicy`、`PlanStep`、scenario summary、trace / eval / cost metric 等核心对象造成冲突。

## 范围

- 定义或确认 `AgentRun`、`ContextPack`、`RetrievalProfile`、`RetrievalDecision`、`EvidenceBundle`、`CitationLineage`。
- 定义或确认输入层 shared contracts：`FileInputFormat`、`SourceObject`、`BinarySourceObject`、`ObjectStoreRef`、`ObjectStoreResult`、`ParserCapabilityStatus`、`ParserDependencyProbe`、`FileIngestionStatus`。
- 定义或确认 worker / queue contracts：`ParserWorkerSpec`、`ParserWorkerResult`、`ParseJobStatus`、`ParseAttempt`、`IndexWorkerSpec`、`IndexWorkerResult`、`QueueMessage`、`QueueBackendResult`、`OutboxEvent`、`DeadLetterRecord`、`ReconcilerFinding`。
- 定义或确认 OCR / VLM derived enrichment contract：`OCRVLMEnrichmentResult`，必须包含 confidence、model_id、prompt_version、derived_from、review_required、privacy_gate、budget_gate 和 blocked / target-blocked 状态。
- 定义或确认 `KnowledgeSpaceConfig`、`ChangeImpactPreview`、file-level status summary、knowledge profile request / response summary。
- 定义或确认 `CapabilityCard`、`CapabilityPolicy`、`CapabilityRiskProfile`、`CapabilityAuditEvent`、`SkillCard`、`ToolCard`、MCP capability、output contract、eval rubric。
- 定义或确认 `PlanStep`、`PlanState`、`StrategySelectorOutput`、`ReflectionVerdict`、`ReplanDecision`、`ReflexionLesson`。
- 定义或确认 `TraceRecord`、`TraceMetric`、`CostMetric`、model call metric 和 release baseline metric。
- 定义或确认 `ConversationRunMetrics`、`StageMetrics`、`IngestionMetrics`、`RetrievalMetrics`、`PlanningMetrics`、`SecurityMetrics`、`EvalComparisonReport`。
- 定义或确认 `ScenarioSummary` / `TraceSummary` fixture contract，用于 PHASE12 用户可感知 E2E evidence。

## 目标架构拼接点

本 phase 是所有层之间的“接口冻结层”。最终目标架构能拼起来，靠的是这些 contract 让各层只依赖稳定语义，而不是互相读内部实现：

- Knowledge 输出 `EvidenceBundle` 和 `CitationLineage` 给 Planning / Reflection / Output Gate。
- Input / Async Infrastructure 输出 `SourceObject`、`ObjectStoreRef`、`FileIngestionStatus`、`ParseJobStatus`、`ParserWorkerResult`、`IndexWorkerResult`、`OutboxEvent`、`DeadLetterRecord` 和 `ReconcilerFinding` 给 Product Surface、Knowledge、E2E 和 Eval。
- Memory 输出 `ContextPack` 给 Planning。
- Product Surface 输出 `KnowledgeSpaceConfig`、`ChangeImpactPreview` 和 file status summary 给 API / Frontend / E2E。
- Capability 输出 `CapabilityPolicy`、`CapabilityRiskProfile`、`CapabilityAuditEvent`、`SkillCard`、`ToolCard` 和 allowed capability summary 给 Planning。
- Security 输出 gate verdict 给 Planning 和 Tool runtime。
- Model Gateway 输出 cost / latency / token metrics 给 Eval。
- Planning 输出 plan / replan / reflexion events 给 Trace / Eval。
- Eval 输出 `ConversationRunMetrics`、`StageMetrics`、`IngestionMetrics`、`RetrievalMetrics`、`PlanningMetrics`、`SecurityMetrics`、`EvalComparisonReport` 给 release gate。
- E2E 输出 `ScenarioSummary` / `TraceSummary`，给 PHASE13 benchmark 和 PHASE15 closure summary。

PHASE02 完成后，后续 workstream 不允许随意发明第二套 file status、queue message、worker result、OCR / VLM result、plan、evidence、skill、trace 或 metrics 字段。

PHASE11 的 `KnowledgeSpaceConfig` / `ChangeImpactPreview`、PHASE06 的 `CapabilityPolicy` 系列、PHASE13 的 per conversation / per stage metrics、PHASE12 的 scenario summary / trace summary fixture 都必须先在本 phase 冻结，再允许各 workstream 实现。

PHASE03 的 `FileInputFormat`、`BinarySourceObject`、`QueueMessage`、`ParserWorkerResult`、`IndexWorkerResult`、`OutboxEvent`、`DeadLetterRecord`、`ReconcilerFinding` 和 `OCRVLMEnrichmentResult` 也必须先在本 phase 冻结；PHASE03、PHASE11、PHASE12、PHASE13 不得自行发明第二套文件状态、队列消息、worker result、OCR / VLM result 或 metrics schema。

## Shared Contract Index

机器可验证入口是 `src/backend/zuno/agent/contracts.py` 的 `PHASE02_SHARED_CONTRACTS`。下表由该索引生成，后续 workstream 需要新增、改名或改变字段语义时必须回 Coordinator；不得在各自目录里发明第二套同义 schema。

| Contract | Owner | Canonical freeze path | Serialization | Frozen fields / enum values | Consuming phases |
|---|---|---|---|---|---|
| `AgentRun` | Workstream F | `src/backend/zuno/agent/contracts.py` | pydantic | `run_id, task_id, session_id, workspace_id, user_id, state, strategy, selected_skill, trace_id` | PHASE09, PHASE10, PHASE12, PHASE13 |
| `ContextPack` | Workstream C | `src/backend/zuno/agent/contracts.py` | pydantic | `context_pack_id, user_goal, task_state, selected_memory_refs, selected_evidence_refs, allowed_capabilities, safety_policy, output_contract, budget` | PHASE05, PHASE09, PHASE10, PHASE12 |
| `RetrievalProfile` | Workstream B | `src/backend/zuno/agent/contracts.py` | enum | `standard, deep, deep_without_graph` | PHASE04, PHASE09, PHASE11, PHASE12 |
| `RetrievalDecision` | Workstream B | `src/backend/zuno/agent/contracts.py` | pydantic | `requested_profile, effective_profile, fallback_reason, retrievers_used, evidence_count, citation_coverage, trace_id` | PHASE04, PHASE09, PHASE12, PHASE13 |
| `EvidenceBundle` | Workstream B | `src/backend/zuno/agent/contracts.py` | pydantic | `evidence_ids, citation_ids, evidence_count, citation_coverage, unsupported_claim_inputs, acl_scopes` | PHASE04, PHASE10, PHASE12, PHASE13 |
| `CitationLineage` | Workstream B | `src/backend/zuno/agent/contracts.py` | pydantic | `citation_id, source_object_id, document_version_id, block_id, parse_job_id, parse_attempt_id, source_sha256, source_span` | PHASE04, PHASE11, PHASE12 |
| `FileInputFormat` | Workstream A | `src/backend/zuno/agent/contracts.py` | enum | `text, markdown, csv, json, html, code, pdf, office, image, scanned, binary, unknown` | PHASE03, PHASE11, PHASE12 |
| `SourceObject` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `source_id, workspace_id, filename, declared_format, mime_type, object_ref, acl_scope, sensitivity_tags` | PHASE03, PHASE11, PHASE12 |
| `BinarySourceObject` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `source_id, workspace_id, filename, declared_format, mime_type, object_ref, acl_scope, sensitivity_tags, bytes_verified, parser_dependency_probe` | PHASE03, PHASE12, PHASE13 |
| `ObjectStoreRef` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `storage_uri, source_sha256, content_type, size_bytes` | PHASE03, PHASE12 |
| `ObjectStoreResult` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `ok, object_ref, diagnostics` | PHASE03, PHASE12 |
| `ParserCapabilityStatus` | Workstream A | `src/backend/zuno/agent/contracts.py` | enum | `current, fallback_current, target_blocked, disabled, unknown_needs_test` | PHASE03, PHASE11 |
| `ParserDependencyProbe` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `provider_id, capability, status, blocked_reason, diagnostics` | PHASE03, PHASE11, PHASE12, PHASE13 |
| `ParserWorkerSpec` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `worker_id, parser_id, supported_formats, dependency_probe, max_attempts` | PHASE03 |
| `ParserWorkerResult` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `parse_job_id, status, document_version_id, parse_attempt, blocked_reason, diagnostics` | PHASE03, PHASE12, PHASE13 |
| `ParseJobStatus` | Workstream A | `src/backend/zuno/agent/contracts.py` | enum | `accepted, queued, running, succeeded, failed, blocked, retrying, cancelled, dead_letter` | PHASE03, PHASE11, PHASE12 |
| `ParseAttempt` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `parse_attempt_id, parse_job_id, attempt, status, started_at, finished_at, diagnostics` | PHASE03, PHASE12 |
| `IndexWorkerSpec` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `worker_id, index_targets, max_attempts` | PHASE03 |
| `IndexWorkerResult` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `index_job_id, status, index_manifest_id, chunk_count, blocked_reason, diagnostics` | PHASE03, PHASE12, PHASE13 |
| `QueueMessage` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `message_id, topic, payload, idempotency_key, status, attempt, trace_id` | PHASE03, PHASE12, PHASE13 |
| `QueueBackendResult` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `ok, message_id, status, dependency_probe, error` | PHASE03, PHASE12 |
| `OutboxEvent` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `event_id, aggregate_id, topic, payload, published` | PHASE03, PHASE12 |
| `DeadLetterRecord` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `dead_letter_id, source_message_id, reason, retryable, payload` | PHASE03, PHASE12, PHASE13 |
| `ReconcilerFinding` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `finding_id, finding_type, severity, entity_id, recommended_action, details` | PHASE03, PHASE12, PHASE13 |
| `OCRVLMEnrichmentResult` | Workstream A | `src/backend/zuno/agent/contracts.py` | pydantic | `status, confidence, model_id, prompt_version, derived_from, review_required, privacy_gate, budget_gate, blocked_reason` | PHASE03, PHASE12, PHASE13 |
| `KnowledgeSpaceConfig` | Coordinator | `src/backend/zuno/agent/contracts.py` | pydantic | `name, workspace_id, description, acl_scope, default_sensitivity, index_capabilities, parser_config, chunk_config, embedding_config, graph_config, ocr_vlm_config, retrieval_defaults, security_policy` | PHASE11, PHASE12, PHASE14 |
| `FileIngestionStatus` | Coordinator | `src/backend/zuno/agent/contracts.py` | pydantic | `file_id, parse_status, index_status, status_timeline, blocked_reason, dependency_probe, retry_count, last_error` | PHASE11, PHASE12, PHASE13 |
| `ChangeImpactPreview` | Coordinator | `src/backend/zuno/agent/contracts.py` | pydantic | `change_type, triggered_action, affected_file_count, affected_chunk_count, affects_existing_artifacts, requires_external_provider, may_create_blocked_state, estimated_duration_ms` | PHASE11, PHASE14 |
| `CapabilityCard` | Workstream D | `src/backend/zuno/agent/contracts.py` | pydantic | `capability_id, capability_type, description, policy, risk_profile, metadata` | PHASE06, PHASE09, PHASE10 |
| `CapabilityPolicy` | Workstream D | `src/backend/zuno/agent/contracts.py` | pydantic | `capability_id, capability_type, workspace_scope, required_roles, approval_required, side_effect_level, network_policy, credential_policy, data_access_policy, audit_policy` | PHASE06, PHASE07, PHASE10 |
| `CapabilityRiskProfile` | Workstream D | `src/backend/zuno/agent/contracts.py` | pydantic | `read_only, write_workspace, external_write, network_access, credential_access, code_execution, browser_control` | PHASE06, PHASE07 |
| `CapabilityAuditEvent` | Workstream D | `src/backend/zuno/agent/contracts.py` | pydantic | `capability_id, task_id, decision, reason, latency_ms, error, approval_id` | PHASE06, PHASE07, PHASE13 |
| `SkillCard` | Workstream D | `src/backend/zuno/agent/contracts.py` | pydantic | `skill_id, skill_version, when_to_use, task_type, recommended_retrieval_profile, required_evidence, allowed_tools, memory_scopes, output_contract, safety_policy, eval_rubric, max_steps, reflection_policy` | PHASE06, PHASE09, PHASE10, PHASE12 |
| `ToolCard` | Workstream D | `src/backend/zuno/agent/contracts.py` | pydantic | `tool_id, capability_id, input_schema, output_schema, permission, trace_fields` | PHASE06, PHASE07, PHASE10 |
| `PlanStep` | Workstream F | `src/backend/zuno/agent/contracts.py` | pydantic | `step_id, goal, action_type, required_evidence, allowed_capabilities, failure_conditions, budget` | PHASE09, PHASE10, PHASE12, PHASE13 |
| `PlanState` | Workstream F | `src/backend/zuno/agent/contracts.py` | pydantic | `plan_id, status, steps, current_step_id` | PHASE09, PHASE10, PHASE12 |
| `StrategySelectorOutput` | Workstream F | `src/backend/zuno/agent/contracts.py` | pydantic | `strategy, reason, selected_skill, retrieval_profile` | PHASE09, PHASE10, PHASE13 |
| `ReflectionVerdict` | Workstream F | `src/backend/zuno/agent/contracts.py` | pydantic | `decision, evidence_enough, citation_coverage, unsupported_claims, security_blocked, reason` | PHASE09, PHASE10, PHASE12, PHASE13 |
| `ReplanDecision` | Workstream F | `src/backend/zuno/agent/contracts.py` | pydantic | `trigger, replaced_step_ids, new_steps, reason` | PHASE09, PHASE10, PHASE12 |
| `ReflexionLesson` | Workstream C | `src/backend/zuno/agent/contracts.py` | pydantic | `lesson_id, task_type, failure_type, root_cause, lesson, recommended_fix, trigger_condition, evidence_refs, scope, safety_label, review_status, expiry` | PHASE05, PHASE10, PHASE13 |
| `TraceRecord` | Workstream G | `src/backend/zuno/agent/contracts.py` | pydantic | `event_id, task_id, trace_id, event_type, payload` | PHASE08, PHASE10, PHASE12, PHASE13 |
| `TraceMetric` | Workstream G | `src/backend/zuno/agent/contracts.py` | pydantic | `name, value, unit, trace_event_ids` | PHASE08, PHASE13 |
| `CostMetric` | Workstream G | `src/backend/zuno/agent/contracts.py` | pydantic | `model_id, token_count, cost_estimate, latency_ms, retry_count, timeout_count` | PHASE08, PHASE13 |
| `ConversationRunMetrics` | Workstream G | `src/backend/zuno/agent/contracts.py` | pydantic | `task_id, session_id, workspace_id, user_id, selected_knowledge_spaces, retrieval_profiles, selected_skill, strategy, model_settings, started_at, ended_at` | PHASE13, PHASE15 |
| `StageMetrics` | Workstream G | `src/backend/zuno/agent/contracts.py` | pydantic | `stage_name, latency_ms, token_count, cost_estimate, model_id, error_count, retry_count, security_block_count, trace_event_ids` | PHASE08, PHASE13 |
| `IngestionMetrics` | Workstream G | `src/backend/zuno/agent/contracts.py` | pydantic | `files_uploaded, files_indexed, files_failed, files_blocked, parse_duration_ms, index_duration_ms, parser_id, parser_format, dependency_status, blocked_reason, retry_count, dead_letter_count, reconciler_findings, ocr_vlm_pages, ocr_vlm_cost_estimate, binary_bytes_processed` | PHASE03, PHASE13 |
| `RetrievalMetrics` | Workstream G | `src/backend/zuno/agent/contracts.py` | pydantic | `retrieval_rounds, retrievers_used, candidate_count, reranked_count, evidence_count, citation_count, citation_coverage, source_span_accuracy` | PHASE04, PHASE13 |
| `PlanningMetrics` | Workstream G | `src/backend/zuno/agent/contracts.py` | pydantic | `plan_step_count, strategy, skill_selected, replan_count, reflection_count, reflexion_count, replan_reason` | PHASE09, PHASE10, PHASE13 |
| `SecurityMetrics` | Workstream G | `src/backend/zuno/agent/contracts.py` | pydantic | `input_blocks, retrieval_acl_denied, tool_approval_required, output_dlp_blocks, prompt_injection_flags` | PHASE07, PHASE13 |
| `EvalComparisonReport` | Workstream G | `src/backend/zuno/agent/contracts.py` | pydantic | `baseline_label, quality_delta, latency_delta, cost_delta, citation_delta, security_delta` | PHASE13, PHASE15 |
| `ScenarioSummary` | Coordinator | `src/backend/zuno/agent/contracts.py` | pydantic | `user_question, selected_knowledge_spaces, retrieval_profiles, selected_skill, plan_summary, retrieval_decision, reflection_verdict, replan_event, artifact_content_excerpt, citations, metrics_summary, feedback_result, restart_rehydrate_result, file_status_timeline, parser_dependency_probe, blocked_reason, worker_event, index_status, citation_lineage` | PHASE12, PHASE13, PHASE15 |
| `TraceSummary` | Workstream G | `src/backend/zuno/agent/contracts.py` | pydantic | `trace_id, events, metrics, cost_summary` | PHASE12, PHASE13, PHASE15 |

## 并行开发可行性

本 phase 主要串行，最多允许只读 review 并行。原因是 contract 文件属于高耦合共享面。

可并行：

- Workstream B/C/D/E/F/G 各自提出字段需求。
- Coordinator 汇总字段，做最小公共 contract。

不可并行：

- 多个 agent 同时编辑同一个 contract 文件。
- 在 runtime 实现中临时新增未登记字段。
- 跳过 PHASE02 直接实现 PHASE03-PHASE13。

## 详细执行卡

- 输入依赖：PHASE01 owner map、现有 DTO / storage / agent / knowledge contracts、workspace API schema、trace/eval 字段现状。
- 主要交付物：共享 contract 文件、contract tests、兼容说明、后续 workstream 不得擅自改动的冻结字段清单。
- 可并行工作包：只读 review 可并行；实际 contract 文件只能单 owner 编辑。各 workstream 可以提交 contract request，但不能直接改共享 schema。
- Coordinator 锁点：AgentRun、ContextPack、RetrievalProfile、EvidenceBundle、KnowledgeSpaceConfig、ChangeImpactPreview、CapabilityPolicy、SkillCard、PlanState、ConversationRunMetrics、StageMetrics、ScenarioSummary、TraceMetric、Workspace API DTO。
- 下游交接：PHASE03 需要 input format、binary object、object ref、queue message、worker result、outbox、dead letter、reconciler、OCR / VLM enrichment 和 status contracts；PHASE04 需要 retrieval/evidence contracts；PHASE05 需要 ContextPack；PHASE06 需要 CapabilityPolicy / CapabilityRiskProfile / SkillCard；PHASE09 需要 Plan/Replan/Reflection contracts；PHASE11 需要 KnowledgeSpaceConfig / ChangeImpactPreview / FileIngestionStatus；PHASE12 需要 ScenarioSummary / TraceSummary；PHASE13 需要 ConversationRunMetrics / StageMetrics / RetrievalMetrics / PlanningMetrics / SecurityMetrics / EvalComparisonReport / IngestionMetrics。
- PR / commit 建议：`feat(contracts): freeze agentic graphrag shared runtime contracts`，必须先过 contract tests 再允许并行实现。

## 禁止范围

- 不在本 phase 大改 `GeneralAgent` 主循环。
- 不让各 workstream 自行新增不兼容 contract 字段。
- 不把 contract-only 写成 runtime completion。

## 验收闸门

- 共享契约文件位置明确，字段命名稳定。
- focused contract tests 覆盖序列化、默认值、枚举值和 backward-compatible parse。
- `FileInputFormat`、`SourceObject`、`BinarySourceObject`、`ObjectStoreRef`、`ObjectStoreResult`、`ParserCapabilityStatus`、`ParserDependencyProbe`、`ParserWorkerSpec`、`ParserWorkerResult`、`ParseJobStatus`、`ParseAttempt`、`IndexWorkerSpec`、`IndexWorkerResult`、`QueueMessage`、`QueueBackendResult`、`OutboxEvent`、`DeadLetterRecord`、`ReconcilerFinding`、`OCRVLMEnrichmentResult`、`KnowledgeSpaceConfig`、`FileIngestionStatus`、`ChangeImpactPreview`、`CapabilityPolicy`、`CapabilityRiskProfile`、`CapabilityAuditEvent`、`ConversationRunMetrics`、`StageMetrics`、`IngestionMetrics`、`RetrievalMetrics`、`PlanningMetrics`、`SecurityMetrics`、`EvalComparisonReport`、`ScenarioSummary` 和 `TraceSummary` 均在 shared contract map 中有唯一 owner。
- 后续 workstream 修改 shared contract 必须经 Coordinator 审查。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent tests/knowledge tests/evals -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
```

## 需要先读取

- `src/backend/zuno/agent/**`
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/capability/**`
- `src/backend/zuno/memory/**`
- `src/backend/zuno/platform/observability/**`
- `tests/agent/**`
- `tests/knowledge/**`
- `tests/evals/**`

## 需要修改的文件

- `src/backend/zuno/agent/contracts.py` or existing equivalent
- `src/backend/zuno/agent/planning/contracts.py` if introduced
- `src/backend/zuno/capability/contracts.py`
- `src/backend/zuno/knowledge/retrieval/contracts.py` or existing equivalent
- `src/backend/zuno/platform/observability/contracts.py` or existing equivalent
- focused contract tests

## 执行拆解

1. 盘点现有 contract 和 DTO，避免重复定义。
2. 写 failing contract tests。
3. 增补最小 dataclass / pydantic / protocol contract。
4. 跑 focused tests。
5. 生成 shared contract map，供 PHASE03-PHASE13 使用。

## 多 agent 分工

- Coordinator owner。
- Workstream B/C/D/F/G 可只读 review 字段是否满足后续实现。
- 不允许多个 agent 同时编辑 shared contract 文件。

## 需要返回的证据

- contract file list。
- focused tests。
- 字段兼容性说明。
- 哪些 contract 被标为 frozen。

## Closure Evidence

- Contract file list：`src/backend/zuno/agent/contracts.py`、`tests/agent/test_shared_contract_freeze.py`、本文件的 `Shared Contract Index`。
- Frozen contracts：`PHASE02_SHARED_CONTRACTS` 中登记的 52 个 contract，覆盖 AgentRun、ContextPack、RetrievalProfile、input / queue / worker / capability / planning / trace / metrics / scenario summary。
- 字段兼容性说明：用户可见检索 profile 只冻结 `standard` / `deep`，`deep_without_graph` 仅为内部 fallback；`basic/local/global/drift` 仍是内部 eval / legacy / GraphRAG method，不进入产品主选择。
- Focused tests：`pytest -q tests/agent/test_shared_contract_freeze.py -p no:cacheprovider` 通过，`2 passed`。
- Broader validation：`pytest -q tests/agent/test_shared_contract_freeze.py tests/agent tests/knowledge tests/evals -p no:cacheprovider` 通过，`367 passed, 3 warnings`。
- Verifier：`git diff --check`、`python tools/agent/render_architecture.py --check`、`python tools/scripts/verify_docs_entrypoints.py`、`python tools/scripts/verify_repo_structure.py`、`python .agent/scripts/verify_agent_system.py`、`python .agent/scripts/verify_doc_boundaries.py`、`powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1` 均通过；测试产生的 `.local/` 与 `.test-tmp/` 已按仓库卫生规则清理。

## 停止条件

- 发现现有 API contract 与计划字段冲突且不能兼容。
- 需要 DB migration 或 frontend breaking change 才能冻结 contract。
- 多个 workstream 对同一字段含义无法收敛。

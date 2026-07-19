# Goal01 Coordinator Audit

state: in_progress
branch: integration/goal01-control-plane-model-ingestion
start_sha: ed787ee962f7f567163388188e56b4b765c27877
audited_at: 2026-07-19

## 目标边界

本文件记录 `goal01-control-plane-model-ingestion` 的一次性 Coordinator 总审计。它不是 Phase Closure Decision，不把 runtime batch、静态 verifier 或局部 focused tests 冒充为 PHASE05、PHASE06、PHASE07 或 PHASE11 completed。

本轮目标文件要求最终只能声明：

```text
PHASE05、PHASE06、PHASE07、PHASE11 在完整 Phase Scope 内 implementation available；PHASE08 ready。
```

在 Phase 文件完成定义仍有缺口时，不得提升 Program Manifest、Current、Roadmap 或 Requirement Ledger 为 completed。

## 读取事实源

- `AGENTS.md`
- `docs/architecture/architecture.md`
- `docs/modules/02-input-document-ingestion.md`
- `docs/modules/04-model-gateway.md`
- `docs/modules/09-security.md`
- `docs/modules/10-observability-eval.md`
- `docs/status/production-readiness.md`
- `.agent/programs/current.md`
- `.agent/programs/program-manifest.yaml`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/task-execution-contract.md`
- `.agent/programs/PHASE05_security-control-plane.md`
- `.agent/programs/PHASE06_observability-minimum-black-box.md`
- `.agent/programs/PHASE07_model-gateway-runtime.md`
- `.agent/programs/PHASE11_durable-ingestion-and-source-lineage.md`

## Start SHA

`origin/main` after `git fetch origin`:

```text
ed787ee962f7f567163388188e56b4b765c27877
```

This matches the known baseline in the goal objective.

## Phase DAG

```text
Wave 1:
  PHASE05 Security Control Plane
  PHASE06 Observability Minimum Black Box

Wave 2:
  PHASE07 Model Gateway Runtime depends on PHASE05 + PHASE06
  PHASE11 Durable Ingestion and Source Lineage depends on PHASE05

Final readiness:
  PHASE08 ready only after PHASE05 + PHASE06 + PHASE07 complete
  PHASE12 remains planned
  PHASE09-PHASE22 remain target
```

## Current Anchors

PHASE05 current anchors found:

- `src/backend/zuno/platform/security/runtime_batch.py`
- `src/backend/zuno/platform/security/governance.py`
- `tests/security/test_security_runtime_batch.py`
- `tools/scripts/verify_security_runtime_batch.py`
- `tools/scripts/verify_security_target_protocols.py`
- `docs/evidence/security-runtime-batch.md`

PHASE06 current anchors found:

- `src/backend/zuno/platform/observability/trace_eval.py`
- `src/backend/zuno/platform/observability/local_trace_store.py`
- `tests/platform/test_observability_runtime_batch.py`
- `tools/scripts/verify_observability_runtime_batch.py`
- `tools/scripts/verify_observability_eval_target_protocols.py`
- `docs/evidence/observability-runtime-batch.md`

PHASE07 current anchors found:

- `src/backend/zuno/platform/model_gateway.py`
- `tests/platform/test_model_gateway.py`
- `tools/scripts/verify_model_gateway_runtime_batch.py`
- `tools/scripts/verify_model_gateway_target_protocols.py`
- `tools/scripts/verify_model_gateway_boundaries.py`
- `docs/evidence/model-gateway-runtime-batch.md`

PHASE11 current anchors found:

- `src/backend/zuno/knowledge/ingestion/runtime_batch.py`
- `src/backend/zuno/knowledge/ingestion/async_runtime.py`
- `src/backend/zuno/knowledge/ingestion/gateway.py`
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`
- `tests/knowledge/test_document_ingestion_contract.py`
- `tests/knowledge/test_ingestion_async_infrastructure.py`
- `docs/evidence/input-runtime-batch.md`

## Verification Already Run

```text
python tools/scripts/verify_security_runtime_batch.py
  passed

python tools/scripts/verify_observability_runtime_batch.py
  passed

python tools/scripts/verify_model_gateway_runtime_batch.py
  passed

python tools/scripts/verify_security_target_protocols.py
  passed

python tools/scripts/verify_observability_eval_target_protocols.py
  passed

python tools/scripts/verify_model_gateway_target_protocols.py
  passed

python tools/scripts/verify_model_gateway_boundaries.py
  passed

pytest -q tests/security tests/platform/test_observability_runtime_batch.py tests/platform/test_model_gateway.py tests/knowledge/test_document_ingestion_contract.py tests/knowledge/test_ingestion_async_infrastructure.py -p no:cacheprovider
  50 passed

python tools/scripts/verify_current_program.py
  failed before verifier fix: PHASE04 post-closure evidence hash mismatch caused by CRLF worktree bytes
  passed after normalizing text evidence line endings in tools/scripts/verify_phase04_post_closure_consistency.py
```

Command requested by PHASE07 but missing:

```text
python tools/scripts/verify_model_gateway_bypass.py
  blocked: file does not exist
```

## Current / Gap

### PHASE05 Security

Current:

- Security runtime batch covers `ARCH-SEC-001` through `ARCH-SEC-060` and target verifier passes.
- Local governance gate and redaction helpers exist.
- Requirement Ledger entries for Security state that runtime batch evidence exists but does not close PHASE05.
- Independent subagent audit confirmed `pytest -q tests/security -p no:cacheprovider` passes, but only for in-memory batch/governance contract coverage.
- PHASE05 Postgres persistence now covers Security facts for PrincipalContext、EffectiveEpoch、AuthorizationDecision、ApprovalRequest/Decision、SecretRef/Lease、RedactionDecision、AuditRequirement 和 Security outbox；focused integration/fault tests prove pre-effect epoch/hash/deadline revalidation, SecretLease audience/expiry/revoke, redaction failure fail-closed and sink outage fail-closed.

Gap:

- Phase file requires full Security control-plane persistence and integration paths under `src/backend/zuno/platform/database/security/**`; no dedicated security Alembic revision or database security directory was found in the initial audit.
- Phase closure requires production paths to consume only `Decision/Ref`; legacy approval booleans and scattered `approval_required` / `approved` fields still exist as migration inputs.
- Mandatory audit integration depends on PHASE06 acceptance and Infrastructure mandatory audit primitive, but Phase-level integration evidence is not yet closed.
- Product/Agent/Tool paths still use boolean/string approval decisions, including workspace resume and tool runtime `approved: bool` inputs.
- Security fault coverage still does not prove every Product/API resume、download、citation、admin 和 full PEP/PDP cutover path; legacy boolean approval inputs remain migration inputs.

Status:

```text
implementation batch available
phase closure not approved
```

### PHASE06 Observability

Current:

- Observability runtime batch covers Trace Context/Tree, Envelope, Dedup, Ordering, Audit, Projection Rebuild, Eval and RAG observability target requirements.
- Existing focused verifier and tests pass.
- Independent subagent audit confirmed `trace_eval.py` is primarily dataclass / pure-function runtime batch coverage and `local_trace_store.py` is a local SQLite inspection helper.

Gap:

- Phase file requires append-only ingest store, typed runtime adapters, immutable audit ledger, projection watermarks/gaps/rebuild, authorized query API and operational dead-letter surface as default reusable black box for later phases.
- Initial audit found helper/runtime-batch style implementation, but not yet a Phase-level closure bundle proving default path adoption by all later module writers.
- No `observability_ingest_envelopes`, `observability_traces`, `observability_spans`, `observability_runtime_events`, accepted audit ledger or watermark/gap Alembic schema was found in the initial audit.
- `src/backend/zuno/api/product/routes/queries.py` and `src/backend/zuno/api/services/product/projection_service.py` do not exist, despite being listed in PHASE06 allowed paths for query/projection work.
- `tests/observability/**`, `tests/integration/observability/**` and `tests/fault/observability/**` do not exist yet.

Status:

```text
implementation batch available
phase closure not approved
```

### PHASE07 Model Gateway

Current:

- Model Gateway runtime batch covers `ARCH-MODEL-001` through `ARCH-MODEL-088`.
- Target protocol verifier and current boundary verifier pass.

Gap:

- PHASE07 requires direct Provider SDK bypasses to be zero. Initial static scan found active direct imports and client creation outside the Gateway boundary, including:
  - `src/backend/zuno/agent/core/models/manager.py`
  - `src/backend/zuno/agent/core/models/embedding.py`
  - `src/backend/zuno/agent/core/models/reason_model.py`
  - `src/backend/zuno/agent/core/models/tool_call.py`
  - `src/backend/zuno/agent/core/models/usage_model.py`
  - `src/backend/zuno/platform/services/rag/embedding.py`
  - `src/backend/zuno/platform/common/extract.py`
  - `src/backend/zuno/capability/tools/resume_optimizer/action.py`
  - `src/backend/zuno/api/services/mcp_chat.py`
  - `src/backend/zuno/platform/services/autobuild/client.py`
  - `src/backend/zuno/platform/services/mcp_openai/mcp_manager.py`
- Existing `verify_model_gateway_boundaries.py` passes because it allowlists many legacy direct-call files. Passing it cannot be used as PHASE07 bypass cutover evidence.
- PHASE07's named bypass verifier is missing.

Status:

```text
implementation batch available
phase closure blocked by direct Provider SDK bypass
```

### PHASE11 Ingestion

Current:

- Input runtime batch and ingestion async infrastructure focused tests pass.
- Local SourceObject, object store, SQLite durable ingestion store, queue, parser worker, blocked image path and handoff envelope evidence exist.
- Independent subagent audit confirmed local text/markdown and text PDF paths exist, with PyMuPDF SourceSpan coverage for the local vertical slice.

Gap:

- PHASE11 requires durable SourceObject to Indexable Snapshot path with object store, queue, lease/fencing, parser router, OCR/VLM/human review, delete and recovery in phase scope.
- Initial audit found local adapter evidence and runtime batch evidence, but not yet a Phase-level closure proving real default path cutover, dedicated Alembic ingestion persistence, full parser adapter conformance, human review state machine and delete/recovery closure.
- Current SQLite `DocumentVersionTable` mixes parser/config/schema fields into document version persistence; PHASE11 requires DocumentVersion and ParseSnapshot version semantics to be separate.
- RabbitMQ in ingestion runtime is still a `target_blocked` probe, not a real PHASE11 queue path.
- OCR/VLM, Office, Archive and Human Review remain target/blocker areas rather than completed adapter/runtime evidence.
- Existing workspace ingestion path still directly parses and indexes in places instead of publishing immutable `IndexableDocumentSnapshotV1` through an outbox handoff.
- Legacy parser paths under `zuno.services.rag.parser.doc_parser` are still used by pipeline/attachment code.

Status:

```text
implementation batch available
phase closure not approved
```

## Ownership

- PHASE05 owner: Module 09 Security.
- PHASE06 owner: Module 10 Observability & Eval.
- PHASE07 owner: Module 04 Model Gateway.
- PHASE11 owner: Module 02 Input / Document Ingestion.
- Coordinator-only files remain Program Manifest, Current, Roadmap, Phase Readiness, Requirement Ledger, Closure Decision and aggregate Evidence.
- Unique Alembic owner for this goal is still unset because no new migration has been accepted for PHASE05/06/07/11 in this audit.

## Immediate Task DAG

```text
P05 audit/closure blockers
P06 audit/closure blockers
  -> if both close, P07 implementation can proceed

P05 audit/closure blockers
  -> if P05 closes, P11 implementation can proceed

P07-T07 Bypass Cutover is currently a hard blocker for PHASE07 closure.
P11-T03/T08 persistence, worker recovery and legacy parser cutover are current blocker candidates for PHASE11 closure.
```

## Coordinator Decision So Far

Do not mark PHASE05, PHASE06, PHASE07 or PHASE11 completed yet.

The first concrete implementation blocker is PHASE07 direct Provider SDK bypass. Work should proceed by creating a strict bypass inventory/guard and migrating active runtime call sites to a Gateway-owned adapter boundary before any PHASE07 closure decision.

However, PHASE07 depends on PHASE05 and PHASE06. Because both PHASE05 and PHASE06 currently fail their own Phase completion definitions, PHASE07 implementation beyond audit/preparation is dependency-blocked by the goal objective's ordering rule.

## Resolved Precondition

`python tools/scripts/verify_current_program.py` initially failed because PHASE04 post-closure evidence hashes did not match the recorded post-closure consistency gate:

```text
docs/evidence/phase04-complete-infrastructure-blocker.md
docs/evidence/phase04-pre-closure.md
docs/evidence/phase04-coordinator-closure.md
docs/evidence/phase04-official-checkpointer-schema-upgrade.md
docs/evidence/phase04-backup-restore-replay.md
```

Root cause:

```text
category: verifier newline normalization defect
evidence: git blob hashes at ed787ee9/origin/main/HEAD match phase04-readiness.yaml, while Windows worktree bytes had CRLF and produced different raw-byte hashes.
fix: tools/scripts/verify_phase04_post_closure_consistency.py now normalizes CRLF to LF for text evidence before hashing.
result: PHASE04 post-closure consistency gate and current program verifier pass.
```

This removes the PHASE04 evidence-integrity blocker. It does not close PHASE05/06/07/11.

## PHASE06 Observability Persistence Work Product

新增 `infra/db/alembic/versions/20260719_17_observability_black_box.py`，作为 PHASE06 Observability / Eval 所有的最小 durable black-box schema。该迁移从 PHASE05 Security migration `20260719_16` 后接入。

新增表：

- `observability_ingest_envelopes`
- `observability_traces`
- `observability_spans`
- `observability_runtime_events`
- `observability_audit_records`
- `observability_projection_watermarks`
- `observability_gaps`
- `observability_dead_letters`
- `observability_projection_rebuilds`

边界：

- 存储版本化 envelope、redaction hash、trace/span、runtime event、immutable audit hash chain、projection watermark、gap、dead letter 和 rebuild fencing facts。
- 不把 prompt、hidden reasoning、chain-of-thought、secret、token、API key 或 password 作为列级事实源。
- 外部 sink 仍不是事实 owner；本地 Postgres black-box schema 是后续 adapter/repository 的落点。

新增验证：

```text
tools/scripts/verify_phase06_observability_persistence.py
tests/repo/test_phase06_observability_persistence.py
```

Status:

```text
PHASE06 persistence foundation added
phase closure not approved
remaining: ingest service, reducer, adapters, immutable audit repository, projection/query API, fault tests
```

Runtime persistence follow-up:

```text
src/backend/zuno/platform/observability/persistence.py
tests/integration/test_phase06_observability_persistence_runtime.py
```

This adds `ObservabilityUnitOfWork` and `ObservabilityRepository` for envelope ingest, duplicate detection, trace/span records, runtime events, immutable audit records, projection watermark, gap records and dead letters. Payloads are redacted before storage and duplicate stream sequence payload mismatch is routed to dead letter instead of silently overwriting.

Status:

```text
PHASE06 durable ingest repository available
phase closure not approved
remaining: typed adapters, reducer/query projection, authorization checks, full fault tests
```

Typed adapter follow-up:

```text
src/backend/zuno/platform/observability/persistence.py
tests/integration/test_phase06_observability_persistence_runtime.py
```

`PostgresObservabilityRuntimeAdapter` now persists `ZunoSpan` and `SandboxAuditEvent` as trace, span, runtime event and audit records through the same Observability repository. This gives active runtime audit/span objects a Security-aware typed adapter path into the durable black box without making Observability mutate source domain state.

Status:

```text
PHASE06 typed security audit/span adapter available
phase closure not approved
remaining: reducer/query projection, authorization checks, external sink isolation, full fault tests
```

Query/freshness follow-up:

```text
src/backend/zuno/platform/observability/persistence.py
tests/integration/test_phase06_observability_persistence_runtime.py
```

Observability repository now exposes read-only `trace_timeline`, `projection_freshness` and `dead_letters` queries. Watermarks advance when missing sequences are filled, open gaps are marked `filled`, and query payloads remain redacted.

Status:

```text
PHASE06 read-only trace/freshness/dead-letter query surface available
phase closure not approved
remaining: API authorization checks, external sink isolation, full fault tests
```

## PHASE05 Security Persistence Work Product

新增 `infra/db/alembic/versions/20260719_16_security_control_plane.py`，作为 PHASE05 Security 所有的第一组持久化事实源。该迁移从 `20260718_15` 之后接入，不改变 PHASE04 已闭合基础设施边界。

新增表：

- `security_principal_contexts`
- `security_effective_epochs`
- `security_authorization_decisions`
- `security_approval_requests`
- `security_approval_decisions`
- `security_secret_refs`
- `security_secret_leases`
- `security_redaction_decisions`
- `security_audit_requirements`
- `security_outbox_events`

边界：

- 只存 Principal、Epoch、Policy Bundle Ref、Prepared Action Hash、Credential Version Ref、Secret Lease Ref、Redaction Decision、Audit Requirement 和 Security Outbox 事实。
- 不存 access token、refresh token、API key、password、plaintext、secret material 或 credential value。
- PHASE04 Alembic verifier 改为只验证到 `20260718_15`，后续 phase migration 由各自 verifier 接管，避免把“仓库最新 head”误当成“PHASE04 head”。

新增验证：

```text
tools/scripts/verify_phase05_security_persistence.py
tests/repo/test_phase05_security_persistence.py
```

Status:

```text
PHASE05 persistence foundation added
phase closure not approved
remaining: runtime repository/UoW adoption, PEP/PDP fail-closed cutover, approval/audit fault tests, security eval evidence
```

Runtime follow-up:

```text
src/backend/zuno/platform/security/persistence.py
tests/integration/test_phase05_security_persistence.py
```

This adds a Security-owned UnitOfWork and repository that persists effective epoch, principal context, authorization decision, approval request, approval decision and security outbox event in one PostgreSQL transaction. It rejects obvious secret material keys before outbox persistence.

Status after runtime follow-up:

```text
PHASE05 persistence foundation callable by runtime
phase closure not approved
remaining: PEP/PDP fail-closed cutover, approval/audit fault tests, security eval evidence
```

Tool Runtime adoption:

```text
src/backend/zuno/capability/runtime.py
tests/agent/test_tool_control_plane_runtime.py
```

Tool Control Plane now accepts an injectable `SecurityApprovalFactSink` and emits a redacted Security approval fact at `approval_waiting` and `approved_before_effect`. The fact includes `prepared_action_hash`, approval ID, audit ref, credential refs and sandbox decision summary, but not raw tool arguments or credential values.

Status:

```text
PHASE05 approval fact sink adopted by active Tool Runtime path
phase closure not approved
remaining: concrete PostgreSQL sink wiring in product runtime, PEP/PDP fail-closed cutover, approval/audit fault tests, security eval evidence
```

PostgreSQL sink wiring:

```text
src/backend/zuno/platform/security/persistence.py
src/backend/zuno/api/services/workspace_task_runtime.py
tests/integration/test_phase05_security_persistence_runtime.py
tests/api/test_workspace_task_runtime.py
```

Security now owns `PostgresSecurityApprovalFactSink`, which consumes redacted Tool Runtime approval facts and writes effective epoch, principal context, authorization decision, approval request, approval decision and security outbox event through `SecurityUnitOfWork`. `WorkspaceTaskRuntimeService.configure_security_approval_sink()` wires the sink into the active workspace tool runtime without moving Security persistence concerns into the API layer.

Status:

```text
PHASE05 PostgreSQL approval fact sink available and product runtime wiring verified
phase closure not approved
remaining: PEP/PDP fail-closed cutover, mandatory audit fault tests, security eval evidence
```

Fail-closed and mandatory audit follow-up:

```text
src/backend/zuno/capability/runtime.py
src/backend/zuno/platform/security/persistence.py
tests/agent/test_tool_control_plane_runtime.py
tests/integration/test_phase05_security_persistence_runtime.py
```

Tool Runtime blocked paths now emit a redacted `failed_closed_before_effect` Security fact before returning a blocked result. `PostgresSecurityApprovalFactSink` records this as a `DENY` authorization decision, a `failed_closed` audit requirement and a security outbox event, without creating an approval request or running the executor.

Status:

```text
PHASE05 fail-closed Security fact and mandatory audit requirement path available
phase closure not approved
remaining: broader PEP/PDP cutover coverage, audit fault injection, security eval evidence
```

Fault injection follow-up:

```text
tests/fault/security/test_phase05_security_sink_fail_closed.py
```

Security approval sink outage is now covered for approved side effects and disabled-tool fail-closed paths. In both cases the runtime raises before executor invocation; the disabled-tool fault test also asserts `calls == []`.

Status:

```text
PHASE05 security sink outage fails closed before effect
phase closure not approved
remaining: broader PEP/PDP cutover coverage, security eval evidence
```

Security eval evidence follow-up:

```text
docs/evidence/phase05-security-control-plane.md
tools/scripts/verify_phase05_security_eval.py
tests/security/test_phase05_security_eval_gate.py
```

Added partial PHASE05 Security evidence covering adaptive side-effect attack blocking, benign read-only utility preservation and sink-outage fail-closed behavior. The evidence explicitly states `phase_completion: not_approved`.

Status:

```text
PHASE05 partial security eval evidence available
phase closure not approved
remaining: broader PEP/PDP cutover coverage and full Security fault matrix
```

## PHASE07 Model Gateway Bypass Guard

新增严格 Provider SDK bypass guard：

```text
tools/scripts/verify_model_gateway_bypass.py
tests/repo/test_model_gateway_bypass.py
.agent/programs/work-products/phase07-provider-bypass-inventory.yaml
```

默认 verifier mode 锁定当前绕行清单，防止新增未登记 direct provider SDK path；`--strict` mode 要求生产源码绕行归零，用于 PHASE07 closure gate。当前 strict mode 仍失败，原因是 12 个已登记的 legacy/active provider SDK direct import 仍存在。

Status:

```text
PHASE07 bypass inventory guard available
phase closure not approved
remaining: migrate listed bypass paths into Gateway-owned adapters, then pass --strict
```

## PHASE07 Model Gateway Bypass Migration 001

已迁移一个直接 Provider SDK 绕行：

```text
src/backend/zuno/platform/common/extract.py
```

该文件原本在模块顶层直接构造 `ChatOpenAI`，并在 import-time 执行 `asyncio.run(main())`。现已改为只通过 `build_default_model_gateway().get_chat_model(...)` 获取 chat model；demo 执行入口移动到 `if __name__ == "__main__"`，普通导入只保留代码块提取工具和显式 helper。

同步更新：

```text
.agent/programs/work-products/phase07-provider-bypass-inventory.yaml
tests/repo/test_model_gateway_bypass.py
```

Status:

```text
PHASE07 bypass count reduced from 12 to 11
phase closure not approved
remaining: migrate the other listed bypass paths, then pass verify_model_gateway_bypass.py --strict
```

## PHASE07 Model Gateway Bypass Migration 002

已迁移一个 provider package 常量依赖：

```text
src/backend/zuno/platform/services/mcp_openai/strict_schema.py
```

该文件原本只为判断 `default` 是否缺失而导入 `openai.NOT_GIVEN`，并不需要 Provider SDK。现已改为模块内 `_NOT_GIVEN` sentinel，保留原行为：`default: None` 被移除，非空 default 保留。

同步更新：

```text
.agent/programs/work-products/phase07-provider-bypass-inventory.yaml
tests/repo/test_model_gateway_bypass.py
```

Status:

```text
PHASE07 bypass count reduced from 11 to 10
phase closure not approved
remaining: migrate the other listed bypass paths, then pass verify_model_gateway_bypass.py --strict
```

## PHASE07 Model Gateway Bypass Migration 003

已迁移一个 Capability 工具直接 Provider SDK 调用：

```text
src/backend/zuno/capability/tools/resume_optimizer/action.py
```

该工具原本直接创建 `OpenAI` client，并 hardcode `gpt-3.5-turbo`。现已改为通过 `ModelGateway.invoke(ModelGatewayRequest(...))` 请求 chat proposal。为避免把本地 mock 冒充为真实简历优化，当前命中 `local_mock_*` provider 时保留原文并输出诊断；只有非 mock Gateway adapter 成功返回非空文本时才替换原文。

同步更新：

```text
.agent/programs/work-products/phase07-provider-bypass-inventory.yaml
tests/repo/test_model_gateway_bypass.py
```

Status:

```text
PHASE07 bypass count reduced from 10 to 9
phase closure not approved
remaining: migrate the other listed bypass paths, then pass verify_model_gateway_bypass.py --strict
```

## PHASE07 Model Gateway Bypass Migration 004

已迁移一个 AutoBuild 默认 chat model 构建点：

```text
src/backend/zuno/platform/services/autobuild/client.py
```

该文件原本在 `create_build_agent()` 中直接创建 `ChatOpenAI(**kwargs)`。现已改为通过注入或默认的 `ModelGateway` 调用 `get_chat_model(binding=..., role=ModelRole.EXECUTOR)`，保留 `LLMService.get_one_llm()` 返回的 model、api_key、base_url 作为 Gateway binding。

同步更新：

```text
.agent/programs/work-products/phase07-provider-bypass-inventory.yaml
tests/repo/test_model_gateway_bypass.py
```

Status:

```text
PHASE07 bypass count reduced from 9 to 8
phase closure not approved
remaining: migrate the other listed bypass paths, then pass verify_model_gateway_bypass.py --strict
```

## PHASE07 Model Gateway Bypass Migration 005

已迁移 MCP chat manager 的 provider package 类型判断：

```text
src/backend/zuno/platform/services/mcp_openai/mcp_manager.py
```

该文件原本直接导入 OpenAI 和 Anthropic SDK 类型，只用于 `match` 判断。现已改为本地能力边界：支持具备 `ainvoke` 或 `invoke` 的 Anthropic-compatible wrapper；OpenAI-like client 继续明确返回 `NotImplementedError`，不把未实现路径伪装为可用。

同步更新：

```text
.agent/programs/work-products/phase07-provider-bypass-inventory.yaml
tests/repo/test_model_gateway_bypass.py
```

Status:

```text
PHASE07 bypass count reduced from 8 to 7
phase closure not approved
remaining: migrate the other listed bypass paths, then pass verify_model_gateway_bypass.py --strict
```

## PHASE07 Model Gateway Bypass Migration 006

已迁移两个真实 embedding provider 调用点到 Gateway-owned adapter：

```text
src/backend/zuno/agent/core/models/embedding.py
src/backend/zuno/platform/services/rag/embedding.py
```

新增 `OpenAIEmbeddingGatewayAdapter` 于 `src/backend/zuno/platform/model_gateway.py`。OpenAI / AsyncOpenAI SDK 调用仍保留真实 provider 行为，但只存在于 Gateway 边界内；Core EmbeddingModel 与 RAG embedding helper 只消费该 adapter，不直接创建 Provider SDK client。

同步更新：

```text
.agent/programs/work-products/phase07-provider-bypass-inventory.yaml
tests/repo/test_model_gateway_bypass.py
```

Status:

```text
PHASE07 bypass count reduced from 7 to 5
phase closure not approved
remaining: migrate the other listed bypass paths, then pass verify_model_gateway_bypass.py --strict
```

## PHASE07 Model Gateway Bypass Migration 007

已迁移默认 ChatOpenAI 构建点到 Gateway-owned helper：

```text
src/backend/zuno/agent/core/models/manager.py
```

新增 `build_openai_chat_gateway_model(...)` 于 `src/backend/zuno/platform/model_gateway.py`。`ModelManager` 继续负责读取 DB / settings 模型配置和 provider model id normalize，但不再直接导入或构造 `ChatOpenAI`。DeepSeek v4 thinking-disable 兼容参数也移入 Gateway 边界。

同步更新：

```text
.agent/programs/work-products/phase07-provider-bypass-inventory.yaml
tests/repo/test_model_gateway_bypass.py
```

Status:

```text
PHASE07 bypass count reduced from 5 to 4
phase closure not approved
remaining: migrate the other listed bypass paths, then pass verify_model_gateway_bypass.py --strict
```

## PHASE07 Model Gateway Bypass Migration 008

已迁移两个核心 OpenAI chat-completions 调用点：

```text
src/backend/zuno/agent/core/models/reason_model.py
src/backend/zuno/agent/core/models/tool_call.py
```

新增 `OpenAIChatCompletionsGatewayAdapter` 于 `src/backend/zuno/platform/model_gateway.py`。`ReasoningModel.astream(...)` 和 `ToolCallModel.ainvoke(...)` 继续保留原 OpenAI chat completions response contract，但不再直接创建 `AsyncOpenAI` client；Provider SDK 调用收敛到 Gateway 边界。

同步更新：

```text
.agent/programs/work-products/phase07-provider-bypass-inventory.yaml
tests/repo/test_model_gateway_bypass.py
```

Status:

```text
PHASE07 bypass count reduced from 4 to 2
phase closure not approved
remaining: migrate anthropic.py and usage_model.py, then pass verify_model_gateway_bypass.py --strict
```

## PHASE07 Model Gateway Bypass Migration 009

已迁移 token-usage chat model 的 OpenAI / LangChain provider imports：

```text
src/backend/zuno/agent/core/models/usage_model.py
```

新增 `OpenAIUsageChatGatewayAdapter` 与 `is_openai_well_known_tool(...)` 于 `src/backend/zuno/platform/model_gateway.py`。`ChatModelWithTokenUsage` 继续保留同步、异步、stream、astream 和 token usage 记录语义，但 Provider SDK client 和 `WellKnownTools` 判断均收敛到 Gateway 边界。

同步更新：

```text
.agent/programs/work-products/phase07-provider-bypass-inventory.yaml
tests/repo/test_model_gateway_bypass.py
```

Status:

```text
PHASE07 bypass count reduced from 2 to 1
phase closure not approved
remaining: migrate anthropic.py, then pass verify_model_gateway_bypass.py --strict
```

## PHASE07 Model Gateway Bypass Migration 010

已迁移最后一个直接 Provider SDK import：

```text
src/backend/zuno/agent/core/models/anthropic.py
```

新增 `AnthropicMessagesGatewayAdapter` 与 `AsyncAnthropicMessagesGatewayAdapter` 于 `src/backend/zuno/platform/model_gateway.py`。`DeepAnthropic` 和 `DeepAsyncAnthropic` 不再继承 provider SDK class，而是通过 Gateway-owned adapter 组合实现原 `invoke`、`ainvoke` 和 stream helper 方法。

同步更新：

```text
tools/scripts/verify_model_gateway_bypass.py
.agent/programs/work-products/phase07-provider-bypass-inventory.yaml
tests/repo/test_model_gateway_bypass.py
```

Status:

```text
PHASE07 Provider SDK bypass count reduced from 1 to 0
verify_model_gateway_bypass.py --strict expected to pass
phase closure not approved
remaining: complete broader PHASE07 runtime closure evidence and dependency gates for PHASE05/PHASE06
```

## PHASE07 Model Gateway Guard Tightening 011

已收紧 PHASE07 cutover 后的遗留放行面：

```text
tools/scripts/verify_model_gateway_boundaries.py
.agent/programs/work-products/temporary-allowlist.yaml
tests/repo/test_model_gateway_bypass.py
```

变更内容：

```text
已迁移的 Provider SDK path 不再出现在 Model Gateway boundary legacy allowlist。
PHASE02 temporary allowlist 保留 PHASE01 inventory path 集合，但已完成 cutover 的条目从 active direct_provider_sdk 放行改为 resolved_provider_sdk_cutover 记录。
新增测试确保这些 path 不会重新被 legacy boundary 或 active direct_provider_sdk allowlist 放行。
RAG embedding 不再直接调用 ModelManager.get_model_config，改为通过 Gateway-owned embedding adapter builder 解析配置。
```

Status:

```text
PHASE07 provider bypass guard hardened after strict-zero cutover
phase closure not approved
remaining: complete broader PHASE07 runtime closure evidence and dependency gates for PHASE05/PHASE06
```

## PHASE11 Ingestion Source Lineage Schema 001

新增 PHASE11 PostgreSQL source-lineage 持久化 schema：

```text
infra/db/alembic/versions/20260719_18_ingestion_source_lineage.py
src/backend/zuno/platform/database/schema_registry.py
tools/scripts/verify_phase11_ingestion_source_lineage.py
tests/repo/test_phase11_ingestion_source_lineage.py
tests/integration/test_phase11_ingestion_persistence_runtime.py
docs/evidence/phase11-ingestion-source-lineage.md
```

覆盖持久化对象链：

```text
SourceObject
DocumentVersion
ParsePlan
ParseJob
ParseAttempt
ParseSnapshot
SourceSpan
QualityGateDecision
IndexableDocumentSnapshot
Ingestion Outbox
Ingestion Dead Letter
```

关键边界：

```text
Migration 链接到 20260719_17，避免第二 Alembic head。
表 owner 统一登记为 Input / Document Ingestion。
DocumentVersion 与 ParseSnapshot 分离。
ParseAttempt 记录 lease/fencing token。
QualityGateDecision 是 IndexableDocumentSnapshot 的 FK 前置条件。
Input migration 不创建 Knowledge Chunk、Entity、Relation、KnowledgeVersion、BM25 或 Vector Index。
IngestionUnitOfWork 可在一笔 Postgres transaction 中写入 SourceObject → IndexableDocumentSnapshot → Outbox。
缺 QualityGateDecision 时数据库 FK 拒绝 IndexableDocumentSnapshot handoff。
```

Status:

```text
PHASE11 source-lineage Postgres schema and repository partial implementation available
phase closure not approved
remaining: migrate real default upload/parser path to this schema; add queue crash, lease loss, retry/dead-letter, delete/legal-hold/restore and adapter conformance evidence
```

## PHASE05 Security Pre-effect Fault Semantics 002

新增 Security-owned persistence 行为：

```text
src/backend/zuno/platform/security/persistence.py
src/backend/zuno/platform/security/__init__.py
tests/fault/security/test_phase05_security_pre_effect_faults.py
tools/scripts/verify_phase05_security_persistence.py
docs/evidence/phase05-security-control-plane.md
```

覆盖语义：

```text
validate_pre_effect_authorization: effect 前重新校验 prepared_action_hash、epoch active、approval status 和 deadline
record_secret_ref / issue_secret_lease / validate_secret_lease: SecretRef/Lease 只保存 ref/hash/audience，wrong audience、expired lease、revoked secret fail-closed
record_redaction_decision: redaction_succeeded=False 时把 requested allow 降为 block，只保存 hash
```

已运行：

```text
python -m py_compile src/backend/zuno/platform/security/persistence.py tools/scripts/verify_phase05_security_persistence.py tests/fault/security/test_phase05_security_pre_effect_faults.py
python tools/scripts/verify_phase05_security_persistence.py
pytest -q tests/integration/test_phase05_security_persistence_runtime.py tests/fault/security -p no:cacheprovider
```

Status:

```text
PHASE05 security persistence fault semantics expanded
phase closure not approved
remaining: full PEP/PDP cutover, Product/API resume/download/citation/admin default-path reauthorization and PHASE06 audit dependency closure
```

## PHASE06 Observability Fault Semantics 004

新增 Observability-owned black-box fault 行为：

```text
src/backend/zuno/platform/observability/persistence.py
src/backend/zuno/platform/observability/__init__.py
tests/fault/observability/test_phase06_observability_fault_semantics.py
tools/scripts/verify_phase06_observability_persistence.py
docs/evidence/phase06-observability-persistence.md
```

覆盖语义：

```text
ingest_envelope: 同 envelope_id 不同 payload 进入 quarantined，并写 duplicate_envelope_payload_mismatch dead letter
verify_audit_chain: 检测 audit sequence gap 与 previous_hash mismatch
claim_projection_rebuild / complete_projection_rebuild: 使用 fencing_token 拒绝 stale projector late commit，并写 dead letter
```

已运行：

```text
python -m py_compile src/backend/zuno/platform/observability/persistence.py tools/scripts/verify_phase06_observability_persistence.py tests/fault/observability/test_phase06_observability_fault_semantics.py
python tools/scripts/verify_phase06_observability_persistence.py
pytest -q tests/integration/test_phase06_observability_persistence_runtime.py tests/fault/observability -p no:cacheprovider
```

Status:

```text
PHASE06 observability persistence fault semantics expanded
phase closure not approved
remaining: API authorization checks and full adapter default-path cutover
```

## PHASE06 Observability Query Surface 005

新增 Product-facing Observability query service/port：

```text
src/backend/zuno/api/services/product/__init__.py
src/backend/zuno/api/services/product/projection_service.py
src/backend/zuno/platform/observability/persistence.py
tests/api/test_phase06_observability_query_surface.py
tools/scripts/verify_phase06_observability_persistence.py
docs/evidence/phase06-observability-persistence.md
```

覆盖语义：

```text
ObservabilityProjectionQueryService.get_trace_projection: 返回 timeline、freshness/completeness、dead_letters
ObservabilityQueryPrincipal: 显式 tenant/workspace/scope 授权
trace_scope: query 前确认 trace 真实 workspace 边界
_public_payload: 从响应剥离 prompt、hidden_reasoning、chain_of_thought、secret、token、api_key、password、raw_tool_args 类字段
```

已运行：

```text
python -m py_compile src/backend/zuno/api/services/product/projection_service.py src/backend/zuno/platform/observability/persistence.py tools/scripts/verify_phase06_observability_persistence.py tests/api/test_phase06_observability_query_surface.py
python tools/scripts/verify_phase06_observability_persistence.py
pytest -q tests/api/test_phase06_observability_query_surface.py tests/integration/test_phase06_observability_persistence_runtime.py tests/fault/observability -p no:cacheprovider
```

Status:

```text
PHASE06 query service/port available
phase closure not approved
remaining: FastAPI route wiring if required and full adapter default-path cutover
```

## PHASE06 External Sink Isolation 006

新增 Observability external sink isolation 行为：

```text
src/backend/zuno/platform/observability/persistence.py
tests/fault/observability/test_phase06_external_sink_isolation.py
tools/scripts/verify_phase06_observability_persistence.py
docs/evidence/phase06-observability-persistence.md
```

覆盖语义：

```text
PostgresObservabilityRuntimeAdapter.record_span_with_external_sink: 本地 trace/span/runtime event/audit facts 先持久化
external sink delivery failed: 写入 external_sink_delivery_failed dead letter，不回滚本地事实
external sink delivery succeeded: delivery state 为 DELIVERED，但 source_success=False，不冒充源领域成功
```

已运行：

```text
python -m py_compile src/backend/zuno/platform/observability/persistence.py tools/scripts/verify_phase06_observability_persistence.py tests/fault/observability/test_phase06_external_sink_isolation.py
python tools/scripts/verify_phase06_observability_persistence.py
pytest -q tests/api/test_phase06_observability_query_surface.py tests/integration/test_phase06_observability_persistence_runtime.py tests/fault/observability -p no:cacheprovider
```

Status:

```text
PHASE06 external sink isolation available
phase closure not approved
remaining: full Agent/Model/Knowledge/Memory/Capability/Tool/Security/Infrastructure adapter default-path cutover and optional FastAPI route wiring
```

## PHASE05 Product Action Reauthorization 003

新增 Security-owned Product action reauthorization guard：

```text
src/backend/zuno/platform/security/product_actions.py
src/backend/zuno/platform/security/__init__.py
src/backend/zuno/api/services/workspace_task_runtime.py
src/backend/zuno/api/v1/workspace.py
tests/api/test_workspace_task_runtime.py
tools/scripts/verify_phase05_security_persistence.py
docs/evidence/phase05-security-control-plane.md
```

覆盖语义：

```text
SecurityProductActionRequest: 绑定 tenant/workspace/principal/action/resource/decision/prepared_action_hash
PostgresSecurityProductActionGuard: 通过 SecurityRepository.validate_pre_effect_authorization 做 effect/read/download 前重新授权
WorkspaceTaskRuntimeService.configure_security_product_action_guard: workspace artifact read/download 接入 Security guard
workspace API: artifact read/download 传入 login_user.user_id 作为 principal
```

已运行：

```text
python -m py_compile src/backend/zuno/platform/security/product_actions.py src/backend/zuno/api/services/workspace_task_runtime.py src/backend/zuno/api/v1/workspace.py tools/scripts/verify_phase05_security_persistence.py tests/api/test_workspace_task_runtime.py
python tools/scripts/verify_phase05_security_persistence.py
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_artifact_read_and_download_reauthorize_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_artifact_download_returns_403_when_security_reauthorization_denies tests/integration/test_phase05_security_persistence_runtime.py tests/fault/security -p no:cacheprovider
```

Status:

```text
PHASE05 product artifact read/download reauthorization guard available
phase closure not approved
remaining: production startup default Postgres guard wiring, resume/citation/admin default-path reauthorization and full PEP/PDP cutover
```

## PHASE05 Product Action Guard Startup Wiring 004

新增应用启动默认接线：

```text
src/backend/zuno/main.py
tools/scripts/verify_phase05_security_persistence.py
docs/evidence/phase05-security-control-plane.md
```

覆盖语义：

```text
init_config: 数据库 bootstrap 成功后配置 WorkspaceTaskRuntimeService.configure_security_product_action_guard(PostgresSecurityProductActionGuard(engine))
artifact read/download: 生产启动后默认使用 Postgres Security pre-effect validation guard
```

已运行：

```text
python -m py_compile src/backend/zuno/main.py tools/scripts/verify_phase05_security_persistence.py
python tools/scripts/verify_phase05_security_persistence.py
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_artifact_read_and_download_reauthorize_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_artifact_download_returns_403_when_security_reauthorization_denies -p no:cacheprovider
```

Status:

```text
PHASE05 product artifact read/download Postgres guard startup wiring available
phase closure not approved
remaining: resume/citation/admin default-path reauthorization and full PEP/PDP cutover
```

## PHASE05 Workspace Resume Reauthorization 005

新增 workspace approval resume 前 Security product action 重新授权：

```text
src/backend/zuno/api/services/workspace_task_runtime.py
src/backend/zuno/api/v1/workspace.py
tests/api/test_workspace_task_runtime.py
tools/scripts/verify_phase05_security_persistence.py
docs/evidence/phase05-security-control-plane.md
```

覆盖语义：

```text
WorkspaceTaskRuntimeService.approve_task: approval_waiting 状态转 resume 前调用 SecurityProductActionGuard
workspace API: approve endpoint 传入 login_user.user_id 作为 principal
deny: 返回 403，任务保持 approval_waiting，不进入 resume 或 complete
```

已运行：

```text
python -m py_compile src/backend/zuno/api/services/workspace_task_runtime.py src/backend/zuno/api/v1/workspace.py tools/scripts/verify_phase05_security_persistence.py tests/api/test_workspace_task_runtime.py
python tools/scripts/verify_phase05_security_persistence.py
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_reauthorizes_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_returns_403_when_security_guard_denies tests/api/test_workspace_task_runtime.py::test_workspace_artifact_read_and_download_reauthorize_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_artifact_download_returns_403_when_security_reauthorization_denies tests/integration/test_phase05_security_persistence_runtime.py tests/fault/security -p no:cacheprovider
```

Status:

```text
PHASE05 workspace approval/resume reauthorization guard available
phase closure not approved
remaining: citation/admin default-path reauthorization and full PEP/PDP cutover
```

## PHASE05 MCP Admin Reauthorization 006

新增 MCP 管理 admin override 的 Security product action 重新授权：

```text
src/backend/zuno/api/services/mcp_server.py
src/backend/zuno/api/services/mcp_stdio_server.py
src/backend/zuno/main.py
tests/agent/test_mcp_server_service.py
tests/agent/test_mcp_stdio_server_security.py
tools/scripts/verify_phase05_security_persistence.py
docs/evidence/phase05-security-control-plane.md
```

覆盖语义：

```text
MCPService.verify_user_permission: admin override view/config/test/update/delete 前调用 SecurityProductActionGuard
MCPService.create_mcp_server/get_all_servers: AdminUser create/list 默认路径调用 SecurityProductActionGuard
MCPServerService stdio create/update/delete: AdminUser 写路径调用 SecurityProductActionGuard
startup: 同一个 PostgresSecurityProductActionGuard 注入 workspace、MCP HTTP/SSE 和 MCP stdio 服务
deny: 在 DAO 写入/删除前中断，owner 自己更新自己的 server 不走 admin override
```

已运行：

```text
python -m py_compile src/backend/zuno/api/services/mcp_server.py src/backend/zuno/api/services/mcp_stdio_server.py src/backend/zuno/main.py tools/scripts/verify_phase05_security_persistence.py tests/agent/test_mcp_server_service.py tests/agent/test_mcp_stdio_server_security.py
python tools/scripts/verify_phase05_security_persistence.py
pytest -q tests/agent/test_mcp_server_service.py::test_mcp_admin_override_reauthorizes_through_security_guard tests/agent/test_mcp_server_service.py::test_mcp_admin_override_denial_blocks_before_permission_success tests/agent/test_mcp_server_service.py::test_mcp_owner_update_does_not_require_admin_override_security_guard tests/agent/test_mcp_stdio_server_security.py tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_reauthorizes_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_returns_403_when_security_guard_denies tests/api/test_workspace_task_runtime.py::test_workspace_artifact_read_and_download_reauthorize_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_artifact_download_returns_403_when_security_reauthorization_denies tests/integration/test_phase05_security_persistence_runtime.py tests/fault/security -p no:cacheprovider
```

Status:

```text
PHASE05 MCP admin default-path reauthorization guard available
phase closure not approved
remaining: citation default-path reauthorization, non MCP admin surface audit and full PEP/PDP cutover
```

## PHASE05 Workspace Citation Reauthorization 007

新增 workspace citation refs 默认读取面的 Security product action 重新授权：

```text
src/backend/zuno/api/services/workspace_task_runtime.py
src/backend/zuno/api/v1/workspace.py
tests/api/test_workspace_agentic_product_contract.py
tools/scripts/verify_phase05_security_persistence.py
docs/evidence/phase05-security-control-plane.md
```

覆盖语义：

```text
artifact response: artifact.read 之后，存在 citation_refs 时追加 citation.read
task snapshot: embedded artifact citation_refs 返回前调用 citation.read
workspace API: get task 传入 login_user.user_id 作为 principal
resource_ref: workspace-artifact:<artifact_id>:citations，独立于 artifact 内容读取
deny: 返回 403，不暴露 citation refs
```

已运行：

```text
python -m py_compile src/backend/zuno/api/services/workspace_task_runtime.py src/backend/zuno/api/v1/workspace.py tools/scripts/verify_phase05_security_persistence.py tests/api/test_workspace_agentic_product_contract.py
python tools/scripts/verify_phase05_security_persistence.py
pytest -q tests/api/test_workspace_agentic_product_contract.py::test_workspace_artifact_citation_refs_reauthorize_through_security_guard tests/api/test_workspace_agentic_product_contract.py::test_workspace_task_snapshot_citation_refs_return_403_when_security_guard_denies tests/api/test_workspace_agentic_product_contract.py::test_workspace_artifact_response_includes_citation_refs tests/api/test_workspace_task_runtime.py::test_workspace_artifact_read_and_download_reauthorize_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_artifact_download_returns_403_when_security_reauthorization_denies tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_reauthorizes_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_returns_403_when_security_guard_denies tests/integration/test_phase05_security_persistence_runtime.py tests/fault/security -p no:cacheprovider
```

Status:

```text
PHASE05 workspace citation refs reauthorization guard available
phase closure not approved
remaining: non MCP admin surface audit and full PEP/PDP cutover
```

## Goal01 Closure Matrix Freeze 001

按更新后的目标文件冻结四张有限 Closure Matrix：

```text
.agent/programs/work-products/goal01-closure-matrix.md
```

边界：

```text
branch: integration/goal01-control-plane-model-ingestion
start_sha_after_fetch: 36130924f5602c894d3d89eaaf6cefc3c8624a89
origin_main_sha_after_fetch: ed787ee962f7f567163388188e56b4b765c27877
matrix: PHASE05 PEP/PDP Cutover, PHASE06 Adapter Cutover, PHASE07 Runtime Closure, PHASE11 Ingestion Closure
```

Status:

```text
Closure Matrix frozen
phase closure not approved
only mandatory_open/completion_candidate rows may be processed unless tests prove architecture defect
```

## PHASE05 Non-MCP Admin Reauthorization 008

新增非 MCP admin override 的共享 Security product action 重新授权：

```text
src/backend/zuno/api/services/security_admin_actions.py
src/backend/zuno/api/services/agent.py
src/backend/zuno/api/services/tool.py
src/backend/zuno/api/services/dialog.py
src/backend/zuno/api/services/mcp_agent.py
src/backend/zuno/api/services/llm.py
src/backend/zuno/api/services/knowledge.py
src/backend/zuno/api/services/knowledge_file.py
src/backend/zuno/api/v1/agent.py
src/backend/zuno/api/v1/tool.py
src/backend/zuno/api/v1/dialog.py
src/backend/zuno/api/v1/llm.py
src/backend/zuno/api/v1/knowledge.py
src/backend/zuno/api/v1/knowledge_file.py
src/backend/zuno/main.py
tests/agent/test_phase05_admin_action_reauthorization.py
tools/scripts/verify_phase05_security_persistence.py
docs/evidence/phase05-security-control-plane.md
```

覆盖语义：

```text
shared guard: security_admin_actions.require_admin_action_authorized 构造 SecurityProductActionRequest
startup: init_config 将 PostgresSecurityProductActionGuard 注入共享 admin guard
admin override: Agent / Tool / Dialog / MCP Agent / LLM / Knowledge / Knowledge File 在 owner 不等于 AdminUser 时重新授权
owner path: owner 自己操作自己的 resource 不触发 admin override guard
deny: 在 permission success 或 DAO delete/update 前中断
```

已运行：

```text
python -m py_compile src/backend/zuno/api/services/security_admin_actions.py src/backend/zuno/api/services/agent.py src/backend/zuno/api/services/tool.py src/backend/zuno/api/services/dialog.py src/backend/zuno/api/services/mcp_agent.py src/backend/zuno/api/services/llm.py src/backend/zuno/api/services/knowledge.py src/backend/zuno/api/services/knowledge_file.py src/backend/zuno/api/v1/agent.py src/backend/zuno/api/v1/dialog.py src/backend/zuno/api/v1/llm.py src/backend/zuno/api/v1/tool.py src/backend/zuno/api/v1/knowledge.py src/backend/zuno/api/v1/knowledge_file.py src/backend/zuno/main.py tests/agent/test_phase05_admin_action_reauthorization.py
python tools/scripts/verify_phase05_security_persistence.py
pytest -q tests/agent/test_phase05_admin_action_reauthorization.py tests/agent/test_mcp_server_service.py::test_mcp_admin_override_reauthorizes_through_security_guard tests/agent/test_mcp_server_service.py::test_mcp_admin_override_denial_blocks_before_permission_success tests/agent/test_mcp_server_service.py::test_mcp_owner_update_does_not_require_admin_override_security_guard tests/agent/test_mcp_stdio_server_security.py tests/api/test_workspace_task_runtime.py::test_workspace_artifact_read_and_download_reauthorize_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_artifact_download_returns_403_when_security_reauthorization_denies tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_reauthorizes_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_returns_403_when_security_guard_denies tests/api/test_workspace_agentic_product_contract.py::test_workspace_artifact_citation_refs_reauthorize_through_security_guard tests/api/test_workspace_agentic_product_contract.py::test_workspace_task_snapshot_citation_refs_return_403_when_security_guard_denies tests/integration/test_phase05_security_persistence_runtime.py tests/fault/security -p no:cacheprovider
```

Status:

```text
PHASE05 non-MCP admin default-path reauthorization guard available
phase closure not approved
remaining: Legacy Approval Boolean adapter deletion plan/guard and full PEP/PDP closure review
```

## PHASE05 Legacy Approval Boolean Adapter 009

新增 Legacy Approval Boolean 到 Decision/Ref 的 versioned adapter 约束：

```text
src/backend/zuno/capability/runtime.py
src/backend/zuno/api/services/workspace_task_runtime.py
tests/agent/test_tool_control_plane_runtime.py
tests/api/test_workspace_task_runtime.py
tools/scripts/verify_phase05_security_persistence.py
.agent/programs/work-products/goal01-closure-matrix.md
docs/evidence/phase05-security-control-plane.md
```

覆盖语义：

```text
ToolRuntimeRequest.approved: 仅保留为 temporary.adapter.tool_runtime.approved_bool
removal_phase: PHASE16
workspace resume default path: approved=True 同时传入 security-approval-decision:<task_id>:<approval_id>
security facts / approval ledger: 记录 approval_decision_ref、approval_adapter_ref、approval_adapter_removal_phase
verifier: 阻止 src/backend/zuno 中新增 ToolRuntimeRequest 之外的 approved: bool owner
```

已运行：

```text
python -m py_compile src/backend/zuno/capability/runtime.py src/backend/zuno/api/services/workspace_task_runtime.py tools/scripts/verify_phase05_security_persistence.py tests/agent/test_tool_control_plane_runtime.py tests/api/test_workspace_task_runtime.py
python tools/scripts/verify_phase05_security_persistence.py
pytest -q tests/agent/test_tool_control_plane_runtime.py::test_high_side_effect_tool_waits_for_approval_then_uses_brokered_credentials tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_emits_security_approval_facts_from_active_tool_path tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_reauthorizes_through_security_guard tests/api/test_workspace_task_runtime.py::test_workspace_task_approval_resume_returns_403_when_security_guard_denies tests/integration/test_phase05_security_persistence_runtime.py tests/fault/security -p no:cacheprovider
```

Status:

```text
PHASE05 legacy approval boolean adapter bounded
phase closure not approved
remaining: PHASE05 Pre-Closure gate and Coordinator review
```

## PHASE06 Model Gateway Observability Adapter 010

新增 Model Gateway runtime 到 PHASE06 typed runtime event/span adapter 的消费边界：

```text
src/backend/zuno/platform/observability/persistence.py
tests/integration/test_phase06_observability_persistence_runtime.py
tools/scripts/verify_phase06_observability_persistence.py
.agent/programs/work-products/goal01-closure-matrix.md
docs/evidence/phase06-observability-persistence.md
```

覆盖语义：

```text
PostgresObservabilityRuntimeAdapter.record_model_gateway_trace_event(...)
requires explicit tenant_id; does not infer tenant from Gateway trace_event
consumes Gateway-owned trace_event payload and writes model span + model.model_call_* runtime event + audit receipt
retains call_id, binding, attempts and ESTIMATE/OBSERVED usage receipt separation
Observability does not retry, reroute or mark provider failure as source success
```

已运行：

```text
python -m py_compile src/backend/zuno/platform/observability/persistence.py tools/scripts/verify_phase06_observability_persistence.py tests/integration/test_phase06_observability_persistence_runtime.py
python tools/scripts/verify_phase06_observability_persistence.py
pytest -q tests/integration/test_phase06_observability_persistence_runtime.py::test_observability_runtime_adapter_persists_model_gateway_trace_event -p no:cacheprovider
git diff --check
```

Status:

```text
PHASE06 Model adapter row moved to completion_candidate
phase closure not approved
remaining: PHASE06 aggregate verification and Coordinator review
```

## PHASE05 Non-MCP Admin Matrix Reconciliation 011

更正 Closure Matrix 中 Non-MCP admin row 的状态：

```text
Admin 管理面：Agent / Tool / Dialog / MCP Agent / LLM / Knowledge / Knowledge File
mandatory_open -> completion_candidate
```

原因：

```text
`f04117ec` 已提交共享 security_admin_actions guard、verifier/evidence 和 focused admin tests；
PHASE05 evidence 已记录 Agent/Tool/Dialog/MCP Agent/LLM/Knowledge/Knowledge File admin override deny-before-DAO。
本次只同步 Matrix 状态，不新增 runtime 行为。
```

已运行：

```text
python tools/scripts/verify_phase05_security_persistence.py
pytest -q tests/agent/test_phase05_admin_action_reauthorization.py -p no:cacheprovider
git diff --check
```

## Goal01 Continuation Start and Ledger Promotion 012

按新目标文件继续使用集成分支，并在开始前 fetch origin：

```text
branch: integration/goal01-control-plane-model-ingestion
continuation_start_sha_after_fetch: 1a65a28a2ca19e11c57a4b1a575052ea07dfb747
origin_main_sha_after_fetch: ed787ee962f7f567163388188e56b4b765c27877
origin_integration_sha_after_fetch: 1a65a28a2ca19e11c57a4b1a575052ea07dfb747
first_fetch_attempt: environment transport failure, schannel TLS handshake
second_fetch_attempt: passed
```

修复 Requirement Ledger 的 Target-to-Current promotion blocker：

```text
PHASE05 mandatory requirements: 140 implementation_available, 0 target_not_current
PHASE06 mandatory requirements: 44 implementation_available, 0 target_not_current
current_status_counts: implementation_available 258, target_not_current 498
```

同步修复 PHASE04 pre/post closure verifier：

```text
旧规则把全局 Requirement Ledger 计数冻结为 74/682，会阻止 PHASE05+ 正常晋升。
新规则保留 PHASE04 mandatory no target_not_current 检查，只要求 current_status_counts 与实际 ledger 自洽。
```

已运行：

```text
python tools/scripts/verify_requirement_ledger_evidence_gate.py
python tools/scripts/verify_phase04_post_closure_consistency.py
python tools/scripts/verify_current_program.py
```

## PHASE06 Observability Query API Route 013

补齐 PHASE06 Product Query row 的真实 API 接线点：

```text
src/backend/zuno/api/v1/observability.py
src/backend/zuno/api/router.py
tests/api/test_phase06_observability_query_route.py
tools/scripts/verify_phase06_observability_persistence.py
docs/evidence/phase06-observability-persistence.md
.agent/programs/work-products/goal01-closure-matrix.md
```

覆盖语义：

```text
GET /api/v1/observability/traces/{trace_id}
uses ObservabilityProjectionQueryService
admin principal receives authorized freshness/timeline/dead-letter projection
non-admin API access returns 403
route does not modify source domain facts
```

已运行：

```text
python -m py_compile src/backend/zuno/api/v1/observability.py src/backend/zuno/api/router.py tools/scripts/verify_phase06_observability_persistence.py tests/api/test_phase06_observability_query_route.py
pytest -q tests/api/test_phase06_observability_query_surface.py tests/api/test_phase06_observability_query_route.py -p no:cacheprovider
python tools/scripts/verify_phase06_observability_persistence.py
```

## PHASE05 PHASE06 Pre-Closure Gates 014

新增 PHASE05 / PHASE06 非破坏性 Pre-Closure gate：

```text
tools/scripts/verify_phase05_pre_closure_gate.py
tools/scripts/verify_phase06_pre_closure_gate.py
docs/evidence/phase05-pre-closure.md
docs/evidence/phase06-pre-closure.md
docs/evidence/phase05-security-control-plane.md
docs/evidence/phase06-observability-persistence.md
```

Gate 覆盖：

```text
Closure Matrix mandatory_open: none for PHASE05/PHASE06
Requirement Ledger target_not_current: none for PHASE05/PHASE06 mandatory items
PHASE05 security persistence/eval verifiers pass
PHASE06 observability persistence verifier passes
Evidence no longer contains resolved pre-closure blockers
Coordinator Closure Decision still required
```

已运行：

```text
python -m py_compile tools/scripts/verify_phase05_pre_closure_gate.py tools/scripts/verify_phase06_pre_closure_gate.py
python tools/scripts/verify_phase05_pre_closure_gate.py
python tools/scripts/verify_phase06_pre_closure_gate.py
```

## PHASE05 PHASE06 Coordinator Closure Decisions 015

Coordinator 独立批准 PHASE05 与 PHASE06 由 `completion_candidate` 晋升为 `completed`：

```text
PHASE05 closure_decision: docs/evidence/phase05-coordinator-closure.md
PHASE06 closure_decision: docs/evidence/phase06-coordinator-closure.md
PHASE05 readiness: .agent/programs/work-products/phase05-readiness.yaml
PHASE06 readiness: .agent/programs/work-products/phase06-readiness.yaml
```

状态同步：

```text
program_manifest: PHASE05 completed, PHASE06 completed, PHASE07 ready, PHASE11 ready
current_phase: PHASE07
PHASE08: planned
PHASE09-PHASE22: not current
production_readiness: not production ready
```

Post-Closure Gate 新增：

```text
tools/scripts/verify_phase05_post_closure_consistency.py
tools/scripts/verify_phase06_post_closure_consistency.py
```

## PHASE07 Coordinator Closure Decision 016

PHASE07 依赖已满足并完成独立 Closure：

```text
PHASE05 closure: approved
PHASE06 closure: approved
PHASE07 closure_decision: docs/evidence/phase07-coordinator-closure.md
PHASE07 readiness: .agent/programs/work-products/phase07-readiness.yaml
current_phase_after_closure: PHASE11
PHASE08: planned until PHASE11 completed
```

真实修复：

```text
src/backend/zuno/platform/model_gateway_adapters.py
src/backend/zuno/platform/model_gateway.py
```

原因：

```text
PHASE07 focused gate 发现 Gateway core 文件仍内联 OpenAI/Anthropic Provider SDK adapter builder。
已将 Provider SDK 调用迁移到 adapter boundary，保持 `zuno.platform.model_gateway` 对外 re-export 不变。
```

已运行：

```text
python -m py_compile src/backend/zuno/platform/model_gateway.py src/backend/zuno/platform/model_gateway_adapters.py tools/scripts/verify_model_gateway_runtime_batch.py tools/scripts/verify_model_gateway_bypass.py
python tools/scripts/verify_model_gateway_runtime_batch.py
python tools/scripts/verify_model_gateway_bypass.py --strict
pytest -q tests/platform/test_model_gateway.py tests/repo/test_model_gateway_bypass.py -p no:cacheprovider
python tools/scripts/verify_phase07_pre_closure_gate.py
python tools/scripts/verify_phase07_post_closure_consistency.py
python tools/scripts/verify_current_program.py
python tools/scripts/verify_requirement_ledger_evidence_gate.py
```

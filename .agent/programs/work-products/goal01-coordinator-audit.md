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

Gap:

- Phase file requires full Security control-plane persistence and integration paths under `src/backend/zuno/platform/database/security/**`; no dedicated security Alembic revision or database security directory was found in the initial audit.
- Phase closure requires production paths to consume only `Decision/Ref`; legacy approval booleans and scattered `approval_required` / `approved` fields still exist as migration inputs.
- Mandatory audit integration depends on PHASE06 acceptance and Infrastructure mandatory audit primitive, but Phase-level integration evidence is not yet closed.
- Product/Agent/Tool paths still use boolean/string approval decisions, including workspace resume and tool runtime `approved: bool` inputs.
- `tests/integration/security/**` and `tests/fault/security/**` do not exist yet, so stale epoch, replay, audit unavailable, secret lease expiry/wrong audience and redaction failure are not proven as Phase fault coverage.

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

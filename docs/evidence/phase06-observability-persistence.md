# PHASE06 Observability Persistence Evidence

status: partial_implementation_available

phase_completion: `not_approved`

date: 2026-07-19

## 目标

记录 PHASE06 Observability Minimum Black Box 的当前可复现证据，覆盖 Postgres append-only ingest、trace/span/runtime event、immutable audit ledger、watermark/gap、dead letter、read-only freshness query、typed security audit adapter 和 focused fault semantics。本文不是 Phase Closure Decision。

## 已证明

- Observability-owned PostgreSQL schema 已提供 ingest envelope、trace、span、runtime event、audit record、projection watermark、gap、dead letter 和 projection rebuild 事实表。
- `ObservabilityRepository.ingest_envelope(...)` 会 redaction 后保存 payload hash；同租户同 schema 同 payload 作为 duplicate ACK；同 `envelope_id` 不同 payload 会 quarantine 并写入 dead letter。
- `record_runtime_event(...)` 维护 stream sequence watermark；out-of-order event 会打开 gap，补齐后 freshness 变回 `fresh` 并把 gap 标为 `filled`。
- duplicate stream sequence 但 payload hash 不同会写入 dead letter，不覆盖原始 event。
- `record_audit(...)` 保存 sequence、previous_hash、payload_hash 和 audit_hash；`verify_audit_chain(...)` 可检测 sequence gap 和 hash mismatch。
- `claim_projection_rebuild(...)` / `complete_projection_rebuild(...)` 使用 fencing token 拒绝 stale projector late commit，并写入 dead letter。
- `PostgresObservabilityRuntimeAdapter` 可把 `ZunoSpan` 与 `SandboxAuditEvent` 写入 trace/span/runtime event/audit record，不修改源领域事实。
- `trace_timeline(...)`、`projection_freshness(...)` 和 `dead_letters(...)` 提供只读查询，返回 freshness/gap/dead-letter 信息，payload 保持 redacted。

## 可复现验证

```powershell
python -m py_compile src/backend/zuno/platform/observability/persistence.py tools/scripts/verify_phase06_observability_persistence.py tests/fault/observability/test_phase06_observability_fault_semantics.py
python tools/scripts/verify_phase06_observability_persistence.py
pytest -q tests/integration/test_phase06_observability_persistence_runtime.py tests/fault/observability -p no:cacheprovider
```

## 未证明

- 尚未形成 PHASE06 closure decision。
- API-level authorized query path 仍未完成。
- 外部 sink failure isolation 仍只在 target/foundation 层说明，未形成 focused fault evidence。
- 完整 Agent、Model、Knowledge、Memory、Capability、Tool、Security、Infrastructure adapter cutover 尚未全部证明。
- PHASE07、PHASE20 和后续 Phase 不得引用本文作为 PHASE06 completed 证明。

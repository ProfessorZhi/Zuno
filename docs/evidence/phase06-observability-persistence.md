# PHASE06 Observability Persistence Evidence

status: partial_implementation_available

phase_completion: `not_approved`

date: 2026-07-19

## 目标

记录 PHASE06 Observability Minimum Black Box 的当前可复现证据，覆盖 Postgres append-only ingest、trace/span/runtime event、immutable audit ledger、watermark/gap、dead letter、read-only freshness query、typed security/model audit adapter 和 focused fault semantics。本文不是 Phase Closure Decision。

## 已证明

- Observability-owned PostgreSQL schema 已提供 ingest envelope、trace、span、runtime event、audit record、projection watermark、gap、dead letter 和 projection rebuild 事实表。
- `ObservabilityRepository.ingest_envelope(...)` 会 redaction 后保存 payload hash；同租户同 schema 同 payload 作为 duplicate ACK；同 `envelope_id` 不同 payload 会 quarantine 并写入 dead letter。
- `record_runtime_event(...)` 维护 stream sequence watermark；out-of-order event 会打开 gap，补齐后 freshness 变回 `fresh` 并把 gap 标为 `filled`。
- duplicate stream sequence 但 payload hash 不同会写入 dead letter，不覆盖原始 event。
- `record_audit(...)` 保存 sequence、previous_hash、payload_hash 和 audit_hash；`verify_audit_chain(...)` 可检测 sequence gap 和 hash mismatch。
- `claim_projection_rebuild(...)` / `complete_projection_rebuild(...)` 使用 fencing token 拒绝 stale projector late commit，并写入 dead letter。
- `PostgresObservabilityRuntimeAdapter` 可把 `ZunoSpan` 与 `SandboxAuditEvent` 写入 trace/span/runtime event/audit record，不修改源领域事实。
- `PostgresObservabilityRuntimeAdapter.record_model_gateway_trace_event(...)` 可消费 Model Gateway runtime 产出的 `trace_event`，在显式 `tenant_id` 下写入 `model` span、`model.model_call_*` runtime event 和 audit receipt；payload 保留 Gateway-owned `call_id`、binding、attempts、`ESTIMATE` / `OBSERVED` usage receipts，不把 provider failure 冒充为业务成功。
- `PostgresObservabilityRuntimeAdapter.record_span_with_external_sink(...)` 已证明外部 sink 失败不会回滚本地 trace/span/runtime event/audit facts；失败会写入 `external_sink_delivery_failed` dead letter；成功的 external delivery receipt 仍保持 `source_success=False`。
- `trace_timeline(...)`、`projection_freshness(...)` 和 `dead_letters(...)` 提供只读查询，返回 freshness/gap/dead-letter 信息，payload 保持 redacted。
- `ObservabilityProjectionQueryService` 提供 Product query port，显式校验 tenant、workspace、`observability:read` scope 和 trace workspace 边界；返回 timeline/freshness/dead-letter 时剥离 prompt、hidden reasoning、secret、token、api_key、password 和 raw_tool_args 类字段。
- `/api/v1/observability/traces/{trace_id}` 已接入授权只读 Query API route；当前 API route 只允许 admin principal 进入 projection service，非 admin 返回 403，不修改源领域事实。

## 可复现验证

```powershell
python -m py_compile src/backend/zuno/platform/observability/persistence.py src/backend/zuno/api/v1/observability.py src/backend/zuno/api/router.py tools/scripts/verify_phase06_observability_persistence.py tests/api/test_phase06_observability_query_route.py tests/integration/test_phase06_observability_persistence_runtime.py tests/fault/observability/test_phase06_external_sink_isolation.py
python tools/scripts/verify_phase06_observability_persistence.py
pytest -q tests/api/test_phase06_observability_query_surface.py tests/api/test_phase06_observability_query_route.py tests/integration/test_phase06_observability_persistence_runtime.py tests/fault/observability -p no:cacheprovider
```

## 未证明

- 尚未形成 PHASE06 closure decision。
- 完整 Agent、Knowledge、Memory、Capability、Tool、Security、Infrastructure adapter cutover 尚未全部证明。
- PHASE07、PHASE20 和后续 Phase 不得引用本文作为 PHASE06 completed 证明。

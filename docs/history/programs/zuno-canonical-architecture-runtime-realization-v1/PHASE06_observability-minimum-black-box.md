# PHASE06 Observability Minimum Black Box

phase_id: PHASE06
status: completed
depends_on: PHASE03, PHASE04
owner: Module 10 Observability & Eval

## Phase 目标

PHASE06 completed。Observability Minimum Black Box 在完整 Phase Scope 内达到 implementation available；这不表示 PHASE20 Eval/Release Gate、quality proven 或 production ready。

先建立所有后续 Runtime 必须依赖的最小黑盒：版本化 Telemetry Envelope、Append-only Ingest、Trace/Span、Runtime Event、Immutable Audit、Dedup、Ordering/Watermark/Gap、Projection/Rebuild 和只读 Query。此 Phase 不实现完整 Eval，但必须保证失败不会静默消失。

## Minimal Read Set

- `docs/modules/10-observability-eval.md`
- PHASE03 Envelope/Audit Contract
- PHASE04 Outbox/Inbox/PostgreSQL/Object
- 当前 observability/trace/audit/eval helper

## Current Anchors

```text
src/backend/zuno/platform/observability/**
src/backend/zuno/agent/**/trace*
src/backend/zuno/api/**/trace*
tools/evals/zuno/**
tests/**/observability*
```

## Allowed Paths

```text
src/backend/zuno/platform/observability/**
src/backend/zuno/platform/database/observability/**
src/backend/zuno/api/product/routes/queries.py
src/backend/zuno/api/services/product/projection_service.py
tests/observability/**
tests/integration/observability/**
tests/fault/observability/**
docs/evidence/**
```

## Forbidden Paths

- Observability 修改源领域事实、触发业务 Retry 或 Agent Replan。
- 采样 Audit、Security Deny、Approval、Effect、RunOutcome、Release Gate。
- 外部平台 Object ID 成为内部主键。

## Work Packages

### P06-T01 TelemetryEnvelope Ingest Service
- Goal：实现 schema/scope/epoch/hash/redaction validation、append-only envelope store、quarantine。
- Tests：duplicate same hash ACK、duplicate different hash quarantine、missing tenant、stale schema、redaction failure。
- Acceptance：Ingest failure 有 Durable Outbox/Retry 或明确 fail-close policy。

### P06-T02 Trace and Span Reducer
- Goal：构建 TraceRecord/SpanRecord、parent/link/causation、terminal immutable、late-event revision。
- Tests：out-of-order span、duplicate terminal、missing parent、parallel branch link、resume same trace。
- Acceptance：Projection 可重建，Raw Event 保留。

### P06-T03 Runtime Event Adapters
- Goal：为 Agent、Model、Knowledge、Memory、Capability、Tool、Security、Infrastructure 建 typed adapter。
- Tests：required field validator；旧 event adapter 不丢 scope/epoch/generation；unknown event quarantine。
- Acceptance：Adapter 不改变源状态，只标准化观测。

### P06-T04 Immutable Audit Ledger
- Goal：实现 accepted AuditEvent、sequence/hash chain、mandatory acceptance receipt、gap detection。
- Tests：hash mismatch、sequence gap、store unavailable、duplicate event、restore 后校验。
- Acceptance：AuditReceipt 只证明持久接受，不证明 Tool/Run 成功。

### P06-T05 Projection Watermark, Gap and Rebuild
- Goal：实现 projector inbox、per-stream watermark、gap lifecycle、rebuild claim/fencing。
- Tests：late event、gap fill、rebuild crash、old projector late commit、projection deletion/recreate。
- Acceptance：产品查询返回 freshness/completeness，不隐藏 gap。

### P06-T06 Query API and Authorization
- Goal：实现 run timeline、trace、audit、module attempts、freshness 的只读 API/Port。
- Tests：tenant/workspace authorization、redaction、missing trace、stale projection、admin scope。
- Acceptance：不暴露 prompt、hidden reasoning、secret、raw tool args。

### P06-T07 Fault and Operational Baseline
- Goal：建立 ingest lag、gap age、audit latency、backlog、dead letter、trace completeness SLO surface 和 Runbook。
- Tests：trace store outage、external sink failure、redaction failure、audit gap、rebuild。
- Acceptance：外部 sink 可选；本地事实不因 sink 失败回滚。

## Phase 完成定义

- 后续所有模块能写入版本化 Trace/Audit。
- Dedup、Gap、Rebuild、Authorization、Redaction Fault Test 通过。
- 查询能显示 freshness/blocked，而不是伪造完整 Trace。
- 无旧 trace helper 作为第二事实 Owner；临时 adapter 有删除任务。

## Validation

```bash
git diff --check
python tools/scripts/verify_observability_eval_target_protocols.py
pytest -q tests/observability tests/integration/observability tests/fault/observability -p no:cacheprovider
```

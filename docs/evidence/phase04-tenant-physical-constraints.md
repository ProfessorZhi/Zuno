# PHASE04 Tenant Physical Constraints Evidence

phase_id: PHASE04
task_id: P04-T07
requirement_ids:
  - ARCH-INFRA-034
status: implementation_available
date: 2026-07-18

## 边界

本证据证明 PHASE04 当前已经把租户范围放入真实基础设施的物理或协议约束中：PostgreSQL 使用 transaction-local tenant context、tenant 参与唯一键和查询条件；RabbitMQ delivery header 保留 tenant context；MinIO/Object 路径通过 bucket/prefix/authorization hook 和 `SourceObjectRefV1` 的 tenant-bound object ref 固定边界；operator telemetry snapshot 带 tenant/trace/failure owner。

本证据不证明 `ARCH-INFRA-058` 的全服务运行时 cross-tenant hit quarantine/fail-closed，也不证明 official LangGraph PostgreSQL Checkpointer、企业 Vector/Graph/Search adapter、PITR 或完整 RecoverySet 已完成。

## Verification Results

- relational_tenant_physical_constraint: passed
- queue_tenant_protocol_constraint: passed
- object_tenant_target_constraint: passed
- trace_audit_tenant_snapshot_constraint: passed
- application_end_filter_only_rejected: passed
- target_only_services_not_promoted: passed
- phase_completion: blocked_official_checkpointer_and_full_recovery_set

## Commands

```powershell
python tools/scripts/verify_phase04_tenant_physical_constraints.py
```

Expected result:

```text
PHASE04 tenant physical constraints verification passed.
```

```powershell
pytest -q tests/repo/test_phase04_tenant_physical_constraints.py -p no:cacheprovider
```

Expected result:

```text
2 passed
```

## Current

- `RELATIONAL`：`tenant_id` 进入 PostgreSQL session context、idempotency unique key、outbox/inbox ordering key、delivery watermark key 和 SQL `WHERE tenant_id = :tenant_id`。
- `QUEUE`：RabbitMQ publish/replay 保留 `tenant_id` header，Outbox publisher 的真实 transport evidence 证明 delivery 不丢失 tenant context。
- `OBJECT`：Object ref contract 绑定 `tenant_id` 与 `object_uri`；MinIO 子范围证明 bucket/prefix/staging、authorization hook fail-closed 和真实 S3-compatible operation。
- `TRACE_AUDIT`：operator snapshot 带 `tenant_id`、`trace_id`、failure owner、retry owner 和 recovery owner。

## Remaining Target

- `CHECKPOINT` 仍被 official LangGraph PostgreSQL Checkpointer 关键依赖阻塞。
- `VECTOR`、`GRAPH`、`LEXICAL`、`CACHE`、`SECRET_KMS` 仍是 profile-only 或 blocked，不能被当作已经具备全服务物理租户隔离。
- Cross-tenant hit quarantine/fail-closed 的完整运行时证明仍归 `ARCH-INFRA-058`。

# PHASE04 运维就绪、容量与退化证据

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-17
status: implementation_available_for_operator_readiness_subscope
operator_readiness_snapshot: passed
postgres_health_readiness_metrics: passed
rabbitmq_capacity_backlog_probe: passed
minio_readiness_probe: passed
structured_operator_log: passed
trace_correlation: passed
telemetry_not_eval_verdict: passed
failure_owner_retry_recovery: passed
p04_t07_operator_subscope: proven
phase_completion: blocked_official_checkpointer_and_full_recovery_set

## 边界

本证据只证明 P04-T07 的运维就绪、容量、backlog、结构化日志和失败归属子范围。它不证明 PHASE04 已关闭，也不证明官方 LangGraph PostgreSQL Checkpointer、完整 Projection Replay、PITR 或含 Checkpointer 的组合恢复。

Operator telemetry 是运行观测事实，不产生 Eval verdict，不冒充领域成功。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL | `zuno-postgres`，`postgres:16`，`localhost:5432` |
| RabbitMQ | `zuno-rabbitmq`，`rabbitmq:3.13-management-alpine`，`localhost:5672` |
| MinIO | `zuno-minio`，`minio/minio:RELEASE.2023-03-20T20-16-18Z`，`localhost:9000` |
| 验证命令 | `python tools/scripts/verify_phase04_operator_readiness.py` |
| 集成测试 | `pytest -q tests/integration/test_phase04_operator_readiness.py -p no:cacheprovider` |

## 已验证行为

- PostgreSQL 通过 `PostgresRuntime.sync_health()` 与 `PostgresRuntime.async_health()` 返回真实 health/readiness、server version、pool size、checked out 和 overflow。
- PostgreSQL Outbox 写入唯一 operator marker，并通过 `InfrastructureRepository.outbox_backlog()` 读取真实 ready/delayed/claimed/dead_letter/oldest pending 指标，随后清理 marker row。
- RabbitMQ 使用真实 durable exchange/queue/DLQ，发布带 trace header 的 persistent message，读取 queue depth，消费 ACK 后确认队列深度归零，并删除临时 topology。
- MinIO 使用真实 bucket/object，stage + commit + read 校验内容和 raw SHA-256，随后删除临时 bucket。
- Operator snapshot 包含 `schema_version`、`event_type`、`trace_id`、`tenant_id`、每个依赖的 health/readiness/capacity/backlog、failure owner、retry owner、recovery owner 和 evidence ref。
- Snapshot 显式保留 `eval_verdict: None`，证明该 telemetry 不是质量评分，也不把基础设施 receipt 解释成领域成功。
- 每次 probe 使用唯一 marker，清理 PostgreSQL marker、RabbitMQ 临时 topology 和 MinIO 临时 bucket。

## 命令与结果

```text
python tools/scripts/verify_phase04_operator_readiness.py
PHASE04 operator readiness verification passed.
```

```text
pytest -q tests/integration/test_phase04_operator_readiness.py -p no:cacheprovider
1 passed
```

## Requirement 对应

| Requirement | 当前证据 |
| --- | --- |
| `ARCH-INFRA-036` Health/Readiness/Degraded 分离 | PostgreSQL sync/async readiness、RabbitMQ queue probe、MinIO read probe 与明确 `ready/not_ready` 状态 |
| `ARCH-INFRA-037` Telemetry Hook 不伪造 Eval | 结构化 operator snapshot 明确 `eval_verdict: None` |
| `ARCH-INFRA-038` Failure 含 Owner/Retry/Recovery/Evidence | 每个依赖记录 failure owner、retry owner、recovery owner 和 evidence ref |

## 剩余缺口

- 官方 LangGraph PostgreSQL Checkpointer 仍需要关键依赖审批和真实恢复证据。
- P04-T07 的完整 Backup/Restore/Replay 仍缺官方 Checkpointer restore、PITR 和跨领域 Projection Replay。
- PHASE04 coordinator approval 仍为 pending，PHASE05 start gate 仍关闭。

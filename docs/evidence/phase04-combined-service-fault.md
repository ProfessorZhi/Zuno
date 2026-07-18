# PHASE04 三服务组合故障证据

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-18
status: implementation_available_for_combined_service_fault_subscope
postgres_rabbitmq_minio_combined_outage: passed
dependency_calls_fail_closed: passed
durable_rabbitmq_message_recovered: passed
outbox_to_inbox_after_restart: passed
minio_hash_after_restart: passed
new_postgres_runtime_after_restart: passed
checkpoint_primitive_after_restart: passed
official_checkpointer_in_combined_fault: passed
official_checkpointer_after_restart: passed
official_checkpointer_delta_history_after_restart: passed
combined_dependency_fault: proven

## 边界

本证据证明 PostgreSQL、RabbitMQ、MinIO 和官方 LangGraph PostgreSQL Checkpointer 组合依赖路径在三项真实服务同时停机时 fail closed；三项服务重新健康后，新建 Runtime、RabbitMQ Transport、MinIO client 和官方 `PostgresSaver` 可以对账停机前耐久事实，并继续完成 Outbox 到 RabbitMQ 再到 Inbox 的交付。

本证据证明 `combined_dependency_fault: proven`。它不关闭 P04-T07，也不关闭 PHASE04；跨领域 replay、Coordinator approval 和 PHASE05 ready gate 仍必须单独收口。`infra_checkpoints` primitive 仍只作为 Infrastructure receipt 边界存在，不能解释为官方 Checkpointer 或领域成功。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL | `zuno-postgres`，镜像 `postgres:16` |
| RabbitMQ | `zuno-rabbitmq`，镜像 `rabbitmq:3.13-management-alpine` |
| MinIO | `zuno-minio`，镜像 `minio/minio:RELEASE.2023-03-20T20-16-18Z` |
| Official Checkpointer | `langgraph.checkpoint.postgres.PostgresSaver`，真实 PostgreSQL DSN |
| 故障命令 | `docker stop --time 20 zuno-postgres zuno-rabbitmq zuno-minio` |
| 恢复命令 | `docker start zuno-postgres zuno-rabbitmq zuno-minio`，随后等待三项 health 为 `healthy` |
| 验证命令 | `python tools/scripts/verify_phase04_combined_service_fault.py` |
| 集成测试 | `pytest -q tests/integration/test_phase04_combined_service_fault.py -p no:cacheprovider` |

## 已验证行为

- 故障前在 PostgreSQL 同一事务写入 pending Outbox、Object Manifest 和 checkpoint primitive。
- 故障前用官方 `PostgresSaver.setup()` 初始化 schema，并写入带 marker 的 checkpoint、writes 和 delta channel history。
- 故障前向 durable RabbitMQ topology 发布 persistent marker，并在 MinIO 提交带 SHA-256 的可见对象。
- 三个容器同时停止后，新的 PostgreSQL connect、RabbitMQ connect 和 MinIO read 均失败，未降级到 SQLite、Local Queue 或 Fake Object Store。
- 三个容器启动后等待 Docker health 全部恢复，随后重新创建 sync/async `PostgresRuntime`、RabbitMQ Transport 和 MinIO client。
- RabbitMQ 重启后仍能消费并 ACK 故障前 persistent marker。
- 新建 Outbox Publisher 领取故障前 pending row，经 publisher confirm 写为 `published`；消费端把同一 event id 写入 tenant-scoped Inbox 后 ACK。
- PostgreSQL Outbox 状态、Object Manifest hash/visibility 和 checkpoint primitive marker 均与停机前一致。
- 官方 `PostgresSaver` 重连后 `get_tuple()` 读取到停机前 checkpoint id 和 marker，`list()` 保持 thread history 单条，`get_delta_channel_history()` 保留 marker channel。
- MinIO committed object 的 bytes 与 SHA-256 在重启前后保持一致。
- 演练 finally 路径保证三项服务恢复健康，并删除临时 topology、bucket 与数据库 marker；重复运行通过。

## 命令与结果

```text
python tools/scripts/verify_phase04_combined_service_fault.py
PHASE04 combined service fault verification passed.
```

## 剩余缺口

- 跨领域 Projection Replay beyond Product projection recovery subset 尚未最终收口。
- P04-T07 保持 `ready`，不是 completed。

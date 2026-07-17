# PHASE04 Outbox 发布策略证据

phase_id: PHASE04
task_id: P04-T03
date: 2026-07-17
status: partial_implementation_available
durable_backoff: passed
retry_exhaustion_dead_letter: passed
manual_replay_audit: passed
broker_outage_recovery: passed
outbox_backlog_visibility: passed
delivery_attempt_headers: passed

## 边界

本证据证明 PostgreSQL Outbox 发布 Owner 已具备持久重试、退避、重试耗尽、dead-letter、人工 replay 和 backlog 可观测能力，并通过真实 RabbitMQ 停机与恢复演练。它不单独关闭 P04-T03，也不关闭 PHASE04。

Queue ACK != Domain Success。Outbox 的 published、dead-letter 和 replay 都是基础设施交付事实，不得解释为消费端领域事务成功。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL | `zuno-postgres`，镜像 `postgres:16` |
| RabbitMQ | `zuno-rabbitmq`，镜像 `rabbitmq:3.13-management-alpine` |
| 数据库 | `postgresql+psycopg://postgres:postgres@localhost:5432/zuno` |
| AMQP | `amqp://guest:guest@localhost:5672/` |
| Alembic revision | `20260717_07` |
| 验证命令 | `python tools/scripts/verify_phase04_outbox_delivery_policy.py` |
| 集成测试 | `pytest -q tests/integration/test_phase04_outbox_delivery_policy.py -p no:cacheprovider` |

## 已验证行为

- Outbox claim 只领取 `next_attempt_at <= now()` 的 pending 记录，并继续使用 `FOR UPDATE SKIP LOCKED`。
- 每次确认发布或失败尝试都持久增加 `publish_attempts`；失败只保存异常类型代码，不保存可能包含 Secret 的异常文本。
- 第一次发布失败将记录恢复为 pending，清除 claim owner，并按指数策略设置 `next_attempt_at`。
- 退避窗口内记录只计入 delayed backlog，不能被其他 Publisher 提前领取。
- 达到本轮 `max_attempts` 后记录原子进入 `dead_letter`，记录 `dead_lettered_at`，并从可发布 backlog 中隔离。
- 人工 replay 仅接受 dead-letter 记录，记录 replay owner、时间和次数，重置本轮 retry count 后重新进入 pending。
- `docker stop zuno-rabbitmq` 期间连续两次真实发布失败，记录依次进入 delayed 和 dead-letter。
- `docker start zuno-rabbitmq` 且 health 恢复后，人工 replay 的同一 `event_id` 获得 publisher confirm 并进入 published。
- RabbitMQ 消息头携带总发布尝试、本轮 retry 和 replay 次数，恢复发布验证值为 `3/0/1`。
- 最终数据库保留 `publish_attempts=3`、`replay_count=1`、最后错误代码和 replay owner，且该 topic backlog 清零。
- 消费端先写入真实 Inbox receipt，再 ACK RabbitMQ；交付 receipt 不提升为领域成功。

## 命令与结果

```text
python tools/scripts/verify_phase04_alembic_migration.py
PHASE04 Alembic migration verification passed.
```

```text
python tools/scripts/verify_phase04_outbox_delivery_policy.py
PHASE04 outbox delivery policy verification passed.
```

```text
pytest -q tests/integration/test_phase04_outbox_delivery_policy.py -p no:cacheprovider
1 passed
```

## 剩余缺口

- P04-T03 仍需与完整领域 Handler adoption、运维指标出口和组合依赖故障总 Gate 一起审查，当前保持 `ready`。
- PHASE04 仍缺 official LangGraph PostgreSQL Checkpointer、完整恢复集和组合依赖故障闭环，不能标记 completed。

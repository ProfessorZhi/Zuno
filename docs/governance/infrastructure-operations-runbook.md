# Infrastructure Operations Runbook

status: implementation_available_for_phase04_operator_subscope
owner: Infrastructure
phase: PHASE04
last_verified: 2026-07-17

## 目标

本 Runbook 规定 PHASE04 真实 PostgreSQL、RabbitMQ 和 MinIO/S3 子范围的 health、readiness、capacity、backlog、恢复和证据更新方式。它不替代官方 LangGraph PostgreSQL Checkpointer Runbook；在官方 Checkpointer 子范围完成前，PHASE04 仍不得关闭。

## 边界

- Health 表示依赖可连接且基础操作成功。
- Readiness 表示依赖可承接当前产品流量或恢复演练，不等于领域成功。
- Capacity/Backlog 是运维指标，不是 Eval verdict。
- Queue ACK、Object Commit、Checkpoint Commit、HTTP 2xx 和 Audit Receipt 都不能解释为领域成功。
- Operator snapshot 只能写运行观测事实，不能写质量评分或用户结果判断。

## 每日检查

1. 启动真实依赖：

```powershell
docker compose -f infra/docker/docker-compose.yml up -d postgres rabbitmq minio
```

1. 检查容器状态：

```powershell
docker compose -f infra/docker/docker-compose.yml ps
```

1. 执行 operator readiness：

```powershell
python tools/scripts/verify_phase04_operator_readiness.py
```

1. 如果 readiness 失败，先按依赖定位，不更新 `implementation_available` 证据。

## PostgreSQL

检查项：

- `PostgresRuntime.sync_health()` 与 `PostgresRuntime.async_health()` 均为 ready。
- Pool size、checked out、overflow 可读。
- `InfrastructureRepository.outbox_backlog()` 能读取 ready、delayed、claimed、dead_letter 和 oldest pending。

恢复步骤：

1. 若连接失败，检查 `zuno-postgres` 是否 healthy。
2. 若 schema 缺失，先运行 Alembic 到 head，不允许用 `create_all()` 补表。
3. 若 backlog 异常增长，先查询 `infra_outbox_events` 的 status 分布，再执行已验证的 outbox reclaim/replay 流程。
4. 若 restore 演练失败，运行 `python tools/scripts/verify_phase04_backup_restore_replay.py` 取得最小复现。

## RabbitMQ

检查项：

- durable exchange/queue/DLQ 可声明。
- persistent message 可发布、读取、ACK。
- queue depth 可读，消费后归零。

恢复步骤：

1. 若连接失败，检查 `zuno-rabbitmq` health 和 `localhost:5672`。
2. 若 publish confirm 或 ACK 异常，保持 outbox row 为 pending/claimed，不得直接写领域成功。
3. 若 DLQ 增长，先读取 message version、tenant、trace header，再按 `phase04-outbox-delivery-policy.md` 的 manual replay 审计路径处理。
4. 恢复后运行 RabbitMQ focused verifier 和 operator readiness。

## MinIO/S3

检查项：

- bucket 可创建。
- object 可 stage、commit、read。
- raw content hash 与 Manifest hash 一致。

恢复步骤：

1. 若对象读取失败，先查 PostgreSQL Manifest visibility。
2. 若物理 object 存在但 Manifest 仍 staged，运行 MinIO Manifest reconciler verifier。
3. 若 hash 不一致，保持或进入 quarantine，不得覆盖 Manifest。
4. 删除必须先写 logical delete/Manifest，再做物理 purge。

## 结构化 Operator Snapshot

每个 snapshot 必须包含：

- `schema_version`
- `event_type`
- `trace_id`
- `tenant_id`
- dependency name
- health/readiness
- capacity/backlog
- failure owner
- retry owner
- recovery owner
- evidence ref
- `eval_verdict: None`

缺少 owner、trace 或 evidence ref 的 snapshot 不能作为 PHASE04 evidence。

## DR Profile

`docs/governance/infrastructure-dr-profile.yaml` 是 PHASE04 当前唯一 DR Profile。它必须声明每个恢复组件的 RPO、RTO、owner、recovery owner、verification command、evidence ref 和 current boundary。

DR Profile 只证明恢复策略、owner 和 cutover policy 已机器可验证；它不能替代真实 Restore、PITR、Projection Replay 或 official LangGraph PostgreSQL Checkpointer 恢复证据。

Cutover 默认 fail closed：`explicit_cutover_required=true` 且 `cutover_allowed_by_default=false`。缺少 Coordinator approval 时，不得把 isolated restore target 切为生产。

## 证据更新规则

- 只有真实依赖 verifier 通过，才能更新 `docs/evidence/`。
- 证据必须写明环境、命令、结果、边界和剩余缺口。
- P04-T07 operator 子范围可写 `implementation_available_for_operator_readiness_subscope`。
- 在官方 LangGraph PostgreSQL Checkpointer、完整 Backup/Restore/Replay 和 coordinator approval 完成前，不得把 PHASE04 写成 completed。

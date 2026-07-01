# PHASE06 Redis Runtime State Boundary

status: pending
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE06_redis-runtime-state-boundary
mode: tdd-implementation

## 目标

定义 `RuntimeStateStore` / `IngestRuntimeStateStore`，实现 local fallback，并提供 Redis adapter boundary / dependency probe。Redis 的职责是快、临时、高频状态：progress、event bridge、heartbeat、lease hint、rate limit、budget counter，不是业务事实源。

## 范围

- 定义 progress contract：ingest_task_id、status、phase、percent、message、updated_at。
- 定义 worker heartbeat contract。
- 定义 rate limit / budget counter local behavior。
- Redis boundary 能表达未配置、连接失败、target-blocked。
- API / service 可查询 progress。

## 禁止范围

- 不要求真实 Redis 服务。
- 不用 Redis 保存 source object、document version、parse job 或 index manifest 事实。
- 不用 Redis Streams 替代 RabbitMQ 主队列，除非单独 phase 和 tests 证明。

## 验收闸门

- local runtime state tests 通过。
- progress 可从 queued -> parsing -> indexing -> indexed / blocked / failed。
- heartbeat 可记录并查询。
- Redis 无配置时 target-blocked evidence 稳定。

## 验证命令

```powershell
pytest -q tests/knowledge/test_ingestion_async_infrastructure.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
git diff --check
```

## 需要先读取

- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/platform/`
- `src/backend/zuno/api/v1/workspace.py`
- `tests/api/test_workspace_durable_ingest_runtime.py`

## 需要修改的文件

- 新增 `src/backend/zuno/knowledge/runtime_state/` 或 `src/backend/zuno/platform/runtime_state/`
- 更新 `src/backend/zuno/knowledge/workers/`
- 更新 `src/backend/zuno/api/services/workspace_task_runtime.py`
- 更新 focused tests

## 执行拆解

1. 写 failing test：local progress lifecycle。
2. 实现 local runtime state store。
3. 写 failing test：worker heartbeat。
4. 实现 heartbeat / lease hint。
5. 写 Redis probe test。
6. 接入 worker progress updates。

## 多 agent 分工

- State Agent：审 progress / heartbeat contract。
- API Agent：审 status query compatibility。
- Verification Agent：跑 focused tests。

## 需要返回的证据

- progress timeline 示例。
- heartbeat record 示例。
- Redis target-blocked probe 示例。

## 停止条件

- Redis 被设计成事实源。
- Progress query 需要真实 Redis 才能通过。
- Runtime state 破坏 existing workspace task events。

# PHASE05 ParserWorker / IndexWorker Runtime

status: pending
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE05_parser-index-worker-runtime
mode: tdd-implementation

## 目标

实现本地可跑的 `ParserWorker` 和 `IndexWorker`。`ParserWorker` 消费 `parse_requested`，调用 `ParseGateway` 并持久化 parse / document facts；成功后发出 `index_requested`。`IndexWorker` 消费 `index_requested`，调用 `KnowledgeIndexRuntime` 并持久化 index manifest / chunks / citation lineage。

## 范围

- 新增 worker contracts / local runner。
- 支持 idempotency key 和 attempt_count。
- blocked / failed parse 不进入 index worker。
- worker 写入 store 和 object store，不绕过 Program 2 durable baseline。
- local async path 可由 tests 主动 drain，不需要后台 daemon。

## 禁止范围

- 不引入 Celery / Dramatiq / external worker framework。
- 不要求真实 RabbitMQ。
- 不删除同步 ingest fallback。
- 不把 worker 多进程部署写成 Current。

## 验收闸门

- focused test：`parse_requested` -> ParserWorker -> parse snapshot / document version / blocks。
- focused test：ParserWorker success -> `index_requested`。
- focused test：IndexWorker -> index manifest / chunks / citation lineage。
- focused test：blocked OCR / VLM parse 不创建 fake index。
- existing durable ingest tests 仍通过。

## 验证命令

```powershell
pytest -q tests/knowledge/test_ingestion_async_infrastructure.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
git diff --check
```

## 需要先读取

- `src/backend/zuno/knowledge/ingestion/gateway.py`
- `src/backend/zuno/knowledge/indexing/runtime.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`
- `tests/api/test_workspace_durable_ingest_runtime.py`

## 需要修改的文件

- 新增 `src/backend/zuno/knowledge/workers/`
- 新增或更新 `src/backend/zuno/knowledge/queue/`
- 更新 `src/backend/zuno/knowledge/storage/`
- 更新 `tests/knowledge/test_ingestion_async_infrastructure.py`

## 执行拆解

1. 写 failing test：ParserWorker consumes parse_requested。
2. 实现最小 ParserWorker。
3. 写 failing test：IndexWorker consumes index_requested。
4. 实现最小 IndexWorker。
5. 写 blocked parser test。
6. 跑 focused + existing durable ingest tests。

## 多 agent 分工

- Worker Agent：审 worker contracts 和 local drain model。
- Parse / Index Agent：审 lineage 是否完整。
- Verification Agent：跑 worker / durable ingest tests。

## 需要返回的证据

- parse_requested / index_requested message 示例。
- ParserWorker output records。
- IndexWorker output chunks 和 citation lineage。
- blocked no-fake-index evidence。

## 停止条件

- Worker 需要后台常驻服务才能测试。
- Worker path 绕过 `ParseGateway` 或 `KnowledgeIndexRuntime`。
- Worker path 造成重复 index 且没有 idempotency 策略。

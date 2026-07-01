# PHASE04 QueueBackend 与 RabbitMQ Boundary

status: pending
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE04_queue-backend-and-rabbitmq-boundary
mode: tdd-implementation

## 目标

定义 `QueueBackend`，实现可测试的 `LocalQueueBackend`，并新增 RabbitMQ adapter boundary / dependency probe。Program 3 的队列语义必须覆盖 parse、index、OCR / VLM、dead letter，不让 API 请求线程承担长任务。

## 范围

- 定义 queue message contract：message_id、topic、payload、attempt、status、created_at、available_at、ack token。
- topic：`parse_requested`、`index_requested`、`ocr_requested`、`vlm_requested`、`dead_letter`。
- `LocalQueueBackend` 支持 enqueue、consume、ack、nack(requeue)、dead_letter。
- RabbitMQ boundary 记录 expected capabilities：ack、publisher confirm、durable queue、dead letter exchange。

## 禁止范围

- 不要求真实 RabbitMQ 服务。
- 不让 Redis 代替业务事实源。
- 不把 queue message 当 DB fact source。
- 不改变 `/workspace/ingest` 同步兼容路径。

## 验收闸门

- focused queue tests 覆盖 enqueue / consume / ack / nack / dead_letter。
- duplicate delivery 不破坏 message identity。
- RabbitMQ 无配置时 dependency probe 返回 target-blocked evidence。
- QueueBackend payload 能承载 parse / index job id 和 idempotency key。

## 验证命令

```powershell
pytest -q tests/knowledge/test_ingestion_async_infrastructure.py -p no:cacheprovider
git diff --check
```

## 需要先读取

- `src/backend/zuno/knowledge/storage/contracts.py`
- `src/backend/zuno/knowledge/ingestion/contracts.py`
- `src/backend/zuno/knowledge/indexing/contracts.py`
- `tests/knowledge/test_parse_gateway_runtime.py`

## 需要修改的文件

- 新增 `src/backend/zuno/knowledge/queue/`
- 新增 `tests/knowledge/test_ingestion_async_infrastructure.py`
- 可能更新 `src/backend/zuno/knowledge/__init__.py`

## 执行拆解

1. 写 failing test：local queue enqueue / consume / ack。
2. 写 failing test：nack requeue 和 dead_letter。
3. 实现 queue contracts 和 `LocalQueueBackend`。
4. 实现 RabbitMQ dependency probe。
5. 跑 focused tests。

## 多 agent 分工

- Queue Agent：审 queue contract 和 topic naming。
- Reliability Agent：审 ack / nack / dead_letter semantics。
- Verification Agent：跑 focused queue tests。

## 需要返回的证据

- Queue message JSON 示例。
- dead letter record 示例。
- RabbitMQ target-blocked probe 示例。

## 停止条件

- 需要真实 RabbitMQ 才能让 local tests 通过。
- Queue payload 不能承载 idempotency / lineage。
- Queue 设计要求改 public API 且没有兼容策略。

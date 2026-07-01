# PHASE03 Parser Worker Runtime 与 Job Lifecycle

status: completed
program: zuno-production-document-ingestion-and-thread-foundation-v1
completed_at: 2026-07-01

## 目标

在不伪装成生产分布式队列的前提下，实现本地 parser worker / job lifecycle 基线：job id、状态机、重试、失败原因、metrics、snapshot、idempotency、blocked / dead-letter 语义和 replay。

## 范围

- 本地 in-process parser worker abstraction。
- Parser job 状态：accepted、running、succeeded、failed、blocked、retrying、cancelled、dead_letter。
- retry policy、attempt count、error class、last error、duration、parser diagnostics。
- snapshot / replay，用于测试和后续 workspace task 接入。
- Target-only 说明：生产 DB-backed job store、queue / outbox、worker lease、heartbeat、dead letter queue 和 reconciler。

## 禁止范围

- 不引入 Celery、Redis Queue、Kafka 或外部分布式 worker。
- 不把本地 worker 写成 production parser platform。
- 不把本地 snapshot 写成 DB-backed queue、outbox、lease 或生产 dead letter。
- 不改 workspace task runtime，除非只添加 parser job handoff contract。
- 不改变现有上传 API 行为。

## 验收闸门

- 同一个 source file + parser config 能生成稳定 job id 或 idempotency key。
- job failed 后可记录 failure snapshot。
- blocked adapter 不算 runtime crash，必须进入 blocked state。
- failed / blocked / cancelled / retrying / dead_letter 的语义必须区分清楚；blocked 表达能力或策略不可用，failed 表达 parser 运行失败。
- metrics 至少包含 count、duration、status、parser name、format。
- focused tests 覆盖 success、failure、blocked、retry、snapshot replay。

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge/test_parse_gateway_runtime.py tests/knowledge/test_index_jobs_runtime.py -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
```

## 需要先读取

- PHASE02 parser contract。
- `docs/architecture/document-ingestion-foundation.md`
- `src/backend/zuno/knowledge/ingestion/`
- `src/backend/zuno/knowledge/indexing/`
- `tests/knowledge/test_parse_gateway_runtime.py`
- `tests/knowledge/test_index_jobs_runtime.py`

## 需要修改的文件

- `src/backend/zuno/knowledge/ingestion/**`
- `src/backend/zuno/knowledge/indexing/**`
- `tests/knowledge/test_parse_gateway_runtime.py`
- `tests/knowledge/test_index_jobs_runtime.py`
- `.agent/programs/PHASE03_parser-worker-runtime-and-job-lifecycle.md`

## 执行拆解

1. 写 failing test：提交 parser job 后能查询 accepted / running / succeeded。
2. 写 failing test：unsupported adapter 返回 blocked job 和 blocked reason。
3. 写 failing test：parser exception 进入 failed job，保存 failure snapshot。
4. 写 failing test：retry 次数和 last error 可观测。
5. 写清 local `parse_idempotency_key` 语义：同一 source hash + parser config 重复请求不能生成冲突 IR。
6. 实现最小 in-process worker 和 job store，优先复用现有本地 snapshot / manifest 模式。
7. 接入 parser diagnostics 到 job result。
8. 在 README 或 phase evidence 中说明 outbox / lease / heartbeat / reconciler 仍是 Target。
9. 运行 focused tests，确认不会破坏 index job runtime。

## 多 agent 分工

- 可用 subagent 做 job lifecycle 只读设计对照。
- 可用 subagent 检查现有 index job manifest 是否已有可复用结构。
- 主线程负责代码实现、tests 和最终 diff。

## 需要返回的证据

- job lifecycle 状态机说明。
- retry / blocked / failure snapshot 示例。
- local idempotency key 和 Target-only outbox / lease / reconciler 边界。
- metrics 字段表。
- focused test 输出。

## PHASE03 证据

### TDD red 证据

先写 tests 后实现，第一次 focused run 失败点符合预期：

- `test_parse_gateway_records_parse_job_status_for_replay`：缺 `parse_idempotency_key`。
- `test_parse_gateway_target_blocked_adapter_enters_blocked_job_state`：target-blocked adapter 仍返回 `succeeded`。
- `test_parse_gateway_records_queue_snapshot_metrics_and_retry_lineage`：缺 `attempt_count`、failure snapshot 和 diagnostics。
- `test_parse_gateway_cancelled_job_snapshot_is_distinct_from_failed`：缺 `cancel_parse_job()`。

### Job lifecycle 状态机

Current local lifecycle 是 in-process snapshot，不是生产队列：

```text
submit_parse_job
  -> accepted
  -> running
  -> succeeded | failed

submit_parse_job(target-blocked adapter)
  -> accepted
  -> blocked

retry_parse_job
  -> retrying
  -> running
  -> succeeded | failed | dead_letter

cancel_parse_job
  -> cancelled
```

`blocked` 表达能力或策略不可用；`failed` 表达 parser 运行失败；`dead_letter` 表达超过本地 retry policy 后仍失败；`cancelled` 表达用户或策略取消。生产 DB queue、outbox、lease、heartbeat、reconciler 仍是 Target。

### Retry / blocked / failure snapshot 示例

- target-blocked OCR / VLM adapter 通过 `submit_parse_job()` 进入 `blocked`，`document=None`，`retryable=False`，snapshot 保留 `blocked_reason` 和 adapter boundary。
- empty source content 进入 `failed`，snapshot 保留 `failure_reason`、`last_error`、`error_class="ValueError"`、`failure_snapshot` 和 `parser_diagnostics`。
- failed job retry成功时保留 `previous_job_id`、`attempt_count=2` 和 `retrying -> running -> succeeded` timeline。
- 超过 local `max_attempts=2` 后仍失败时进入 `dead_letter`，不写成生产 dead letter queue。
- `cancel_parse_job()` 将 snapshot 更新为 `cancelled`，与 `failed` 区分。

### Idempotency / metrics 字段

| 字段 | Current 语义 |
| --- | --- |
| `parse_idempotency_key` | `workspace_id + source_sha256 + parser_id + parser_version + parser_config_hash` 的 sha256。 |
| `parse_attempt_id` | `attempt_{job_id}_{attempt}`，本地稳定 attempt 标识。 |
| `attempt_count` | 当前 job attempt 次数。 |
| `retry_policy` | 当前本地 `max_attempts=2`，生产 retry policy / queue policy 仍是 Target。 |
| `ParserJobMetrics.status` | job terminal status。 |
| `ParserJobMetrics.parser_name` | parser id。 |
| `ParserJobMetrics.format` | parser format。 |
| `ParserJobMetrics.block_count/table_count/figure_count` | parser output 计数。 |
| `ParserJobMetrics.warning_count/error_count/duration_ms` | diagnostics 与本地耗时。 |

### 修改文件

- `src/backend/zuno/knowledge/ingestion/contracts.py`
- `src/backend/zuno/knowledge/ingestion/gateway.py`
- `src/backend/zuno/knowledge/ingestion/README.md`
- `docs/architecture/document-ingestion-foundation.md`
- `tests/knowledge/test_parse_gateway_runtime.py`

### Focused test 结果

```powershell
pytest -q tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
# 18 passed

pytest -q tests/knowledge/test_index_jobs_runtime.py -p no:cacheprovider
# 5 passed

pytest -q tests/knowledge -p no:cacheprovider
# 31 passed
```

## 停止条件

- 需要生产队列或外部 DB 才能满足验收。
- parser worker 变更要求改 workspace task public API。
- retry 行为会导致非幂等重复索引，且无法在本 phase 内隔离。

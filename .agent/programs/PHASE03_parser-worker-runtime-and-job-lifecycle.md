# PHASE03 Parser Worker Runtime 与 Job Lifecycle

status: planned
program: zuno-production-document-ingestion-and-thread-foundation-v1

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

## 停止条件

- 需要生产队列或外部 DB 才能满足验收。
- parser worker 变更要求改 workspace task public API。
- retry 行为会导致非幂等重复索引，且无法在本 phase 内隔离。

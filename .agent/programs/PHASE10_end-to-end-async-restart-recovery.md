# PHASE10 End-to-End Async Restart Recovery

status: pending
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE10_end-to-end-async-restart-recovery
mode: tdd-implementation

## 目标

用一个端到端 focused test 证明 Program 3 的 async infrastructure baseline 不是散装接口：file -> object store -> queued ingest -> ParserWorker -> IndexWorker -> status -> task artifact -> feedback -> restart -> rehydrate -> cited answer 仍可用。

## 范围

- 使用 local store、local object store、local queue、local runtime state。
- 执行完整 async drain。
- 重启 service/runtime 后 rehydrate index 和 workspace product state。
- 证明 citation lineage、artifact content、feedback、events 不丢。

## 禁止范围

- 不要求真实外部服务。
- 不扩大到 Program 4 Memory / Tool / Security / GraphRAG 工作。
- 不把 flaky sleep / background daemon 当作验收。

## 验收闸门

- focused E2E test 先失败后通过。
- 重启后 file、parse job、parse snapshot、document version、index manifest、index chunks、task、events、artifact、feedback 均可查询。
- 重启后再次提问能生成带 `[1]` citation 的 artifact。
- blocked OCR / VLM scenario 仍不 fake index。

## 验证命令

```powershell
pytest -q tests/api/test_workspace_ingest_async_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/knowledge/test_ingestion_async_infrastructure.py -p no:cacheprovider
git diff --check
```

## 需要先读取

- `tests/api/test_workspace_durable_ingest_runtime.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/workers/`
- `src/backend/zuno/knowledge/queue/`
- `src/backend/zuno/knowledge/runtime_state/`

## 需要修改的文件

- `tests/api/test_workspace_ingest_async_runtime.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/workers/`
- 相关 support modules

## 执行拆解

1. 写 failing E2E async restart test。
2. 实现 missing service wiring。
3. 确保 deterministic local drain，不依赖 sleep。
4. 跑 E2E focused test。
5. 跑 existing durable recovery test。

## 多 agent 分工

- E2E Agent：审 full path。
- Runtime Agent：审 rehydrate 和 citation。
- Verification Agent：跑 API / knowledge focused tests。

## 需要返回的证据

- E2E test name 和结果。
- restart recovery 查询对象清单。
- cited artifact 内容片段。

## 停止条件

- E2E 需要真实 daemon 或外部服务。
- Rehydrate 只能恢复部分对象。
- Async path 与 sync durable path 出现不可兼容分歧。

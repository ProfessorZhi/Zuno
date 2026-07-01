# PHASE08 Async Ingest Status / Retry / Cancel / Replay

status: pending
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE08_async-ingest-status-retry-cancel-replay
mode: tdd-implementation

## 目标

为 async ingest 暴露 service contract 或 API surface，使前端和 runtime 能查询 ingest status，并能对 retry、cancel、replay 形成稳定语义。现有 `/workspace/ingest` response 必须保持兼容，新增字段只能 additive。

## 范围

- ingest status：queued、parsing、parsed、indexing、indexed、blocked、failed、dead_letter、cancelled。
- status query service / endpoint。
- retry parse / index service contract。
- cancel queued / running job contract。
- replay outbox / retry dead letter contract。
- response 中保留 parse_job_id、document_version_id、index_job_id、durable_status、progress_ref。

## 禁止范围

- 不做复杂 UI。
- 不改变现有 `/workspace/ingest` 必填字段。
- 不让 cancel 删除历史事实；只能写状态和 reason。
- 不绕过 ACL / workspace ownership check。

## 验收闸门

- API / service focused test 覆盖 status query。
- retry / cancel / replay 至少有 service contract 和 local test。
- retry 不生成冲突 document version。
- cancel 后不会继续 index。
- response shape 保持 additive compatibility。

## 验证命令

```powershell
pytest -q tests/api/test_workspace_ingest_async_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
git diff --check
```

## 需要先读取

- `src/backend/zuno/api/v1/workspace.py`
- `src/backend/zuno/api/dto/workspace.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/workers/`

## 需要修改的文件

- `src/backend/zuno/api/v1/workspace.py`
- `src/backend/zuno/api/dto/workspace.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- 新增 `tests/api/test_workspace_ingest_async_runtime.py`

## 执行拆解

1. 写 failing test：async ingest status query。
2. 实现 service / endpoint。
3. 写 failing test：cancel prevents index。
4. 实现 cancel state transition。
5. 写 failing test：retry / replay keeps lineage.
6. 实现 retry / replay contract。

## 多 agent 分工

- API Agent：审 response compatibility。
- Worker Agent：审 status transition 和 cancel / retry。
- Verification Agent：跑 API focused tests。

## 需要返回的证据

- API response before / after diff。
- status timeline 示例。
- retry / cancel / replay test 输出。

## 停止条件

- Public API 需要破坏性重命名。
- Cancel / retry 语义无法与 ParseGateway snapshot 对齐。
- Replay 会重复生成无法区分的 index chunks。

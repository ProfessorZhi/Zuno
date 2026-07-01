# PHASE07 Restart Recovery End-to-End

status: completed
program: zuno-enterprise-document-ingestion-platform-v2
phase: PHASE07_restart-recovery-end-to-end
mode: focused-e2e

## 目标

用一个端到端测试证明 file -> ingest -> task -> artifact -> feedback -> reset runtime -> rehydrate -> 查询 task/events/artifact/feedback -> 新 cited task 仍可用。

## 范围

- `tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_restart_rehydrates_cited_artifact_and_feedback`。
- local SQLite store 和 local object store。
- fresh `WorkspaceTaskRuntimeService` class state。

## 禁止范围

- 不用 monkeypatch 内存 payload 当作恢复证明。
- 不接真实外部 DB / queue / object store。
- 不把跨进程 worker recovery 写成 Current。

## 验收闸门

- reset 后旧 task snapshot 200。
- reset 后 events 仍含 feedback event。
- reset 后 artifact content 可读。
- reset 后新 task 可从 persisted index chunk 生成带 citation artifact。

## 验证命令

```powershell
pytest -q tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_restart_rehydrates_cited_artifact_and_feedback -p no:cacheprovider
```

## 需要先读取

- `tests/api/test_workspace_durable_ingest_runtime.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/indexing/runtime.py`

## 需要修改的文件

- `tests/api/test_workspace_durable_ingest_runtime.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/indexing/runtime.py`
- `src/backend/zuno/knowledge/storage/*`

## 执行拆解

1. 建立 temp SQLite / object store。
2. 完成 file、ingest、task、feedback。
3. reset in-memory state。
4. configure same store with `rehydrate=True`。
5. 查询旧 task/events/artifact/feedback。
6. 创建新 cited task 验证 persisted chunks 可用。

## 多 agent 分工

主线程直接执行；未拆子线程。

## 需要返回的证据

- post-restart task snapshot 恢复 artifact_ids 和 feedback_ids。
- post-restart artifact content 包含原文。
- post-restart cited artifact 包含 `[1]`。

## 停止条件

- 如果恢复只能靠原 class dict 则停止。
- 如果 citation lineage 不能重建则停止。

## PHASE07 Evidence

- `pytest -q tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_restart_rehydrates_cited_artifact_and_feedback -p no:cacheprovider`：通过。


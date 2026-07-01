# PHASE05 Index Persistence / Rehydrate

status: completed
program: zuno-enterprise-document-ingestion-platform-v2
phase: PHASE05_index-persistence-rehydrate
mode: tdd-implementation

## 目标

保存 index manifest、canonical index chunks 和 citation lineage，并让 fresh `KnowledgeIndexRuntime` 能从 SQLite chunks rehydrate 后继续服务 Agentic retrieval。

## 范围

- `SQLiteDurableIngestionStore.save_index_manifest()` / `save_index_chunk()` / `list_index_manifests()`。
- `KnowledgeIndexRuntime.rehydrate_index()`。
- `/workspace/ingest` 成功分支的 chunk persistence。

## 禁止范围

- 不接 Elasticsearch / Milvus / Neo4j。
- 不把 local rehydrate 写成 external index service Current。
- 不把重复 BM25 / vector / graph payload 伪装成三份不同 source truth。

## 验收闸门

- index manifest fresh store 可读。
- index chunks fresh store 可读，带 `citation_lineage`。
- fresh runtime rehydrate 后，新 task 能用 persisted chunks 生成带 citation 的 artifact。

## 验证命令

```powershell
pytest -q tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_restart_rehydrates_cited_artifact_and_feedback -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_answers_from_ingested_index_with_citations -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/knowledge/indexing/runtime.py`
- `src/backend/zuno/knowledge/agentic_graphrag.py`
- `tests/api/test_workspace_task_runtime.py`

## 需要修改的文件

- `src/backend/zuno/knowledge/indexing/runtime.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/storage/durable_ingestion_store.py`
- `tests/api/test_workspace_durable_ingest_runtime.py`

## 执行拆解

1. 在 restart recovery test 中要求 post-restart cited task。
2. 新增 `KnowledgeIndexRuntime.rehydrate_index()`。
3. 从 SQLite manifest/chunks 重建 knowledge space、latest manifest 和 local indexes。
4. 用 persisted chunk 同时 seed local Product V1 BM25 / vector / graph surfaces。

## 多 agent 分工

主线程直接执行；未拆子线程。

## 需要返回的证据

- green result：restart recovery test 和既有 cited answer test 通过。
- citation evidence：post-restart artifact 包含原始文档内容和 `[1]` citation。

## 停止条件

- 如果 rehydrate 需要外部 index service 才能继续则停止。
- 如果 citation lineage 丢失则停止。

## PHASE05 Evidence

- `pytest -q tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_restart_rehydrates_cited_artifact_and_feedback -p no:cacheprovider`：通过。
- `pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_answers_from_ingested_index_with_citations -p no:cacheprovider`：通过。


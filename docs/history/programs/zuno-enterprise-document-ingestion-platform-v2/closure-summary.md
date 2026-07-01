# Program Closure Summary

program: zuno-enterprise-document-ingestion-platform-v2
status: completed
closed_at: 2026-07-01

## Summary

Program 2 已完成。Zuno 的文档输入层从 Program 1 的 local runtime slice 推进到 Product V1 local durable ingestion baseline：`/workspace/file` 保存 source object 和 workspace file metadata；`/workspace/ingest` 继续走 `ParseGateway`，并持久化 parse job、snapshot、document version、document blocks、index manifest、index chunks 和 citation lineage；workspace task、events、artifact content/ref 和 feedback 可从 SQLite rehydrate。

## Current Evidence

- Source object 和 workspace file durable round-trip：`tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_file_register_persists_source_object_and_content_ref`。
- Parse / document / index durable round-trip：`test_workspace_ingest_persists_parse_document_index_and_chunks`。
- Blocked diagnostics without fake index：`test_target_blocked_parser_diagnostics_are_persisted_without_fake_index`。
- Restart recovery and cited artifact after rehydrate：`test_workspace_restart_rehydrates_cited_artifact_and_feedback`。
- Existing workspace task runtime compatibility：`tests/api/test_workspace_task_runtime.py`。

## Remaining Target

- Postgres、Redis、outbox、worker lease、MinIO / S3、external OCR / VLM、external vector / graph index、enterprise SSO / RBAC / DLP 仍是 Target / Production Scale Target。
- `SingleControllerDurableRuntime` 仍未声明为生产 DB-backed LangGraph runtime。
- Program 3-5 仍是 queued，未自动启动。

## Validation

本 archive 创建前已通过：

- `pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider`：`4 passed`。
- `pytest -q tests/knowledge -p no:cacheprovider`：`50 passed`。
- `pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider`：`8 passed`。
- `pytest -q tests/api -p no:cacheprovider`：`52 passed`。

最终 closure verifier 结果记录在本轮提交前终端输出。

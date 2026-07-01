# Zuno Production Document Ingestion and Thread Foundation V1 Closure Summary

> 状态：completed / archived。此目录是历史证据，不是当前 active program。

## 摘要

`zuno-production-document-ingestion-and-thread-foundation-v1` 已完成 PHASE01-PHASE08。本 program 将企业知识库文档入口从分散的本地 stub 推进到可验证的 ParseGateway / Document IR / parser job / index manifest / citation lineage 地基，并准备 Program 2 四条多线程施工提示词。

本 program 没有把生产级外部依赖伪装成 Current。生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index、生产 sandbox、外部 vault、外部 trace / eval 和 online eval 仍是 Remaining Target。

## Current Local Runtime Slice

```text
workspace file
  -> /api/v1/workspace/ingest
  -> ParseDocumentRequest
  -> ParseGateway.submit_parse_job()
  -> ParseJobSnapshot
  -> CanonicalDocumentIR
  -> KnowledgeIndexRuntime.index_document(parse_job_snapshot=...)
  -> IndexJobManifest
  -> retrieval payload
  -> evidence / citation provenance
```

Current evidence:

- `ParseGateway` exposes `parse_document()`、`submit_parse_job()`、`get_job_status()`、`get_job_snapshot()`、retry、cancel、blocked、failed 和 dead-letter 本地语义。
- `CanonicalDocumentIR` 已记录 source hash、document version、parser config hash、IR schema version、ACL、sensitivity、fallback 和 target-blocked diagnostics。
- Native `txt / md / csv / json / html / code` parser baseline 已有 deterministic blocks、tables、JSON pointer、HTML filtering、code metadata 和 malformed diagnostics。
- `KnowledgeIndexRuntime.index_document()` 已把 parse job lineage、diagnostics digest、document version、source hash、ACL 和 sensitivity 写入 `IndexJobManifest` 和 retrieval chunk `citation_lineage`。
- `/api/v1/workspace/ingest` 已走 `ParseGateway.submit_parse_job()`，并把 `parse_job`、`parse_snapshot` 和带 parse lineage 的 `index_job` 返回给 API caller。

## Workspace Ingest -> ParseGateway Evidence

Focused regression:

```powershell
pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_answers_from_ingested_index_with_citations -p no:cacheprovider
```

该测试先失败于 API response 缺少 `parse_job`，修复后通过。测试断言：

- `parse_job.status == succeeded`
- `parse_snapshot.status == succeeded`
- `parse_snapshot.parser_id != workspace_text_runtime`
- `index_job.parse_job_id == parse_job.job_id`
- `index_job.parse_attempt_id == parse_snapshot.parse_attempt_id`
- `index_job.document_version_id == parse_snapshot.source_provenance.document_version_id`
- `index_job.source_sha256 == parse_snapshot.source_provenance.source_sha256`

## Target-Blocked Parser / OCR / VLM Evidence

- PDF / Office / OCR / VLM 通过 adapter boundary、dependency probe、network policy、privacy gate、budget gate 和 blocked diagnostics 表达。
- OCR / VLM 当前只能作为 target-blocked derived enrichment，不能覆盖 deterministic parser source truth。
- 外部 Docling / PyMuPDF、Unstructured / MarkItDown、MinerU、OCR / VLM worker 没有部署到本仓库 runtime，因此不能写成 Current。

## Remaining Target Infrastructure

- 生产 DB-backed parser queue、object store、metadata DB、outbox、worker lease、heartbeat、dead letter queue 和 reconciler。
- 生产 Docling / MinerU / Unstructured worker、深度 OCR / layout / table / code extraction。
- 外部 Elasticsearch / Milvus / Neo4j、生产 LLM GraphRAG extraction、真实 community report pipeline 和 production reranker。
- 生产级 LangGraph persistence、semantic/vector Memory DB、真实 sandbox、外部 credential vault、真实网络代理、外部 trace/eval 和 online eval。

## Program 2 Handoff

Program 2 仍是 queued。四条 thread prompts 已归档：

- `thread-prompts/THREAD_A_memory-context.md`
- `thread-prompts/THREAD_B_tool-sandbox.md`
- `thread-prompts/THREAD_C_security-governance.md`
- `thread-prompts/THREAD_D_graphrag-index.md`

它们分别声明 branch、worktree、allowed paths、forbidden paths、focused tests、stop conditions、commit / push evidence，并把 Program 1 的 Document IR、parse lineage、index manifest、ACL、sensitivity 和 `citation_lineage` 作为共享输入事实。

## Verification Results

| Command | Result |
| --- | --- |
| `pytest -q tests/api/test_workspace_task_runtime.py::test_workspace_task_runtime_answers_from_ingested_index_with_citations -p no:cacheprovider` | pass, `1 passed, 1 warning` |
| `pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider` | pass, `8 passed, 1 warning` |
| `git diff --check` | pass; Windows line ending warnings only |
| `python tools/agent/render_architecture.py --check` | pass |
| `python tools/scripts/verify_docs_entrypoints.py` | pass |
| `python tools/scripts/verify_repo_structure.py` | pass |
| `python .agent/scripts/verify_agent_system.py` | pass |
| `python .agent/scripts/verify_doc_boundaries.py` | pass |
| `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1` | pass |
| `pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider` | pass, `59 passed` |
| `pytest -q tests/knowledge -p no:cacheprovider` | pass, `49 passed` |

## Release Metadata

```text
branch: codex/zuno-truth-source-production-readiness-baseline
archive: docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/
state_after_closure: no-active
final_commit: see git log after PHASE08 closure commit
push_status: pushed after PHASE08 closure commit
```

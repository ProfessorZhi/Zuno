# Program Roadmap

state: no-active
active_program: none
current_phase: none
latest_completed_program: `zuno-enterprise-document-ingestion-platform-v2`

## 总套件

本轮套件名：

`zuno-enterprise-agentic-graphrag-production-suite-v1`

核心目标：

```text
企业内部资料
  -> 多格式解析
  -> Document IR
  -> durable ingestion facts
  -> index / graph handoff
  -> Single Controller Agentic GraphRAG
  -> cited answer / artifact / trace
  -> automated enterprise KB eval
```

Zuno 最终产品不是 Basic RAG、GraphRAG、Agentic GraphRAG 三个并列模式。最终产品是企业知识库 Agentic GraphRAG Agent。Basic RAG 与静态 GraphRAG 是 Program 5 的评测 baseline。

## Program 1A：Document Ingestion 与线程地基

Program ID：`zuno-production-document-ingestion-and-thread-foundation-v1`

状态：completed / archived。

归档位置：

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

完成边界：`ParseGateway`、`CanonicalDocumentIR`、parser job snapshot、adapter boundary、native parser fixtures、index manifest lineage 和 citation lineage 已形成本地可验证地基。

## Program 1B / V2：Enterprise Document Ingestion Platform V2

Program ID：`zuno-enterprise-document-ingestion-platform-v2`

状态：completed / archived。

归档位置：

- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`

完成边界：

- `/workspace/file` 保存 local source object、source hash、storage uri 和 workspace file metadata。
- `/workspace/ingest` 继续走 `ParseGateway.submit_parse_job()`。
- SQLite durable store 保存 parse job、snapshot、document version、document blocks、index manifest、index chunks 和 citation lineage。
- blocked parser diagnostics 落库，blocked 不创建 fake index。
- workspace task、events、artifact content/ref 和 feedback 可从 durable store rehydrate。
- restart recovery focused test 证明 fresh service/runtime 后仍能查询 task / events / artifact / feedback，并用 persisted chunks 生成 cited artifact。

Remaining Target：

- Postgres、object store、queue / outbox、worker lease、external OCR / VLM、external index、production parser worker 和 reconciler。

## Program 3：Runtime Subsystems Parallel

Program ID：`zuno-runtime-subsystems-parallel-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM03_runtime-subsystems-parallel.md`。

Program 3 必须在新一轮启动门重新确认 UI 目标模式、worktree、branch、允许范围、禁止范围和验证闸门后才能 active。

## Program 4：Planning Integration

Program ID：`zuno-agent-planning-integration-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM04_agent-planning-integration.md`。

## Program 5：Enterprise Knowledge Eval Benchmark

Program ID：`zuno-enterprise-knowledge-eval-benchmark-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM05_enterprise-knowledge-eval-benchmark.md`。

## 验证基线

no-active 文档与 workflow 基线：

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

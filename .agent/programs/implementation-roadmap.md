# Program Roadmap

state: active
active_program: `zuno-enterprise-ingestion-async-infrastructure-v1`
current_phase: `PHASE01_truth-source-and-async-gap-audit.md`
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
  -> async parse / index workers
  -> index / graph handoff
  -> Single Controller Agentic GraphRAG
  -> cited answer / artifact / trace
  -> automated enterprise KB eval
```

Zuno 最终产品不是 Basic RAG、GraphRAG、Agentic GraphRAG 三个并列模式。最终产品是 AgentChat 驱动的企业知识库 Agentic GraphRAG Agent。用户在勾选知识库时只选择标准检索 / 深度检索；建库时决定基础索引、图谱增强索引和 OCR / 多模态解析能力；Agent 后端自动选择 RAG / GraphRAG / re-query / rerank。Basic RAG 与静态 GraphRAG 是 Program 6 的评测 baseline。

## Program 1：Document Ingestion Foundation

Program ID：`zuno-production-document-ingestion-and-thread-foundation-v1`

状态：completed / archived。

归档位置：

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

完成边界：`ParseGateway`、`CanonicalDocumentIR`、parser job snapshot、adapter boundary、native parser fixtures、index manifest lineage 和 citation lineage 已形成本地可验证地基。

## Program 2：Durable Ingestion Product V1

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

## Program 3：Enterprise Ingestion Async Infrastructure

Program ID：`zuno-enterprise-ingestion-async-infrastructure-v1`

状态：active。

当前 phase：

- `.agent/programs/PHASE01_truth-source-and-async-gap-audit.md`

目标：把 Program 2 的 SQLite / local synchronous durable baseline 升级为企业文档输入异步基础设施 baseline。Program 3 不是否定 Program 2 closure，而是补齐文档入口层最核心的企业化运行面：

- `DurableIngestionStore` protocol / interface。
- SQLite 默认实现继续通过现有 tests。
- PostgreSQL-compatible adapter boundary / dependency probe / target-blocked evidence。
- `ObjectStore` protocol，支持 `save_bytes`、`save_text`、`read_bytes`、`read_text`、`open_stream`、`get_metadata`、`verify_sha256`。
- `LocalObjectStore` 支持 binary source、IR artifact、diagnostics artifact 和 artifact content。
- `QueueBackend` protocol、`LocalQueueBackend`、RabbitMQ adapter boundary / dependency probe。
- `ParserWorker` / `IndexWorker` local runner。
- `RuntimeStateStore` protocol、local fallback、Redis adapter boundary / dependency probe。
- outbox、dead letter、worker lease / heartbeat、reconciler。
- ingest status / retry / cancel / replay service contract。
- OCR / VLM worker boundary，默认 target-blocked diagnostics，不 fake success。

验收主链路：

```text
file -> object store -> queued ingest -> parser worker -> ParseGateway
     -> parse snapshot / document version / blocks
     -> index worker -> index manifest / chunks / citation lineage
     -> ingest status query -> restart recovery -> reconciler check
```

## Program 4：Runtime Subsystems Parallel

Program ID：`zuno-runtime-subsystems-parallel-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM04_runtime-subsystems-parallel.md`。

Program 4 在 Program 3 完成后启动，使用多线程模式并行推进 Memory / Context、Tool / Sandbox、Security / Governance、GraphRAG / Index。它不再替文档输入层补 queue、worker、outbox 或 reconciler。GraphRAG / Index 线程需要产出知识库索引能力与 retrieval profile 的基础契约：标准检索、深度检索、graph_index_not_ready 降级和 trace 字段。

## Program 5：Planning Integration

Program ID：`zuno-agent-planning-integration-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM05_agent-planning-integration.md`。

Program 5 合并 Program 4 成果，实现 Single Controller / Single `GeneralAgent` 内部的 planning、ReAct、reflection 和 replan 闭环。核心验收是 Agentic Retrieval Planner 能消费每个知识库的标准检索 / 深度检索 profile，自动生成 query rewrite、retriever selection、GraphRAG expansion、reflection、re-query 和 cited answer 轨迹。

## Program 6：Enterprise Knowledge Eval Benchmark

Program ID：`zuno-enterprise-knowledge-eval-benchmark-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM06_enterprise-knowledge-eval-benchmark.md`。

Program 6 建设企业知识库问答自动化评测，对比 Basic RAG baseline、Static GraphRAG baseline、标准检索 profile、深度检索 profile 和 Agentic GraphRAG target。

## Program 3 验证基线

Program 3 开轮和每个 phase 至少运行最小有效验证；最终 closure 至少运行：

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

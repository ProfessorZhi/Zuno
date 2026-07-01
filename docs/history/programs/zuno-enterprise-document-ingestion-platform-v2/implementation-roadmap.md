# Program Roadmap

state: completed
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
  -> index / graph handoff
  -> Single Controller Agentic GraphRAG
  -> plan / react / observe / reflect / replan
  -> cited answer / artifact / trace
  -> automated enterprise KB eval
```

Zuno 最终产品不是 Basic RAG、GraphRAG、Agentic GraphRAG 三个并列模式。最终产品是企业知识库 Agentic GraphRAG Agent。Basic RAG 与静态 GraphRAG 是 Program 5 的评测 baseline。

## Program 1：Document Ingestion 与线程地基

Program ID：`zuno-production-document-ingestion-and-thread-foundation-v1`

状态：completed / archived。

归档位置：

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

完成边界：

- `ParseGateway`、`CanonicalDocumentIR`、parser job snapshot、adapter boundary、native parser fixtures、index manifest lineage 和 citation lineage 已形成本地可验证地基。
- `/api/v1/workspace/ingest` 已走 `ParseGateway.submit_parse_job()`，并把 parse job snapshot 传给 `KnowledgeIndexRuntime.index_document()`。
- 后续 runtime subsystems 四条 thread prompts 已归档到 `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/thread-prompts/`，启动时必须按新队列刷新。

Remaining Target：

- 生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index、production parser worker 和 reconciler。

## Program 2：Enterprise Document Ingestion Platform V2

Program ID：`zuno-enterprise-document-ingestion-platform-v2`

状态：completed / archived。归档位置：`docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`。

业务口径：这是 Program 2，不是重写或篡改已归档 Program 1。Program 1 已经完成 `workspace ingest -> ParseGateway -> Document IR -> Index Manifest -> Citation Lineage` local runtime slice；Program 2 的目标是把这条链路升级为企业级文档输入与持久化平台雏形。

目标：文件由后端持久化保存，parse / index / job 状态落库，OCR / VLM / PDF / Office 有明确 adapter boundary，服务重启后文档、任务、索引、artifact、feedback 和引用 lineage 不丢。

成熟度边界：

```text
Current Local Slice
  已完成 Program 1 的 workspace file -> ParseGateway -> Document IR -> index manifest -> citation lineage。
  已完成 Program 2 的 SQLite / local file store durable ingestion baseline。

Launchable Prototype Target
  SQLite / SQLModel backed local durable store + local file store + in-process runner。
  后端持久化 source object、workspace file、parse job、document version、document blocks、index manifest、index chunks、citation lineage、workspace task、events、artifact content/ref 和 feedback。
  服务重启后文档输入层核心业务事实可查询，并可 rehydrate 本地 retrieval index。

Production Scale Target
  Postgres、object store、queue/outbox/worker、worker lease、external OCR/VLM、external index、SSO/RBAC/DLP、OTel/LangSmith、online eval 和多租户运维。
```

Program 2 已关闭文档输入层的事实源和重启恢复，为后续 Memory / Tool / Security / GraphRAG 四线程继续加能力提供持久化输入地基。PHASE01-PHASE08 的详细证据保留在本归档目录。

## Program 3：Runtime Subsystems Parallel

Program ID：`zuno-runtime-subsystems-parallel-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM03_runtime-subsystems-parallel.md`。

目标：在 Program 1 的解析和索引地基稳定、Program 2 的 enterprise ingestion persistence baseline 完成后，使用多线程模式并行推进四个低耦合子系统。

线程：

1. Memory / Context：分层记忆、上下文压缩、semantic fallback、privacy delete、sensitive exclusion、memory eval。
2. Tool / Sandbox：Tool Control Plane、approval ledger、network policy、credential-ref-only、sandbox adapter。
3. Security / Governance：prompt injection、retrieval gate、tool gate、output DLP、cross-workspace leakage tests。
4. GraphRAG / Index：enterprise knowledge schema、RRF/rerank trace、GraphRAG baseline runner、external index adapter boundary。

Program 3 不直接重写 `GeneralAgent` 主循环；它只产出可被 Program 4 合并的模块能力、tests 和 evidence。

## Program 4：Planning Integration

Program ID：`zuno-agent-planning-integration-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM04_agent-planning-integration.md`。

目标：把 Program 3 的 Memory、Tool、安全、GraphRAG 能力合并进 Single Controller Agent，并实现真实 `plan -> ReAct -> observe -> reflect -> replan` 闭环。

Program 4 是高冲突 program，默认由主线程集中执行，必要时只用 subagent 做只读审计。它不得把 Zuno 产品 runtime 改成多 Agent。

## Program 5：Enterprise Knowledge Eval Benchmark

Program ID：`zuno-enterprise-knowledge-eval-benchmark-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM05_enterprise-knowledge-eval-benchmark.md`。

目标：建设企业知识库问答自动化评测系统，对同一 corpus 和 question set 比较 Basic RAG baseline、Static GraphRAG baseline 和 Agentic GraphRAG target。

## 当前 Program 2 启动门槛

Program 2 已启动。PHASE01 执行前必须：

1. 重新确认 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
2. 确认本轮目标是 Program 2 企业级文档输入与持久化平台，而不是启动四线程 Runtime Subsystems。
3. 只读审计 `WorkspaceTaskRuntimeService`、`ParseGateway`、`KnowledgeIndexRuntime`、platform storage / DB 和 tests。
4. 只在 Program 2 closure 后刷新 Program 1 归档 thread prompts 并启动 Program 3。

## 验证基线

no-active 文档与 workflow 基线：

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

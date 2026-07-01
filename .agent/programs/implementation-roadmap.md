# Program Roadmap

state: no-active
active_program: none
current_phase: none
latest_completed_program: `zuno-production-document-ingestion-and-thread-foundation-v1`

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

Zuno 最终产品不是 Basic RAG、GraphRAG、Agentic GraphRAG 三个并列模式。最终产品是企业知识库 Agentic GraphRAG Agent。Basic RAG 与静态 GraphRAG 是 Program 4 的评测 baseline。

## Program 1：Document Ingestion 与线程地基

Program ID：`zuno-production-document-ingestion-and-thread-foundation-v1`

状态：completed / archived。

归档位置：

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

完成边界：

- `ParseGateway`、`CanonicalDocumentIR`、parser job snapshot、adapter boundary、native parser fixtures、index manifest lineage 和 citation lineage 已形成本地可验证地基。
- `/api/v1/workspace/ingest` 已走 `ParseGateway.submit_parse_job()`，并把 parse job snapshot 传给 `KnowledgeIndexRuntime.index_document()`。
- Program 2 四条 thread prompts 已归档到 `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/thread-prompts/`。

Remaining Target：

- 生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index、production parser worker 和 reconciler。

## Program 2：Runtime Subsystems Parallel

Program ID：`zuno-runtime-subsystems-parallel-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM02_runtime-subsystems-parallel.md`。

目标：在 Program 1 的解析和索引地基稳定后，使用多线程模式并行推进四个低耦合子系统。

线程：

1. Memory / Context：分层记忆、上下文压缩、semantic fallback、privacy delete、sensitive exclusion、memory eval。
2. Tool / Sandbox：Tool Control Plane、approval ledger、network policy、credential-ref-only、sandbox adapter。
3. Security / Governance：prompt injection、retrieval gate、tool gate、output DLP、cross-workspace leakage tests。
4. GraphRAG / Index：enterprise knowledge schema、RRF/rerank trace、GraphRAG baseline runner、external index adapter boundary。

Program 2 不直接重写 `GeneralAgent` 主循环；它只产出可被 Program 3 合并的模块能力、tests 和 evidence。

## Program 3：Planning Integration

Program ID：`zuno-agent-planning-integration-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM03_agent-planning-integration.md`。

目标：把 Program 2 的 Memory、Tool、安全、GraphRAG 能力合并进 Single Controller Agent，并实现真实 `plan -> ReAct -> observe -> reflect -> replan` 闭环。

Program 3 是高冲突 program，默认由主线程集中执行，必要时只用 subagent 做只读审计。它不得把 Zuno 产品 runtime 改成多 Agent。

## Program 4：Enterprise Knowledge Eval Benchmark

Program ID：`zuno-enterprise-knowledge-eval-benchmark-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM04_enterprise-knowledge-eval-benchmark.md`。

目标：建设企业知识库问答自动化评测系统，对同一 corpus 和 question set 比较 Basic RAG baseline、Static GraphRAG baseline 和 Agentic GraphRAG target。

## 下一轮启动门槛

启动 Program 2 前必须：

1. 重新确认 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
2. 重新确认用户要打开多线程模式，而不是挂机模式。
3. 如使用 Program 1 归档提示词，先复制或刷新到 `.agent/programs/thread-prompts/`，再确认真实 Codex UI 目标模式线程。
4. 从 `PHASE01` 建立新的 active program truth source，并同步 verifier / tests。

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

# Program Roadmap

state: active
active_program: `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
current_phase: `PHASE01_truth-source-and-merge-plan.md`
latest_completed_program: `zuno-enterprise-document-ingestion-platform-v2`

## 总套件

本轮套件名：

`zuno-enterprise-agentic-graphrag-production-suite-v1`

当前执行形态收敛为三个前台 program：

1. Program 1：Document Ingestion Foundation，completed / archived。
2. Program 2：Durable Ingestion Product V1，completed / archived。
3. Program 3 Mega：Launchable Enterprise Agentic GraphRAG Full Closure，active。

原 Program 3 / 4 / 5 / 6 已合并进 Program 3 Mega：

- `zuno-enterprise-ingestion-async-infrastructure-v1` -> merged_into mega program。
- `zuno-runtime-subsystems-parallel-v1` -> merged_into mega program。
- `zuno-agent-planning-integration-v1` -> merged_into mega program。
- `zuno-enterprise-knowledge-eval-benchmark-v1` -> merged_into mega program。

核心目标：

```text
企业内部资料
  -> 多格式解析
  -> Document IR
  -> durable ingestion facts
  -> async parse / index workers
  -> index / graph handoff
  -> Memory & Context Engine
  -> Capability Layer
  -> Planning & Control Runtime
  -> Single Controller Agentic GraphRAG
  -> cited answer / artifact / trace / cost / eval
  -> launchable product baseline
```

Zuno 最终产品不是 Basic RAG、GraphRAG、Agentic GraphRAG 三个并列模式。最终产品是 AgentChat 驱动的企业知识库 Agentic GraphRAG Agent。Agent Core 公式是 `Model Gateway + Memory & Context Engine + Planning & Control Runtime + Capability Layer + Governance / Trace / Eval Envelope`。用户在勾选知识库时只选择标准检索 / 深度检索；建库时决定基础索引、图谱增强索引和 OCR / 多模态解析能力；Agent 后端自动选择 RAG / GraphRAG / re-query / rerank、Skill、MCP 和工具能力。Basic RAG 与静态 GraphRAG 是 eval baseline。

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

## Program 3 Mega：Launchable Enterprise Agentic GraphRAG Full Closure

Program ID：`zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`

状态：active。

当前 phase：

- `.agent/programs/PHASE01_truth-source-and-merge-plan.md`

目标：把原 Program 3-6 合并为一个可执行到 closure 的全链路 program，完成 launchable enterprise Agentic GraphRAG product baseline。它不是要求部署真实生产集群，而是要求每个关键层都有 local runnable implementation、adapter boundary、dependency probe / target-blocked evidence、focused tests、E2E 闭环、trace/eval/cost 记录和文档成熟度边界。

完成后前台结论必须是：

```text
Launchable enterprise Agentic GraphRAG product baseline completed.
Production scale external deployments remain replaceable targets.
```

## Mega Program Phase Gate

1. `PHASE01_truth-source-and-merge-plan.md`
   - 审计当前 Program 3 active 状态与 queued Program 4-6。
   - 输出 merge map、owner map、shared file map、workstream map、PR / commit plan。
   - 确认目标架构公式和 Product Baseline 完成标准。
2. `PHASE02_shared-contract-freeze.md`
   - 冻结 AgentRun、ContextPack、RetrievalProfile、RetrievalDecision、EvidenceBundle、CitationLineage、FileInputFormat、SourceObject、BinarySourceObject、ObjectStoreRef、ObjectStoreResult、ParserCapabilityStatus、ParserDependencyProbe、ParserWorkerSpec、ParserWorkerResult、ParseJobStatus、ParseAttempt、IndexWorkerSpec、IndexWorkerResult、QueueMessage、QueueBackendResult、OutboxEvent、DeadLetterRecord、ReconcilerFinding、OCRVLMEnrichmentResult、KnowledgeSpaceConfig、FileIngestionStatus、ChangeImpactPreview、CapabilityCard、CapabilityPolicy、CapabilityRiskProfile、CapabilityAuditEvent、SkillCard、ToolCard、PlanStep、ReflectionVerdict、ReplanDecision、ReflexionLesson、ScenarioSummary、TraceSummary、TraceRecord、ConversationRunMetrics、StageMetrics、IngestionMetrics、RetrievalMetrics、PlanningMetrics、SecurityMetrics、EvalComparisonReport 和 CostMetric。
3. `PHASE03_enterprise-ingestion-async-infrastructure.md`
   - DurableIngestionStore、binary ObjectStore、LocalObjectStore save/read/verify bytes、QueueBackend、LocalQueueBackend、RabbitMQ boundary / probe、Redis runtime state boundary、ParserWorker / IndexWorker、Outbox、DeadLetter、Reconciler、PDF / Office / image / scanned / binary async ingestion target、OCR/VLM blocked boundary、file status lifecycle、ingest status / retry / cancel / replay。
4. `PHASE04_knowledge-retrieval-and-graphrag-profile.md`
   - 标准检索 / 深度检索、RetrievalProfile、RetrievalDecision、EvidenceBundle、CitationLineage、deep_without_graph fallback。
5. `PHASE05_memory-context-engine.md`
   - Working / Session / Episodic / Semantic / Procedural / Reflexion / Governance memory、ContextPack、structured extraction、hierarchical summary、evidence-bound summary、budget-aware packing、sensitive exclusion。
6. `PHASE06_capability-skill-tool-mcp-layer.md`
   - Capability Registry、CapabilityPolicy、CapabilityRiskProfile、CapabilityAuditEvent、SkillCard、Knowledge / Tool / MCP / External API / File / Code / Browser / Artifact capabilities。
7. `PHASE07_security-governance-envelope.md`
   - Input / Retrieval / Tool / Output gates、ACL、workspace isolation、prompt injection、DLP、approval、audit。
8. `PHASE08_model-gateway-cost-latency.md`
   - Model Gateway、provider abstraction、token / latency / cost estimate、timeout、retry、trace fields。
9. `PHASE09_planning-contract-and-strategy-selector.md`
   - PlanStep、PlanState、StrategySelectorOutput、SelectedSkill、CapabilityPlan、RetrievalPlan、ReflectionVerdict、ReplanDecision、ReflexionLesson。
10. `PHASE10_react-reflection-replan-reflexion-runtime.md`
   - ReAct step runner、Reflection gate、Dynamic Replan、Reflexion candidate 和 trace events。
11. `PHASE11_workspace-product-api-frontend-sync.md`
   - 后端新增 profile / plan / trace / capability / eval 字段与 workspace API / frontend API types 最小同步，并补 KnowledgeSpaceConfig、创建 Wizard、Settings tabs、file status、parser dependency probe、PDF / Office / OCR provider target、retry / cancel / reparse / reindex / rebuild_graph actions 和 Change Impact Preview 的产品契约。
12. `PHASE12_end-to-end-product-runtime.md`
   - Upload / ingest / parse / index / retrieval / planning / skill / artifact / trace / feedback / restart rehydrate E2E，并生成用户可感知 scenario summary / trace summary fixture；覆盖 native formats、PDF / Office target-blocked、image / scanned OCR/VLM blocked no fake index、binary object traceability、local queue / worker lifecycle、dead_letter / reconciler fixture。
13. `PHASE13_eval-trace-cost-benchmark.md`
   - ConversationRunMetrics、StageMetrics、IngestionMetrics、retrieval / answer / planning / replan / reflection / reflexion / security / cost / latency metrics and regression report；回答文件 blocked、PDF / Office / OCR no fake index、binary sha256 traceability、parse / index duration、deep retrieval cost source 和 OCR/VLM provider blocked 是否正确。
14. `PHASE14_docs-architecture-expansion.md`
   - agent core runtime、capability and skill、agentic retrieval planner、input-layer-and-document-processing、knowledge-space-product-configuration、eval observability and cost 等架构展开文档。
15. `PHASE15_verification-archive-closure.md`
   - full verification、archive、no-active、closure summary、commit、push。

## 目标架构拼接矩阵

| 目标架构层 | 对应 Phase | 主要产物 | 下游消费者 |
|---|---|---|---|
| Product Surface | PHASE11, PHASE12 | knowledge profile request、KnowledgeSpaceConfig、Change Impact Preview、task snapshot、artifact citation、feedback、scenario summary | 用户、AgentChat、E2E、Eval |
| Input / Async Infrastructure | PHASE03 | binary ObjectStore、QueueBackend、ParserWorker、IndexWorker、Outbox、DeadLetter、Reconciler、OCR/VLM blocked boundary、file lifecycle | Knowledge Retrieval、Product API、E2E、Eval、Restart Recovery |
| Knowledge Capability | PHASE04 | RetrievalProfile、RetrievalDecision、EvidenceBundle、CitationLineage | Planning、Reflection、Output Gate、Eval |
| Memory & Context Engine | PHASE05 | ContextPack、多重 memory、structured extraction、hierarchical summary、evidence-bound compression、Reflexion review path | Strategy Selector、ReAct、Reflexion |
| Capability Layer | PHASE06 | CapabilityRegistry、CapabilityPolicy、SkillCard、ToolCard、MCPCapability、KnowledgeCapability、ArtifactCapability | Skill selection、Tool Gate、Retrieval Gate、ReAct runner |
| Security / Governance Envelope | PHASE07 | Input / Retrieval / Tool / Output gates、audit verdict | Planning、Retrieval、Tool runtime、Output safety、Eval |
| Model Gateway | PHASE08 | model category、provider boundary、cost / latency / token metrics | Planning budget、Retrieval rerank、Eval judge |
| Planning & Control Runtime | PHASE09, PHASE10 | StrategySelector、PlanStep、Reflection、Dynamic Replan、ReflexionLesson | Product runtime、Trace、E2E |
| Eval / Trace / Cost | PHASE13 | ConversationRunMetrics、StageMetrics、IngestionMetrics、metrics、trace、regression report、release baseline | Closure、README / architecture evidence |
| Docs / Archive | PHASE14, PHASE15 | architecture docs、production readiness、closure summary、archive | Future programs、repo verifiers |

## 串并行策略

必须串行：

1. PHASE01：Program 合并和 owner map。
2. PHASE02：Shared contract freeze。
3. PHASE09-PHASE10：Planning runtime integration，由单 owner 控制。
4. PHASE11：Workspace Product API / Frontend Sync，由 Coordinator 控制共享 API。
5. PHASE12：E2E Product Runtime，由 Coordinator 集成。
6. PHASE15：Verification / Archive / Closure，由 Coordinator 收口。

可并行：

- PHASE03 Workstream A：Input / Async Infrastructure。
- PHASE04 Workstream B：Knowledge / Retrieval / GraphRAG。
- PHASE05 Workstream C：Memory / Context。
- PHASE06 Workstream D：Capability / Skill / Tool / MCP。
- PHASE07 Workstream E：Security / Governance。
- PHASE08 和 PHASE13 Workstream G：Model Gateway、Eval / Trace / Cost。
- PHASE14 Workstream I 可以起草 supporting docs，但 architecture.md / README / AGENTS 最终 wording 归 Coordinator。

共享文件锁：

- Coordinator only：`.agent/programs/current.md`、`implementation-roadmap.md`、`closure-checklist.md`、README、AGENTS、`docs/architecture/architecture.md`、`docs/architecture/production-readiness.md`、`src/backend/zuno/api/services/workspace_task_runtime.py`、public API DTO、frontend workspace API type。
- Workstream owner files：各自 backend layer、tests 和 supporting docs。
- 任何 workstream 需要改 shared contract，必须先回到 PHASE02 contract review。

## Workstream 与 PR / commit 分组

并行 workstream：

- Coordinator：Program 状态、共享契约、roadmap、README / AGENTS、共享 API、最终 merge、验证、commit / push、archive。
- A：Input / Async Infrastructure。
- B：Knowledge / Retrieval / GraphRAG。
- C：Memory / Context。
- D：Capability / Skill / Tool / MCP。
- E：Security / Governance。
- F：Planning / Agent Runtime。
- G：Eval / Trace / Cost。
- H：Product API / Frontend Minimal Sync。
- I：Docs / Verifier。

建议 PR / commit 分组：

```text
PR-00 program open + contracts
PR-A1 input interfaces
PR-A2 parser/index workers + outbox/reconciler
PR-B1 retrieval profiles
PR-B2 evidence/citation + deep fallback
PR-C1 Memory ContextPack
PR-C2 ReflexionMemory review path
PR-D1 Capability registry
PR-D2 SkillCard fixtures + Tool/MCP boundary
PR-E1 security gates
PR-E2 ACL/DLP/prompt injection tests
PR-F1 planning contracts + strategy selector
PR-F2 react/reflection/replan/reflexion runtime
PR-G1 trace/cost metrics
PR-G2 benchmark/release baseline
PR-H1 API/frontend minimal contract sync
PR-Z1 E2E scenarios
PR-Z2 docs/verifier/archive closure
```

## 验证基线

开轮与每个 phase 至少运行最小有效验证；最终 closure 至少运行：

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
pytest -q tests/agent -p no:cacheprovider
pytest -q tests/api -p no:cacheprovider
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

# Goal04 PHASE18 Startup Audit

phase_id: PHASE18
phase_name: Agentic GraphRAG Inner Loop
phase_status: in_progress
branch: codex/goal04-phase18-agentic-graphrag
base_main_sha: 4d14ae9e8cd953359c82e51d55279cc123ab47ae
phase17_merge_sha: 4d14ae9e8cd953359c82e51d55279cc123ab47ae
worktree: C:\Users\Administrator\.codex\worktrees\goal04-phase18\Zuno
started_at: 2026-07-28
production_readiness: not established

## 启动结论

PHASE17 PR C 已通过 merge commit `4d14ae9e8cd953359c82e51d55279cc123ab47ae` 合并到 `main`，PHASE18 的依赖 `PHASE12 + PHASE17` 已满足。PR D 从该最新 `main` 创建独立分支 `codex/goal04-phase18-agentic-graphrag`，工作树 clean，开始一次性 startup audit。

本文件只证明 PHASE18 已启动并冻结 Gap List，不表示 PHASE18 completed、Goal04 completed、PHASE19 已启动、quality proven 或 production ready。

## 启动检查

- latest main：`4d14ae9e8cd953359c82e51d55279cc123ab47ae`。
- PR C merge subject：`Merge Goal04 PHASE17 dynamic plan DAG closure`。
- PHASE17 closure evidence：`docs/evidence/goal04-phase17-coordinator-closure.md`。
- PHASE18 worktree：`C:\Users\Administrator\.codex\worktrees\goal04-phase18\Zuno`。
- PHASE18 branch：`codex/goal04-phase18-agentic-graphrag`。
- Alembic head：`20260728_49 (head)`。
- 当前 PHASE18 状态：`in_progress`。

## 已读事实源

- `docs/architecture/architecture.md`
- `docs/architecture/architecture-views.md`
- `docs/architecture/architecture.html`
- `docs/modules/README.md`
- `docs/modules/03-knowledge-agentic-graphrag.md`
- `docs/modules/06-agent-core-planning-control.md`
- `docs/status/production-readiness.md`
- `.agent/architecture/architecture.md`
- `.agent/modules/README.md`
- `.agent/README.md`
- `.agent/system.yaml`
- `.agent/references/current-program.md`
- `.agent/references/docs-map.md`
- `.agent/references/code-map.md`
- `.agent/references/task-routing.md`
- `.agent/references/workflow.md`
- `.agent/references/project-map.md`
- `.agent/references/architecture-docs-map.md`
- `.agent/references/documentation-governance.md`
- `.agent/references/architecture-update-policy.md`
- `.agent/references/diagram-inventory.md`
- `.agent/references/current-target-future-rules.md`
- `.agent/references/verification-map.md`

## Current Baseline

PHASE12 已完成 KnowledgeVersion / Snapshot / Index Visibility / Cutover / Standard RAG durable port，当前 evidence 可作为 PHASE18 输入，但不证明 Agentic GraphRAG Inner Loop 已完成。

当前可复用基础：

- `src/backend/zuno/knowledge/agentic/runtime.py`：已有 `CorrectiveAgenticRetrievalRuntime` 局部 loop，可运行多轮 corrective retrieval。
- `src/backend/zuno/knowledge/agentic/evidence_ledger.py`：已有 in-memory `EvidenceLedger`，可按 version/span/text hash 去重。
- `src/backend/zuno/knowledge/agentic/corrective.py`：已有 failure bucket 到 corrective action 的局部 policy。
- `src/backend/zuno/knowledge/agentic/durable.py`：已有 `DurableKnowledgeRetrievalPort`，可把部分 QueryRun、Round、Evidence、CitationLineage 写入 repository。
- `src/backend/zuno/platform/database/knowledge/domain.py`：已有 KnowledgeVersion、Snapshot、QueryRun、RetrievalRound、EvidenceRecord、CitationLineage 的部分 PostgreSQL repository。
- `tests/knowledge/test_corrective_retrieval_runtime.py` 和 `tests/knowledge/test_evidence_ledger.py` 覆盖局部 corrective runtime、durable port 和 ledger。

当前旧默认链：

```text
CompletionService
→ GeneralAgent
→ ContextOrchestrator.prepare
→ search_knowledge_base
→ KnowledgeQueryService
→ GraphRAGQueryService
→ RetrievalPlanner / RetrievalOrchestrator
```

旧链仍大量位于 `src/backend/zuno/platform/services/retrieval/**` 和 `src/backend/zuno/platform/services/graphrag/**`，并通过 `src/backend/zuno/knowledge/query_service.py` 的 compatibility export 暴露。这是 PHASE18 必须切流和收口的主要目标。

## Frozen Gap List

### P18-T01 EvidenceRequirement and Profile Selection

Current：`CorrectiveRetrievalRequest` 已有 query、workspace、knowledge_space_ids、trace、task、profile 和 `agent_core_decision_ref`，但不是正式 `KnowledgeQueryRequest`；缺少完整 EvidenceRequirement、run_id、plan_version_id、step_run_id、goal_version_id、authorized_scope_ref、retrieval_budget_ref、deadline、idempotency_key 和 profile ceiling。

Target：Agent Core EvidenceRequirement、scope、budget、risk 和 profile ceiling 必须解析为正式 KnowledgeQueryRequest；Profile 自适应，不默认 Agentic。

### P18-T02 Fixed KnowledgeRetrievalGraph and Round Domain

Current：没有 `src/backend/zuno/knowledge/graph/knowledge_retrieval_graph.py`；`CorrectiveAgenticRetrievalRuntime` 是 Python loop，不是固定 `validate -> pin snapshot -> scope -> interpret -> select profile -> plan round -> admit -> dispatch -> normalize -> fuse -> ledger -> evaluate -> decide` 图；`RetrievalRound` 只有部分 repository 记录。

Target：实现固定 KnowledgeRetrievalGraph、KnowledgeGraphState、immutable RetrievalRound 和 restart/deadline/cancel/snapshot guard。RetrievalRound 不修改 Agent PlanVersion。

### P18-T03 Graph Entity/Relation/Path/Community Runtime

Current：`agentic_graphrag.py` 有 local deterministic graph extraction/community trace 和 `GraphRAGIndexPipelineContract`，但 Graph path/entity/relation/community 仍是局部 trace 与旧 orchestrator 组合；SourceSpan grounding 部分存在，未形成正式 retriever attempt、path lineage 和 strict evidence eligibility contract。

Target：Entity、Relation、Path、Community retriever 必须在固定 Snapshot 和 authorized scope 下运行；Graph candidate 必须能回到 DocumentVersion / CitationChunk / SourceSpan。

### P18-T04 DRIFT and Multi-retriever Dispatch

Current：`AgenticRetrievalRouter` 可选择 BASIC/LOCAL/GLOBAL/DRIFT，旧 `RetrievalOrchestrator` 可组合检索，但没有 Knowledge 内部 durable multi-retriever dispatch、attempt claim、late-result fencing、timeout/partial failure 和 branch cap。

Target：实现 Knowledge 内部 RetrieverBatch dispatch；BM25、Vector、Entity、Relation、Path、Community retriever 受预算、deadline、capacity 和 idempotency 控制，不混用 Agent Plan DAG 事实。

### P18-T05 Fusion, Rerank and Rank Lineage

Current：`EvidenceItem` 已有 raw_score、rrf_score、rerank_score、rank_before、rank_after、rank_delta、dropped reasons 等字段，旧 fusion/rerank 也有测试；但 rank lineage 未作为 PHASE18 正式领域事实持久化，gold evidence loss、dropped reason、score scale mismatch 还未进入 Agentic GraphRAG closure gate。

Target：accepted/rejected evidence 都必须有 raw/fused/reranked rank、score normalization、drop/demotion reason 和 deterministic tie-break lineage。

### P18-T06 EvidenceLedger, Frontier and Quality Verdict

Current：`EvidenceLedger` 是 in-memory ledger；`RetrievalQualityGate` 能给出 RELEVANT / AMBIGUOUS / IRRELEVANT / CONFLICTING / INSUFFICIENT_SPAN；缺 EvidenceFrontier、coverage/authority/temporal/conflict/citation availability/no-yield/budget exhausted 的 durable verdict。

Target：EvidenceLedger、EvidenceFrontier、QualityVerdict 均为 Knowledge 事实；Verdict 不得冒充 Agent ControlDecision。

### P18-T07 Corrective Retrieval Decision

Current：`CorrectiveRetrievalPolicy` 可根据 failure bucket 选择 rewrite、multi-query、HYDE、parent/graph/focused citation 等动作；缺 typed CorrectiveRetrievalDecision、round generation、loop cap persistence、index unavailable、deadline、no-yield 和 snapshot recovery 的完整故障语义。

Target：Retry、Corrective Retrieval、Index Recovery Proposal 和 Agent Replan 必须分离；Corrective Retrieval 只能创建新 RetrievalRound，不创建 Agent PlanVersion。

### P18-T08 KnowledgeControlProposal and Agent Integration

Current：`CorrectiveAction` 有 ASK_USER、USE_EXTERNAL_TOOL、ABSTAIN，但没有正式 `KnowledgeControlProposal` domain / repository / schema；Agent Core accept/reject、Replan Barrier 接入和旧 GraphRAG default cutover 未完成。

Target：Knowledge 只能输出 ASK_USER / EXTERNAL_SEARCH / REPLAN / ABSTAIN Proposal，由 Agent Core 验证并决定；旧 `GraphRAGQueryService` / `RetrievalPlanner` / `RetrievalOrchestrator` 默认路径必须切流，临时 adapter 明确进入 PHASE22 删除清单。

## Stop Conditions

- 需要改变 Knowledge 与 Agent Core owner 边界时停止。
- 需要把 Knowledge 直接改 Agent PlanVersion、Ask User、External Tool 或 Final Answer 时停止。
- 需要不可逆数据库 migration 且无恢复策略时停止。
- 发现旧 GraphRAG 默认路径无法切流且只能保留双主路径时停止。

## 下一步

从 P18-T01 开始实现正式 `KnowledgeQueryRequest` / EvidenceRequirement / Profile Selection domain，并为后续 fixed KnowledgeRetrievalGraph、Round、Ledger、Proposal 和 default cutover 建立可验证合同。

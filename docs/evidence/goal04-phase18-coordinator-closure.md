# Goal04 PHASE18 Coordinator Closure

updated: 2026-07-28
phase: PHASE18 Agentic GraphRAG Inner Loop
pr: PR D / #49
branch: codex/goal04-phase18-agentic-graphrag
base_main_sha: 4d14ae9e8cd953359c82e51d55279cc123ab47ae
head_sha: 42a77f9fccf0b328bb48098eb6b16dcad883abcd
status: completed
coordinator_approval: approved
production_readiness: not established

## 结论

PHASE18 完成并获 Coordinator Approval。P18-T01 至 P18-T08 已从 Frozen Gap List 收口为代码、PostgreSQL 事实复用、聚焦测试和 evidence bundle。PHASE18 不声明 Agentic GraphRAG 相对 baseline 的质量提升；quality / release gate 仍等待 PHASE20/22。

本 closure 不启动 PHASE19。PHASE19 仍必须等待 PHASE18 与 PHASE10 都进入 main 后才能创建分支。

## Mandatory Scope 映射

- P18-T01：`CorrectiveRetrievalRequest` 携带 query、workspace、knowledge scope、profile ceiling、budget、deadline、trace、Agent Core decision ref 和 claims；KnowledgeStepExecutor 默认 STANDARD profile，不默认 Agentic。
- P18-T02：`KnowledgeRetrievalGraphTrace` 固定 validate、pin_snapshot、scope、interpret、select_profile、plan_round、admit、dispatch、normalize、fuse_rerank、evidence_ledger、evaluate、corrective_decision 节点；动态内容进入 `RetrievalPlan` 和 rounds。
- P18-T03：Deep profile 生成 Entity、Relation、Path、Community dispatch plan；strict evidence 只有带 DocumentVersion / SourceSpan / Citation lineage 的记录可持久化。
- P18-T04：多 retriever dispatch plan 记录 budget、timeout、parallel group；required retriever timeout / index unavailable fail closed；optional late graph result 被 fencing，不进入 ledger。
- P18-T05：EvidenceLedger record 保留 raw/fusion/rerank score、selection reason、retriever source、graph path、claim refs 和 text hash。
- P18-T06：EvidenceFrontier / CoverageSummary 覆盖 claim coverage、strict citation、authority、temporal version、conflict group、no-yield / coverage / citation / conflict stop reasons。
- P18-T07：CorrectiveRetrievalPolicy 消费 verdict、failure bucket、novelty、loop cap 和 frontier stop reasons；纠正只产生新 retrieval round，不创建 Agent PlanVersion。
- P18-T08：KnowledgeControlProposal 只作为 Proposal；Agent Core deterministic gate 只接受 `accept_evidence`，拒绝 `abstain`、ask-user、external-tool、agent-replan 和 unresolved corrective proposal 为 blocked observation。WorkspaceTaskRuntimeService、product_baseline retrieval probe 和 KnowledgeQueryService application facade 已接 PHASE18 trace。

## Migration 和 Alembic

PHASE18 未新增 Alembic revision。它复用 PHASE12 已合并的 Knowledge PostgreSQL domain facts 和 Alembic head `20260728_49`：

```text
knowledge_query_runs
knowledge_retrieval_rounds
knowledge_evidence_records
knowledge_citation_lineage
knowledge_snapshots
knowledge_chunks
```

`DurableKnowledgeRetrievalPort` 使用稳定 QueryRun/Round id、strict evidence idempotent replay 和 CitationLineage commit；缺 active snapshot 或 durable persistence failure 均 fail closed 为 blocked observation。

## 默认运行链

```text
WorkspaceTaskRuntimeService
→ CorrectiveAgenticGraphRAGRuntime
→ CorrectiveAgenticRetrievalRuntime
→ fixed KnowledgeRetrievalGraph trace
→ KnowledgeControlProposal
→ Agent Core KnowledgeStepExecutor accept/reject gate
```

应用层 query facade：

```text
KnowledgeQueryService.query()
→ PHASE18 application query path metadata
→ knowledge_retrieval_graph / knowledge_control_proposal / evidence_frontier trace
```

旧 `AgenticRetrievalRuntime` 保留为受控 candidate/index adapter，由 PHASE18 wrapper 包裹并输出 PHASE18 trace；永久 legacy / alias 清零仍属于 PHASE22。

## 实际运行验证

```powershell
python -m pytest tests\agent\test_knowledge_graphrag_runtime_contracts.py tests\api\test_workspace_task_runtime.py::test_workspace_task_runtime_resets_to_phase18_agentic_graphrag_default_path tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py -q -p no:cacheprovider --tb=short
```

结果：

```text
26 passed, 1 warning in 23.28s
```

结构和文档验证：

```powershell
git diff --check
python tools\scripts\verify_current_program.py
python tools\scripts\verify_docs_entrypoints.py
python .agent\scripts\verify_agent_system.py
python .agent\scripts\verify_doc_boundaries.py
```

结果：

```text
passed
```

PR #49 GitHub validate：

```text
validate: SUCCESS
workflow: Architecture document set
head: 42a77f9fccf0b328bb48098eb6b16dcad883abcd
```

## Failure Fingerprints

1. Parser fixture DOCX blocked 预期漂移：
   - command: `python -m pytest tests\api\test_workspace_task_runtime.py::test_workspace_task_runtime_resets_to_phase18_agentic_graphrag_default_path tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py tests\evals\test_agentic_graphrag_product_baseline.py -q -p no:cacheprovider --tb=short`
   - test: `tests\evals\test_agentic_graphrag_product_baseline.py::test_launchable_agentic_graphrag_product_baseline_generates_shareable_summaries`
   - exception: `RuntimeError`
   - first relevant stack frame: `src\backend\zuno\agent\product_baseline.py:423`
   - environment signature: local parser dependency state no longer blocks docx before PHASE18 retrieval probe
   - retry count: 1
   - disposition: non-PHASE18 parser fixture drift; not fixed in PHASE18 runtime.

2. Product integration seed missing description:
   - command: `python -m pytest tests\integration\test_goal03_wave_a_persistence.py -q -p no:cacheprovider --tb=short`
   - test: `tests\integration\test_goal03_wave_a_persistence.py::test_phase09_product_command_is_idempotent_and_receipt_does_not_claim_domain_success` and 8 sibling product-owner tests
   - exception: `sqlalchemy.exc.IntegrityError / psycopg.errors.NotNullViolation`
   - first relevant stack frame: `tests\integration\test_goal03_wave_a_persistence.py:114`
   - environment signature: PHASE09/product seed schema mismatch before PHASE18 knowledge query-run/evidence assertions
   - retry count: 1
   - disposition: product-owner fixture / schema seed mismatch; not fixed in PHASE18 runtime.

## 未运行验证

- 全仓 pytest 未运行，避免无代码变化重复已通过 suite。
- PHASE10 Web/Desktop lint/build/E2E 未运行；按 Goal04 顺序，PHASE18 合并后再更新 PR #47。
- Fixed benchmark / quality release gate 未运行；属于 PHASE20/22。

## Coordinator Approval

approved. PHASE18 completed. PR #49 可标记 ready 并合并到 `main`。Production readiness not established。

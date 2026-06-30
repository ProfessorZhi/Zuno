# PHASE08 RAG GraphRAG Evidence Citation

status: completed

## 目标

把 Zuno 的知识系统明确落成 **Agentic GraphRAG**：用户面对的是 `normal / enhanced / auto` 三种产品模式，Agent / Query Router 在增强和自动模式下选择 `basic / local / global / drift` 这些内部召回通道，并通过 evidence / citation / eval 证明选择是可解释、可评测、可回放的。

本 phase 不做“把四个底层检索方法直接暴露给用户”的产品设计。`basic / local / global / drift` 是 internal query method；`normal / enhanced / auto` 才是 user-facing product mode。

## 步骤

- [x] 保持 product mode：normal、enhanced、auto。
- [x] 明确 mode policy：`normal -> basic`；`enhanced -> retrieval required, Agent selects method(s)`；`auto -> Agent first decides retrieval need, then selects method(s)`。
- [x] 保持 resolved query method：basic、local、global、drift；`auto` 不允许成为最终 resolved query method。
- [x] 建立 Agentic Retrieval Router contract，输入包含 query、workspace、context pack、product mode、budget、ACL、evidence state 和 fallback history。
- [x] 固定 BM25 + dense vector + RRF + optional rerank 的目标边界；本 phase 不把生产级融合写成 Current。
- [x] 固定 GraphRAG extraction、community report、local/global/drift query 的成熟目标路径；本 phase 只完成可测 contract。
- [x] 建立 staged fusion：`global` 先产出 community-level prior / theme / subquestions，再由 `local` 或 `basic` 回补 chunk-level evidence。
- [x] 建立 Evidence Bundle、Citation Builder、unsupported claim check。
- [x] 定义 GraphRAG index pipeline：Document IR -> TextUnit/Block -> entity/relation extraction -> entity resolution -> graph upsert -> community detection -> community report -> embeddings/search index -> index manifest。
- [x] 定义 EvidenceBundle schema，包含 evidence_id、document_id、block_id、retrieval_method、score、source_span、citation_label、trust_label。
- [x] 定义 unsupported claim 失败处理：rewrite、retrieve more、ask user、evidence-limited answer、block high-risk confident wording。
- [x] 在 trace 中记录 requested product mode、router decision、candidate methods、resolved method(s)、fallback reason、evidence coverage 和 citation coverage。
- [x] 写 retrieval/eval tests。

## 输入 / 输出文件

输入：

- PHASE04 Canonical Document IR 和 index handoff。
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/platform/services/graphrag/**` 的迁移候选代码。
- 现有 GraphRAG query service / retrieval planner / orchestrator tests。

输出：

- Agentic Retrieval Router contract。
- GraphRAG index pipeline contract。
- staged fusion contract。
- EvidenceBundle / Citation Builder / unsupported claim check。
- retrieval eval fixtures。

## 依赖与阻塞

- 依赖 PHASE04 Document IR；GraphRAG extraction 和 citation 不直接消费 parser 原始输出。
- 依赖 PHASE05 runtime state；retrieval decision 必须挂 trace_id / task_id。
- 依赖 PHASE09 ACL / security labels；跨 workspace chunk 不进入 evidence。
- PHASE10 eval 必须消费本 phase 的 `resolved_methods`、`evidence_count`、`citation_coverage`、`unsupported_claims`。

## 测试矩阵

| 场景 | 期望 |
| --- | --- |
| normal | 强制 `basic`，不解析为 `auto`。 |
| enhanced exact lookup | retrieval required，允许 basic/local。 |
| enhanced global question | router 可选 global，并通过 local/basic 回补 evidence。 |
| auto no retrieval | Agent 可直接回答或执行轻量任务，但 trace 记录 no_retrieval reason。 |
| auto complex research | Agent 进入 drift 或 staged combination。 |
| local entity question | 命中实体邻域、关系和 source chunks。 |
| global community question | 命中 community report，不硬混 BM25 chunk ranking。 |
| unsupported claim | 触发 rewrite / retrieve more / evidence-limited answer。 |
| ACL filtered chunk | 不进入 EvidenceBundle。 |

## 验收

- `auto` 只是 router，不是最终 query method。
- `normal` 强制 basic；`enhanced` 一定检索但方法由 Agent 选择；`auto` 先判断是否需要检索，再由 Agent 选择方法。
- `global` 是 community-level prior，不和 BM25 chunk 生硬混榜。
- 用户不需要理解 `local/global/drift` 的内部差异，也能通过产品模式得到合适行为。
- 每个答案可以追溯 evidence 和 citation。
- 生产级 extraction、community report、fusion/rerank 未完成前，只能写 Target；不能把 query contract foundation 写成成熟 Agentic GraphRAG Current。

## 完成事实

Current 已完成：

- `src/backend/zuno/knowledge/agentic_graphrag.py` 提供 Agentic Retrieval Router、ProductMode、QueryMethod、StagedFusionPlan、EvidenceBundle、CitationBuilder、UnsupportedClaimChecker、GraphRAGIndexPipelineContract 和 AgenticGraphRAGTrace。
- `tests/agent/test_agentic_graphrag_contract.py` 覆盖 product mode 与 internal method 分离、`auto` 不作为最终 resolved method、global staged fusion、ACL-filtered evidence、citation coverage、unsupported claim actions 和 Document IR 到 GraphRAG index pipeline 的 source span handoff。
- `zuno.knowledge` facade 已 lazy 暴露 PHASE08 contract，不 eager load DB、vector runtime 或 provider client。

仍是 Target：

- 生产级 LLM entity / relation extraction、community report 生成、RRF / rerank 策略治理、GraphRAG index job runtime 和线上 retrieval eval baseline。

## 验证

```powershell
pytest -q tests/agent/test_agentic_graphrag_contract.py tests/agent/test_knowledge_graphrag_runtime_contracts.py tests/agent/test_knowledge_layer_surfaces.py tests/graphrag tests/retrieval tests/evals -p no:cacheprovider
```

# Agentic Retrieval Planner

所属运行域：Agent Core、Input & Knowledge、Governance & Observability。

## 定位

Agentic Retrieval Planner 不是用户手动选择一堆 RAG 工具，而是 Single Controller Agent 根据 ContextPack 和任务目标生成 RetrievalPlan，并在检索、Graph expansion、rerank、citation binding 和 reflection 中闭环。

RAG 的目标设计已经清楚：离线侧完成 SourceObject、Document IR、Chunk、Embedding/Index 和 Graph evidence；在线侧完成 Query strategy、粗召回、fusion/rerank、EvidenceBundle、claim binding 和 grounded answer。当前主要缺口不是“有没有 GraphRAG”，而是 agentic re-retrieval 是否由统一 Agent Core loop 驱动，以及 fixed benchmark 是否证明 evidence-span、citation 和 answer correctness 增益。

## 模式关系

- standard retrieval：fixed baseline，使用 BM25/vector 和 citation。
- deep retrieval：扩大 query、candidate pool、rerank 和 evidence diagnostics。
- agentic retrieval：在 standard/deep 的 evidence contract 上增加 planning、Graph expansion、reflection、replan、tool observation 和 abstain。

短期 RetrievalPlan 的 query strategy contract 至少应能表达：

- Query Rewrite：把用户问题改写为检索友好查询。
- Multi Query：为同一问题生成多个互补查询。
- Step-back Query：先抽象上位问题，再回到具体证据。
- HyDE：在合适任务上生成假设性答案/段落辅助召回。

这些策略是 RetrievalPlan 的字段或 step，不是用户手动选择的产品模式。是否启用由 StrategySelector、ContextPack、budget、evidence diagnostics 和 reflection 共同决定。

## Contract

```text
ContextPack
-> StrategyDecision
-> RetrievalPlan
   -> Query Rewrite / Multi Query / Step-back / HyDE
-> BM25 / Vector / Graph retrieval
-> Fusion / Rerank
-> EvidenceBundle
-> ClaimBinding
-> ReflectionDecision
```

EvidenceBundle 必须包含 source document、source span、citation label 和 retriever/rerank diagnostics。Graph evidence 必须回到 source span；doc-only evidence 不得作为 strict citation。

## 五阶段 Retrieval Architecture

```text
1. Index Layer
2. Query Strategy Layer
3. Recall / Graph / Rerank Layer
4. Evidence and Citation Layer
5. Corrective Agentic Control Layer
```

### Index Layer

```text
SourceObject
-> ParseSnapshot
-> CanonicalDocumentIR
-> DocumentBlock / SourceSpan
-> CitationChunk
-> ParentChunk
-> BM25 / Vector / Entity-Relation-Community indexes
-> IndexManifest
-> CitationLineage
```

粒度边界：

```text
CitationChunk = retrieval unit
ParentChunk   = context expansion unit
SourceSpan    = citation and provenance unit
```

parser failed 或 source span 缺失时不得 fake index 或 strict citation。

### QueryStrategy

```yaml
query_strategy:
  type: DIRECT | REWRITE | MULTI_QUERY | STEP_BACK | HYDE | ENTITY_DECOMPOSITION | RELATION_QUERY
  generated_queries: [string]
  rationale_summary: string
  budget_cost: number
  expected_failure_to_fix: string
```

| 问题特征 | 默认策略 |
| --- | --- |
| 口语、缩写、代词指代 | REWRITE |
| 用户表达与文档文体差异大 | HYDE |
| 问题过度具体、需要背景原理 | STEP_BACK |
| 多维度、表述角度多 | MULTI_QUERY |
| 多实体及关系问题 | ENTITY_DECOMPOSITION / RELATION_QUERY |
| 精确型号、数字、术语 | DIRECT + BM25 |
| 简单清晰事实问题 | DIRECT |

### Recall、Fusion 与 Rerank

```text
BM25 ---------\
Vector --------\
Multi Query ----> RRF / fusion -> Cross-encoder rerank -> Parent expansion
Graph ----------/
```

- BM25 与 Vector 默认可并行。
- RRF 使用排名融合不可比分数。
- Rerank 只对候选集运行。
- Graph 不是默认全开，由 GraphRoutingDecision 控制。
- Context 中只放经预算选择的 evidence。

### GraphRoutingDecision

```yaml
graph_routing_decision:
  use_graph: boolean
  reason_codes:
    - multiple_entities
    - explicit_relation
    - multi_hop
    - global_theme
    - cross_document_relation
  mode: local_path | global_community
  max_hops: int
  entry_entities: [entity]
```

适合使用 Graph：多个明确实体、实体关系、多跳路径、跨文档关联、corpus-level 主题/社区问题。

跳过 Graph：简单事实查找、操作流程、无可靠实体 grounding、图证据无法回到 SourceSpan、latency/budget 不允许。

## EvidenceLedger

多轮检索必须通过 EvidenceLedger 累积、去重和追踪证据。

```yaml
evidence_record:
  evidence_id: string
  source_document_id: string
  document_version_id: string
  source_span: object
  citation_label: string
  retrieval_round: int
  query_id: string
  retriever: bm25 | vector | graph | tool
  raw_score: number | null
  fusion_rank: int | null
  rerank_score: number | null
  graph_path: [edge] | null
  claim_refs: [claim_id]
  contradiction_group: string | null
  freshness: string
  selected: boolean
  selection_reason: string
  trace_span_id: string
```

EvidenceLedger 负责跨轮去重、证据版本、新证据增量、冲突分组、source lineage、Context budget、claim attribution 和 eval attribution。

## RetrievalQualityVerdict

```yaml
retrieval_quality_verdict:
  verdict: RELEVANT | AMBIGUOUS | IRRELEVANT | CONFLICTING | INSUFFICIENT_SPAN
  evidence_count: int
  span_coverage: number
  top_score: number | null
  novelty_since_previous_round: number
  missing_requirements: [string]
```

Corrective loop：

```text
Need retrieval?
-> Query Strategy
-> Retrieve / Graph / Rerank
-> EvidenceLedger
-> Retrieval Quality Gate
   -> sufficient -> Claim Binding
   -> doc miss -> Rewrite / Multi Query / HyDE
   -> text miss -> Parent / Adjacent / Graph expansion
   -> citation miss -> Focused source-span retrieval
   -> conflicting -> retrieve both sides / ask user
   -> external gap -> governed external Tool
   -> no safe path -> abstain
```

停止条件：

- Retrieval Quality Gate 达到 sufficient / PASS。
- `max_retrieval_rounds` 到达上限。
- `novelty_since_previous_round` 低于阈值，继续检索没有增量。
- 所有未使用的 CorrectiveRetrievalAction 都已尝试或被 policy/budget 禁止。
- token、latency 或 cost budget 耗尽。
- 需要用户澄清才能继续。
- 没有安全路径时输出 ABSTAIN。

## Failure Buckets

- doc_miss
- doc_hit_text_miss
- text_hit_citation_miss
- citation_hit_answer_wrong
- unavailable_due_to_missing_trace_fields

缺少 trace 字段时必须输出 unavailable，不得编造 bucket。

| Failure bucket | 默认纠正动作 |
| --- | --- |
| `doc_miss` | REWRITE、MULTI_QUERY、HYDE、扩大 scope |
| `doc_hit_text_miss` | Parent expansion、adjacent span、Graph path |
| `text_hit_citation_miss` | focused citation retrieval、source-span expansion |
| `citation_hit_answer_wrong` | answer critic、claim rewrite、重新 synthesis |
| `graph_without_span` | 降为辅助信息，不允许 strict citation |
| `retrieval_low_confidence` | external Tool、ASK_USER 或 ABSTAIN |
| `conflicting_evidence` | 保存双方证据、标记冲突、继续检索或说明不确定性 |

## 质量门

```text
Agentic Recall@5 >= standard_rag
Evidence Text Available@5 >= 0.60
Source Doc Citation Accuracy >= 0.85
Citation Accuracy >= 0.30
Answer Correctness >= standard_rag
Unsupported Claim Rate 不得恶化
```

Current：

```text
implementation available
measurement blocked
quality not yet proven
```

PHASE08 Current 事实：

- `src/backend/zuno/knowledge/agentic/` 已提供 QueryStrategy、RetrievalQualityVerdict、CorrectiveRetrievalAction、EvidenceLedgerRecord、EvidenceLedger、RetrievalQualityGate、CorrectiveRetrievalPolicy 和 CorrectiveAgenticRetrievalRuntime。
- EvidenceLedger 按 document version / SourceSpan / text hash 去重，并把 retrieval round、query strategy、retriever、score、graph path、claim refs、contradiction group 和 strict citation eligibility 写入 trace。
- Graph evidence 缺少 SourceSpan 时只能作为辅助证据，不能升级为 strict citation。
- `KnowledgeStepExecutor` 已在注入 `knowledge_runtime` 时调用 corrective retrieval runtime，并把 rounds、final action、final verdict 和 ledger trace 写入 runtime observation metadata；未注入依赖时保留 deterministic fallback。
- 本地 focused tests 已证明第一轮不足可进入第二轮 query，source span 命中可停止并输出 strict-citation-eligible evidence。

仍未 measured：

- fixed EnterpriseRAG paired benchmark 尚未完成 measured pass。
- Evidence Text Available@5、Citation Accuracy、Answer Correctness 仍不能写成质量通过。
- PHASE09 之前，Reflection / Replan / Rewrite / Grounded Synthesis 还不是完整质量闭环。

Short-term：

- P0 完整跑通 fixed EnterpriseRAG paired benchmark。
- P0 release gate 只在 measured profile 完整时判断通过或失败。
- P0 agentic re-retrieval 由统一 Agent Core loop 驱动，Reflection 的 RETRIEVE_MORE 必须回到 RetrievalPlan / execute_step，而不是停留在诊断文本。
- P1 retrieval diagnostics 和 citation diagnostics 持久化并可在 trace 中查看。

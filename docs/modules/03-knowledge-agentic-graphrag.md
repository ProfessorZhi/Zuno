# 03 Knowledge / Agentic GraphRAG

updated: 2026-07-12  
status: normative-target-module-design  
module_number: 03

所属运行域：Knowledge & Memory Runtime、Agent Core、Governance & Observability、Durable Infrastructure。

> 本文合并原 `agentic-retrieval-planner.md` 与 `knowledge-space-product-configuration.md`，作为 Knowledge / Agentic GraphRAG 的正式模块入口。

## 1. 模块定位

Knowledge / Agentic GraphRAG 负责把 Input 模块交付的标准文档表示转换为可检索、可融合、可引用、可纠偏的知识运行时。

核心职责：

```text
Retrieval Chunk / Parent Chunk / Citation Chunk
BM25 / Vector / Graph Index
RetrievalPlan
Query Strategy
并行 Retriever
Fusion / Rerank
Parent Expansion
EvidenceLedger
CitationLineage
RetrievalQualityVerdict
Corrective Retrieval
KnowledgeSnapshot / KnowledgeVersion
Knowledge Space Configuration
```

它不负责：

```text
原始文件解析
Agent 全局任务规划
模型 Provider 调用
Tool 执行
长期 Agent Memory
最终 AnswerPolicy 决策
```

Agent Core 决定何时以及为什么检索；Knowledge 决定如何可靠地检索、融合并返回证据。

## 2. Retrieval 模式关系

- standard retrieval：固定 baseline，使用 BM25/vector 和 citation。
- deep retrieval：扩大 query、candidate pool、rerank 和 evidence diagnostics。
- agentic retrieval：在 standard/deep 的 evidence contract 上增加 planning、Graph expansion、reflection、replan、tool observation 和 abstain。

这些是 Runtime Policy，不是让用户手动勾选一堆 RAG 工具。

## 3. 总体 Contract

```text
IndexableDocumentSnapshot
→ Chunking / Entity-Relation Extraction
→ BM25 / Vector / Graph Index
→ KnowledgeVersionManifest

ContextPack
→ StrategyDecision
→ RetrievalPlan
   → Query Rewrite / Multi Query / Step-back / HyDE
→ BM25 / Vector / Graph retrieval
→ Fusion / Rerank
→ Parent Expansion
→ EvidenceBundle / EvidenceLedger
→ ClaimBinding
→ RetrievalQualityVerdict
→ ReflectionDecision
```

Evidence 必须包含 source document、document version、SourceSpan、citation label 和 retriever/rerank diagnostics。Graph evidence 必须回到 SourceSpan；doc-only evidence 不得作为 strict citation。

## 4. 五阶段架构

```text
1. Index Layer
2. Query Strategy Layer
3. Recall / Graph / Rerank Layer
4. Evidence and Citation Layer
5. Corrective Agentic Control Layer
```

## 5. Index Layer

```text
SourceObject
→ ParseSnapshot
→ CanonicalDocumentIR
→ DocumentBlock / SourceSpan
→ CitationChunk
→ ParentChunk
→ BM25 / Vector / Entity-Relation-Community indexes
→ IndexManifest
→ CitationLineage
```

粒度边界：

```text
CitationChunk = retrieval unit
ParentChunk   = context expansion unit
SourceSpan    = citation and provenance unit
```

Parser failed 或 SourceSpan 缺失时不得 fake index 或 strict citation。

## 6. KnowledgeVersion

一次可服务的知识版本必须固定：

```text
knowledge_space_id
knowledge_version_id
document_set_version
chunk_policy_version
embedding_model_version
bm25_index_version
vector_index_version
graph_index_version
graph_extractor_version
validation_result_ref
```

AgentRun 通过 KnowledgeSnapshotRef 固定版本，不能让并行分支静默混用不同索引版本。

## 7. Query Strategy

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

是否启用由 Agent Core RuntimePolicy、ContextPack、预算、Evidence diagnostics 和 Reflection 共同决定。

## 8. Retriever Adapter

统一接口至少支持：

```text
query
workspace_id
authorization_context_ref
knowledge_snapshot_ref
metadata filters
ACL filters
top_k
timeout
score normalization
trace
```

目标 Adapter：

```text
BM25Retriever
VectorRetriever
GraphRetriever
StructuredDataRetriever
ExternalSearchRetriever
```

权限过滤必须在召回前进入 Retriever Query，不能先召回敏感内容再在 Python 中过滤。

## 9. Recall、Fusion 与 Rerank

```text
BM25 ---------\
Vector --------\
Multi Query ----> RRF / fusion -> Cross-encoder rerank -> Parent expansion
Graph ----------/
```

规则：

- BM25 与 Vector 默认并行。
- RRF 用于融合不可比分数。
- Rerank 只对候选集执行。
- Graph 不默认全开，由 GraphRoutingDecision 控制。
- Context 只放经过预算选择的 Evidence。
- 重复 Chunk、Parent/Child 和相同 SourceSpan 必须去重。
- 记录 rank_before、rank_after、rerank_score、selection_reason。

## 10. GraphRoutingDecision

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

适合 Graph：多个明确实体、实体关系、多跳路径、跨文档关联、corpus-level 主题或社区问题。

跳过 Graph：简单事实查找、操作流程、无可靠实体 grounding、图证据无法回到 SourceSpan、latency/budget 不允许。

## 11. EvidenceLedger

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
  authority_level: string
  selected: boolean
  selection_reason: string
  trace_span_id: string
```

EvidenceLedger 负责：

```text
跨轮去重
版本与时效
新证据增量
冲突分组
SourceLineage
Context Budget
Claim Attribution
Eval Attribution
Strict Citation Eligibility
```

## 12. Source Authority 与冲突

来源排序不能只看相关性，还要考虑：

```text
Authority
Effective Time
Approval Status
Supersedes Relation
Freshness
Source Type
ACL
```

示例：

```text
现行正式制度 > 已失效旧制度 > 草稿 > 员工个人笔记
```

Knowledge 返回 EvidenceVerdict：

```python
class EvidenceVerdict(BaseModel):
    sufficient: bool
    authoritative: bool
    temporally_valid: bool
    conflicting: bool
    selected_evidence_refs: list[str]
    superseded_evidence_refs: list[str]
    conflict_refs: list[str]
```

Agent Core 消费 Verdict，但不自己定义来源权威规则。

## 13. RetrievalQualityVerdict

```yaml
retrieval_quality_verdict:
  verdict: RELEVANT | AMBIGUOUS | IRRELEVANT | CONFLICTING | INSUFFICIENT_SPAN
  evidence_count: int
  span_coverage: number
  top_score: number | null
  novelty_since_previous_round: number
  missing_requirements: [string]
```

## 14. Corrective Retrieval Loop

```text
Need retrieval?
→ Query Strategy
→ Retrieve / Graph / Rerank
→ EvidenceLedger
→ Retrieval Quality Gate
   → sufficient → Claim Binding
   → doc miss → Rewrite / Multi Query / HyDE
   → text miss → Parent / Adjacent / Graph expansion
   → citation miss → Focused SourceSpan retrieval
   → conflicting → retrieve both sides / disclose conflict
   → external gap → governed external Tool
   → no safe path → abstain
```

停止条件：

- Quality Gate 达到 sufficient / PASS。
- 达到 `max_retrieval_rounds`。
- `novelty_since_previous_round` 低于阈值。
- Corrective Action 已用尽或被 policy/budget 禁止。
- Token、latency 或 cost budget 耗尽。
- 需要用户澄清。
- 没有安全路径时 ABSTAIN。

## 15. Failure Taxonomy

```text
KNOWLEDGE_MISS
RETRIEVAL_MISS
PARSING_MISS
INDEX_STALE
INDEX_INCOMPATIBLE
PERMISSION_FILTERED
EVIDENCE_INSUFFICIENT
EVIDENCE_CONFLICT
SOURCE_SPAN_MISSING
```

Failure Buckets：

```text
doc_miss
doc_hit_text_miss
text_hit_citation_miss
citation_hit_answer_wrong
graph_without_span
retrieval_low_confidence
conflicting_evidence
unavailable_due_to_missing_trace_fields
```

| Failure bucket | 默认纠正动作 |
| --- | --- |
| `doc_miss` | REWRITE、MULTI_QUERY、HYDE、扩大 scope |
| `doc_hit_text_miss` | Parent expansion、adjacent span、Graph path |
| `text_hit_citation_miss` | focused citation retrieval、SourceSpan expansion |
| `citation_hit_answer_wrong` | answer critic、claim rewrite、重新 synthesis |
| `graph_without_span` | 降为辅助信息，不允许 strict citation |
| `retrieval_low_confidence` | external Tool、ASK_USER 或 ABSTAIN |
| `conflicting_evidence` | 保存双方证据、标记冲突、继续检索或说明不确定性 |

缺少 trace 字段时必须返回 unavailable，不能编造 bucket。

## 16. Knowledge Space 配置

Knowledge Space 是用户选择知识库、模型 slot、检索 profile 和解析/index 配置的产品边界。它不是前端 Filter，而是后端可恢复、可 Trace、可用于 Benchmark 的配置事实源。

配置对象：

- `KnowledgeSpace`、`WorkspaceFile`。
- `RetrievalProfile`：top-k、candidate pool、RRF weights、rerank weights、citation threshold。
- `ChunkingProfile`：chunk size、chunk overlap、parent context size。
- `ParserProfile`：parser provider、PDF/text support、blocked reason policy。
- `EvalProfile`：benchmark case set、release thresholds。
- `ModelSlotBinding`：仅保存对 Model Gateway 的 slot 引用，不拥有模型执行。

优先级：

```text
DB workspace binding
> environment secret/reference
> YAML default
> test fixture default
```

运行时必须把最终生效配置写入 Trace 或 Eval Report。Workspace override 只允许通过后端 DTO 和 Policy Validation。

## 17. Quality Gate

```text
Agentic Recall@5 >= standard_rag
Evidence Text Available@5 >= 0.60
Source Doc Citation Accuracy >= 0.85
Citation Accuracy >= 0.30
Answer Correctness >= standard_rag
Unsupported Claim Rate 不得恶化
```

只有同一 Fixed Case Set 上完整 measured profile 才能进入 Release Gate。

## 18. Current 与 Gap

Current：

```text
implementation available
measurement blocked
quality not yet proven
```

已存在：

- QueryStrategy、RetrievalQualityVerdict、CorrectiveRetrievalAction、EvidenceLedger、RetrievalQualityGate 和 CorrectiveAgenticRetrievalRuntime baseline。
- EvidenceLedger 可记录 document version、SourceSpan、retrieval round、query strategy、retriever、score、graph path、claim refs 和 strict citation eligibility。
- Graph evidence 缺少 SourceSpan 时只能作为辅助证据。
- 本地 focused tests 已证明第一轮不足可进入第二轮 Query。

仍未完成：

- 真实 BM25 + Milvus + Neo4j 生产 Adapter 闭环。
- 真实 Cross-Encoder / Provider Reranker。
- Fixed EnterpriseRAG paired benchmark measured pass。
- 完整 ACL 前置过滤与 KnowledgeSnapshot。
- Source Authority、版本冲突与删除传播闭环。

## 19. 完成证据

```text
同一 Run 固定 KnowledgeSnapshot
BM25 / Vector 独立召回并通过 RRF 融合
Rerank 前后排名可追踪
Graph Routing 可解释且证据回到 SourceSpan
ACL 在召回前生效
EvidenceLedger 跨轮去重
Corrective Retrieval 真实改变下一轮 Query
删除文档后所有索引不可再召回
固定 Benchmark 达到 Release Gate
```

只有代码、持久化、真实 Adapter、Eval 与运行证据完成后，Target 才能写为 Current。
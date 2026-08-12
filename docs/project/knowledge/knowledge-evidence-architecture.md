# Knowledge & Evidence Architecture：文档如何变成可引用证据？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Ingestion、Retrieval、EvidenceCandidate 和 Citation Lineage 如何服务 Domain/Agent？
owner: Knowledge Service
replaces: `docs/project/modules/02-input-document-ingestion.md`、`03-knowledge-agentic-graphrag.md`（Superseded）

## Part A — Architecture Narrative

Knowledge Service 的工作不是“把所有文本塞进一个 legal_kb”，而是让不同 Scope 的材料在需要时
变成可定位、可授权、可复核的证据。案件文档先形成 DocumentVersion，再经过解析、Chunk/SourceSpan、
索引和 RetrievalRound，最后产生 EvidenceCandidate；Domain Owner 接受后才成为 EvidenceVersion。
这条链把原文位置、版本、权限和检索策略保留下来，回答也因此能解释依据来自哪一页哪一版材料。

复杂案件可能需要 Claim→Evidence、Fact→LegalElement→Statute 或跨文档事件链。Graph 只在关系型
查询和多证据链上作为 Conditional Projection；Exact Statute 或简单语义检索可能只需要 lexical、
dense 或 hybrid。每次选择都受 QueryClass、EvidenceRequirement、Scope、ACL 和预算控制，不因
“GraphRAG”这个名字自动增加复杂度。

主要失败是解析重复发布、索引引用旧 DocumentVersion、Citation 指向错误 SourceSpan，或检索结果
跨越 Matter/Organization Scope。系统必须拒绝或标记 unsupported，并允许降级到更简单的检索路径。
Graph、Milvus、Neo4j、RAGFlow 和 reranker 都是 Provider；如果 Hybrid RAG 在相同任务上更好，
Graph 应被外部化或删除。
Knowledge 不拥有 accepted Finding、HumanDecision 或外部副作用，只负责检索投影和可追溯候选。

## Part B — Detailed Architecture Specification

### Ingestion and retrieval contract

Ingestion 输入 `source_artifact_id`、content hash、DocumentVersion、parser/model version、scope、ACL
和 JobId，输出 SourceSpan/Chunk/Projection 或 rejected/stale receipt；重复 Job 必须幂等。Retrieval
输入 QueryClass、Task、Claim、EvidenceRequirement、scope、ACL 和预算，输出带 document version、
source span、ranker/provider version 和 CitationLineage 的 EvidenceCandidate。错误版本、无权限、
无来源或证据不足必须阻断发布并留下审计原因。

## Boundary

Knowledge Service owns source ingestion、OCR/parse、chunk、embedding、BM25/dense/hybrid/rerank、graph projection、RetrievalRound、EvidenceCandidate 和 Citation Lineage。它不拥有 Matter、accepted Evidence、Finding、HumanDecision 或 Tool Effect。

## Scopes

Public Legal Knowledge、Organization Knowledge、Matter Knowledge 是 retrieval scopes。Scope selected 不等于 retrieve everything；QueryClass、Task、Claim、EvidenceRequirement、权限和预算共同决定 lexical/dense/hybrid/rerank/graph/corrective strategy。

## Worker split

同一 Knowledge Service 下保留独立 worker profiles：OCR/parse、embedding/rerank、index publish、graph build、batch reprocessing。每个 worker 有 Job Identity、Idempotency、Retry、DLQ、backpressure 和 partial index recovery。

## Evidence contract

```text
Raw Document / DocumentVersion
  → SourceSpan / Chunk / Index Projection
  → RetrievalCandidate / CitationLineage
  → EvidenceCandidate
  → Domain Owner accepts EvidenceVersion
```

Graph、向量、BM25、RAGFlow 或其他 Provider 不能直接产生法律事实。Citation 必须回到授权 SourceSpan；Graph path 不是天然 citation。

## Citation provenance gate

Target Citation Contract 必须绑定 `claim_id`、`evidence_id`、`document_version_id`、`source_span_id`
和 provenance。缺少来源、引用了错误 DocumentVersion/SourceSpan、证据与 Claim 冲突或权限不可验证
时，系统必须拒绝、标记 unsupported、请求更多证据或进入人工复核；不能只因为检索结果存在就发布
Finding。当前 Citation wrong-span 校验仍属于实现缺口，不能写成 Current。

Graph 是 Conditional Projection。只有按 Query Class 的 Graph ablation、质量、延迟和成本结果证明
收益，Graph 才保留；否则降级为 Hybrid/Vector/Lexical Provider。

## Current / Target / Gap

- Current：仓库有 ingestion、RAG、GraphRAG、Milvus/Neo4j adapters 和 RabbitMQ workers；这些是代码/基础设施事实，不等于质量证明。
- Target：一个 Knowledge Service + resource-specific workers；Graph conditional。
- Gap：服务独立运行、retrieval SLO、Graph Kill Test、evidence sufficiency 和 cross-service Contract。

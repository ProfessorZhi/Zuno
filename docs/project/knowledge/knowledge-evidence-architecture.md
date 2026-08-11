# Knowledge & Evidence Architecture：文档如何变成可引用证据？

status: normative-target
canonical_question: Ingestion、Retrieval、EvidenceCandidate 和 Citation Lineage 如何服务 Domain/Agent？
owner: Knowledge Service
replaces: `docs/project/modules/02-input-document-ingestion.md`、`03-knowledge-agentic-graphrag.md`（Superseded）

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

## Current / Target / Gap

- Current：仓库有 ingestion、RAG、GraphRAG、Milvus/Neo4j adapters 和 RabbitMQ workers；这些是代码/基础设施事实，不等于质量证明。
- Target：一个 Knowledge Service + resource-specific workers；Graph conditional。
- Gap：服务独立运行、retrieval SLO、Graph Kill Test、evidence sufficiency 和 cross-service Contract。

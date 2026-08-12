# Knowledge & Evidence Architecture：文档如何变成可引用证据？

status: normative-target
architecture_state: ACCEPTED_TARGET
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

## Citation provenance gate

Target Citation Contract 必须绑定 `claim_id`、`evidence_id`、`document_version_id`、`source_span_id`
和 provenance。缺少来源、引用了错误 DocumentVersion/SourceSpan、证据与 Claim 冲突或权限不可验证
时，系统必须拒绝、标记 unsupported、请求更多证据或进入人工复核；不能只因为检索结果存在就发布
Finding。当前 `CitationBinder` 尚未证明这条 wrong-span 校验，属于 `Q039-C / P0-I`，不能写成 Current。

Graph 是 Conditional Projection。只有按 Query Class 的 Graph ablation、质量、延迟和成本结果证明
收益，Graph 才保留；否则降级为 Hybrid/Vector/Lexical Provider。

## Current / Target / Gap

- Current：仓库有 ingestion、RAG、GraphRAG、Milvus/Neo4j adapters 和 RabbitMQ workers；这些是代码/基础设施事实，不等于质量证明。
- Target：一个 Knowledge Service + resource-specific workers；Graph conditional。
- Gap：服务独立运行、retrieval SLO、Graph Kill Test、evidence sufficiency 和 cross-service Contract。

## Round-002 Target refinements（D003、D004）

Ingestion 发布必须保留 `source_artifact_id`、`DocumentVersion`、解析器/模型版本、内容 hash、
scope、ACL 和 JobId；重复投递应收敛到同一版本或明确的 rejected/stale 结果，不能依赖队列 ACK
证明业务发布成功。检索计划必须根据 QueryClass、Claim、EvidenceRequirement 和预算选择
lexical、dense、hybrid、rerank 或 conditional graph，并把最终 Claim 绑定到可验证的
`SourceSpan`/`CitationLineage`。

Graph 仍是 Conditional Provider。没有按查询类别的 Graph-vs-Hybrid 消融、证据充分性、引用正确性、
延迟、Token 和成本结果时，系统必须能够降级为更简单的检索路径；本节没有把 GraphRAG 质量收益
或当前服务拆分写成事实。

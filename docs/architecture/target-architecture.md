# Target Architecture

## Purpose

This file states the high-level near-term target. It is desired direction, not
current implementation truth.

## Target

Zuno should remain:

```text
monorepo now, modular monolith, service-ready later
```

The stable target concepts are:

```text
Local-first Agent Workspace
= Single GeneralAgent Runtime
+ Context / Memory Engine
+ Capability / Tool Retrieval
+ Knowledge / GraphRAG Retrieval
+ Evidence / Citation / Trace / Eval
+ Typed API + Web/Desktop
```

The high-level target layers are:

1. Product Layer: Vue Web and Electron Desktop.
2. API & Application Layer: FastAPI routes, DTOs, and Application Services.
3. Single GeneralAgent Runtime:
   `prepare_context -> agent_loop -> post_turn_commit`.
4. Context & Memory Layer: L0 Working Context, L1 Recent Interaction Window,
   L2 Task Summary Memory, L3 Structured Long-term Memory, L4 External
   Knowledge, and Raw Event Log.
5. Capability / Tool Retrieval Layer: ToolCard registry, keyword / alias
   search, Native BM25 over ToolCards, optional vector search, permission /
   health / cost filter, and capability selection trace.
6. Knowledge / GraphRAG Layer: `KnowledgeQueryService`,
   `GraphRAGQueryService`, `GraphRAGProjectSnapshot`, `basic`, `local`,
   `global`, `drift`, and `auto` router.
7. Retrieval / Fusion / Evidence Layer: query variants, Native BM25, dense
   vector, graph local, community global, deduplication, RRF fusion, optional
   rerank, evidence check, citation, and trace.
8. Infrastructure / Observability / Eval: PostgreSQL, Redis, RabbitMQ, MinIO,
   Milvus, optional Elasticsearch adapter, Neo4j, trace, eval, and benchmark.

Memory target strategy:

- Summary Compression + Structured Extraction.
- Sliding Window remains L1 recent-window and token-budget protection only.
- Importance Filtering can help retention/selection, but is not the main
  strategy.
- Summaries and structured memories must keep `source_event_ids`.
- Summary does not replace the Raw Event Log.
- External Knowledge is not Agent Memory.
- Prompt Caching is a compute-layer hint, not memory compression.

Retrieval target:

- Native BM25 is a ranking algorithm implemented locally by
  `NativeBM25Index` and `NativeBM25Retriever`.
- Elasticsearch is an optional external adapter, not BM25 itself.
- Enhanced paths may generate query variants, but the original query must be
  preserved.
- Multi-retriever recall may use Native BM25, Dense Vector, Graph Local, and
  Community Global.
- Deduplication uses stable ids such as `chunk_id`, `document_id + span`,
  `graph_node_id`, and `community_report_id`.
- RRF is the default coarse fusion method with `k = 60`, followed by optional
  rerank.

## Replacement Direction

```text
Domain Pack front path -> GraphRAG Project
domain_pack_id target name -> graphrag_project_id
rag_graph_deep -> Enhanced Mode plus query_method
local_graphrag -> local
community_global -> global
drift_like -> drift
```

## Not Near-Term

These are future direction, not current acceptance targets:

- Java business services
- microservice extraction
- event-driven workers
- product-level multi-agent mode
- Coding Agent mode
- independent GraphRAG or indexing services

## Detailed Design

Detailed design-stage material lives in:

- `.agent/architecture/near-term/`
- `.agent/architecture/future/`
- `.agent/architecture/decisions/`

The canonical Target / Proposed visual blueprint is:

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`

The canonical near-term Markdown files are:

- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`

Only implemented and verified conclusions should be promoted from `.agent/` to
formal `docs/`.

# Locked Near-Term Decisions

1. The near-term mainline is Python FastAPI + LangGraph AI Runtime.
2. Java, microservices, event bus, independent workers, and default multi-agent
   mode are future direction.
3. GraphRAG mainline is GraphRAG Project, not Domain Pack.
4. Enhanced Mode is a pipeline, not a single retriever.
5. Basic = BM25 + dense vector + fusion + rerank.
6. Query Method = `auto/basic/local/global/drift`.
7. Community reports are not a first-level query method.
8. Do not build a long-term Domain Pack shim.
9. Do not split microservices in the near-term refactor.
10. Ordinary QA does not default to multi-agent mode.

## Consequence

If implementation work needs one of the future items, it should become a new
explicit program instead of silently expanding the near-term GraphRAG cleanup.

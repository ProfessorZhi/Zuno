# Phase 2: Retrieval Strategy Closure

## Goal

Make the runtime strategy for `标准检索` and `增强检索` structurally correct.

## Required Outcome

### Standard Retrieval

Default chain:

```text
query rewrite
  -> vector + bm25
  -> fusion
  -> rerank
  -> citation answer
```

### Enhanced Retrieval

Default internal mode:

```text
rag_graph_deep
```

Default capability set:

```text
vector + bm25 + local graph + community report
```

### Router Rules

1. fact questions prefer hybrid retrieval
2. relation questions prefer local graph
3. global theme questions prefer community global
4. global-plus-evidence questions prefer drift-like routing
5. fallback paths must record reasons in metadata

## Required Runtime Behaviors

1. BM25 is enabled by default
2. graph failure can degrade to standard RAG
3. community-not-ready can degrade to local graph
4. rerank unavailability can degrade to score-based ordering
5. trace metadata must expose requested mode, resolved mode, route, and fallback reason

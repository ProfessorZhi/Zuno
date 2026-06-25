# Enhanced Retrieval Orchestrator Contract

This spec defines the target contract for product-facing
`enhanced_retrieval`.

It does not rename every runtime branch today. Instead, it defines the stable
orchestrator behavior that future aliases must satisfy.

## Goal

Expose only two product retrieval modes:

- `standard_retrieval`
- `enhanced_retrieval`

Hide internal route names such as `local_graphrag`, `community_global`, and
`drift_like` from ordinary product UX.

## Inputs

Enhanced retrieval takes:

- `query`
- `knowledge config`
- GraphRAG Project `query_policy` / retrieval policy
- available index inventory and health
- model profile
- query features
- route diagnostics from prior attempts, if any

Minimum runtime input shape:

```text
query
  + rewritten queries
  + knowledge capability
  + retrieval settings
  + graph/community index health
  + rerank availability
  + model profile
  + route policy
```

## High-Level Contract

```text
query
  -> query analysis
  -> query rewrite / requery
  -> multi-route retrieval
  -> confidence scoring
  -> baseline-preserving fusion
  -> final rerank
  -> final ranked contexts + citations + route trace
```

`standard_retrieval` must always remain the fallback floor.

That means enhanced retrieval may broaden the search, but it must not lose the
ordinary standard-retrieval candidate quality without an explicit confidence
reason.

## Step 1: Query Analysis

The orchestrator must first classify the query.

Minimum checks:

- simple fact question
- keyword-heavy exact-match question
- multi-hop question
- comparison question
- bridge relation question
- global / summary question
- evidence-required question
- whether requery is needed

Expected outputs:

- normalized query
- query feature flags
- route hints
- graph-worthiness signal
- candidate route set

The router should not treat every enhanced query as graph-first. Query analysis
decides which routes are worth paying for.

## Step 2: Query Rewrite / Requery

Rules:

- rewritten queries complement the original query; they do not replace it
- original and rewritten variants may both enter retrieval
- requery-derived candidates must preserve source attribution
- route trace should record which query variants were actually used

Typical uses:

- phrase expansion
- bridge clarification
- relation disambiguation
- global question broadening

## Step 3: Multi-Route Retrieval

Enhanced retrieval may use these channels:

- vector retrieval
- BM25 retrieval
- hybrid retrieval
- Local GraphRAG retrieval
- community/global retrieval
- deep research / DRIFT-like retrieval

Rules:

- not every query must run every channel
- orchestrator chooses routes based on query features and index health
- `standard_retrieval` channels stay available as the baseline floor
- graph/community/drift routes are additive, not permission to discard baseline

Recommended internal route mapping:

- fact question -> vector + BM25
- keyword-heavy question -> BM25 + vector
- relation / bridge question -> vector + BM25 + local graph
- global question -> community/global
- global + evidence question -> community/global + local graph via drift-like

## Step 4: Confidence Scoring

Enhanced retrieval must score route quality, not just route availability.

Minimum confidence families:

- `graph_confidence_score`
- route confidence
- source confidence
- fallback reason
- empty-result handling

Decision rules:

- low-confidence graph evidence must not break baseline top5 quality
- medium-confidence graph evidence may receive only limited promotion
- high-confidence graph evidence may enter top3/top5 aggressively
- unavailable or stale graph/community indexes must emit a traceable fallback

Confidence metadata should be explainable in trace outputs rather than hidden in
silent heuristics.

## Step 5: Baseline-Preserving Fusion

Fusion rules:

- standard-retrieval candidates are the floor
- graph/community/drift candidates may supplement or promote
- graph results must not displace baseline gold-like candidates without
  confidence support
- duplicate candidates must be merged
- source attribution must be retained

Expected source labels:

- `vector`
- `bm25`
- `requery`
- `graph`
- `community`
- `drift`
- `fused`

Current repository direction already contains baseline-preserving fusion logic.
This spec turns that direction into an explicit product contract.

## Step 6: Final Rerank

Rules:

- rerank happens after fusion
- rerank is unified across the final fused candidate set
- rerank uses `gte-rerank-v2` in the current default model profile
- final answer context order must come from the final reranked list

Important distinction:

- route-local rerank inside one retriever is not enough
- enhanced retrieval needs a final cross-route rerank contract

## Step 7: Output

Enhanced retrieval output must include:

- final ranked contexts
- citations
- route trace
- `retriever_used`
- confidence scores
- fallback reason
- latency
- failure count

Recommended trace fields:

- `requested_mode`
- `resolved_mode`
- `internal_route`
- `query_variants`
- `enabled_retrievers`
- `used_vector`
- `used_bm25`
- `used_graph`
- `used_communities`
- `used_paths`
- `follow_up_questions`
- `fallback_reason`
- `rerank_info`
- `citation_chunks`

## Degradation Rules

Enhanced retrieval must degrade predictably:

- if graph is unavailable -> fall back to `standard_retrieval`
- if community reports are unavailable -> degrade to local graph or standard
  retrieval depending on query type
- if rerank is unavailable -> return score-sorted candidates and expose the
  downgrade in trace metadata

Degradation must be visible in metadata. Silent degradation is not acceptable.

## Boundary With Standard Retrieval

`standard_retrieval` remains a distinct product contract:

- vector + BM25 + fusion + rerank + citations
- no graph/community/drift semantics

`enhanced_retrieval` extends that contract:

- starts from the same floor
- adds route analysis, graph/global/deep routes, and confidence-governed fusion

This is the key product boundary:

- standard retrieval is not a weak baseline
- enhanced retrieval is not a single graph toggle

## Current Implementation Status

Current repository already has partial building blocks for this contract:

- `RetrievalPlanner`
- `RetrievalOrchestrator`
- query rewrite adapter
- Local GraphRAG
- community/global and DRIFT-like route skeletons
- fusion metadata
- fallback metadata

But current runtime does not yet fully satisfy this contract because:

- BM25 is not enabled by default in the current planner
- current eval baseline does not exercise standard retrieval as defined here
- final cross-route rerank is not yet a fully explicit unified stage
- product aliases `standard_retrieval` / `enhanced_retrieval` are not yet
  formalized

## Acceptance Meaning

This spec should be treated as the stable target for future runtime alias work,
eval runner naming, and frontend wording.

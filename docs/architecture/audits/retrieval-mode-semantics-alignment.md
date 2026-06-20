# Retrieval Mode Semantics Alignment

This audit aligns product-facing retrieval names with the current runtime and
eval terminology.

The immediate goal is naming clarity, not a runtime rewrite. Current code still
uses historical eval labels such as `baseline_rag`, `local_graphrag`, and
`deep_graphrag`. Those labels are useful for controlled experiments, but they
are not the right product surface.

## Product-Facing Retrieval Modes

### `standard_retrieval`

Recommended user-facing names:

- `standard_retrieval`
- `标准检索`
- `普通模式`

Definition:

- Vector RAG
- BM25
- multi-source fusion
- rerank
- citation-oriented context retrieval

Excludes:

- Local GraphRAG
- Community / Global Search
- Deep Research / DRIFT-like

Product position:

- default product retrieval mode
- product baseline
- not a weak baseline
- not a vector-only ablation

### `enhanced_retrieval`

Recommended user-facing names:

- `enhanced_retrieval`
- `增强检索`

Definition:

- `standard_retrieval` as the floor
- query rewrite / requery
- multi-route retrieval
- Local GraphRAG
- Community / Global Search
- Deep Research / DRIFT-like
- confidence scoring
- baseline-preserving fusion
- final rerank
- orchestrator-side automatic route selection and result combination

Product position:

- product enhanced mode
- not a single GraphRAG switch
- not a user-visible choice among `local_graphrag`, `community_global`, and `drift_like`
- backend orchestrator should choose and fuse the best route automatically

## Internal Technical Modes

These names are internal runtime strategies, compatibility aliases, or ablation
labels. They should not be exposed as ordinary product modes:

- `vector_rag`
- `bm25`
- `hybrid_rag`
- `local_graphrag`
- `community_global`
- `drift_like`
- `rag_graph_deep`
- `vector_only_ablation`
- `local_graphrag_ablation`
- `deep_route_ablation`

Current repository-specific notes:

- `rag` is the current plain runtime mode alias.
- `rag_graph_deep` is the current deep graph runtime alias.
- `baseline_rag`, `local_graphrag`, and `deep_graphrag` are the current eval
  runner names in `tools/evals/zuno/multihop_eval/run_real_runtime_eval.py`.

### Current Label Mapping

Current labels should be interpreted like this until formal aliases are added:

| current label | current meaning | should later become |
| --- | --- | --- |
| `baseline_rag` | historical eval baseline, currently vector-first + rerank | `standard_retrieval` after BM25 + real fusion are formalized |
| `local_graphrag` | internal local graph ablation | `local_graphrag_ablation` |
| `deep_graphrag` | internal deep-route ablation around `rag_graph_deep` | `deep_route_ablation` |

## Naming Rules

Future product reports should prefer:

- `standard_retrieval`
- `enhanced_retrieval`

Historical eval names should be treated as follows:

- `baseline_rag`: historical eval alias; should migrate to `standard_retrieval`
- `local_graphrag`: internal ablation for graph-module contribution, not a
  product mode
- `deep_graphrag`: internal deep-route ablation, not a user-facing product name

Documentation rule:

- user-facing docs should describe only `standard_retrieval` and
  `enhanced_retrieval`
- architecture and eval docs may still mention internal route names when they
  are needed for implementation or measurement clarity

## Current Code Fact Audit

Source files checked:

- `src/backend/zuno/services/retrieval/orchestrator.py`
- `src/backend/zuno/services/retrieval/planner.py`
- `src/backend/zuno/services/retrieval/retrievers.py`
- `src/backend/zuno/services/retrieval/fusion.py`
- `src/backend/zuno/services/rag/handler.py`
- `tools/evals/zuno/multihop_eval/run_real_runtime_eval.py`

### 1. Is current `baseline_rag` really equal to `standard_retrieval`?

No.

Current `baseline_rag` maps to runtime mode `rag` in the eval runner. In the
current planner, `RetrievalPlanner(enable_keyword_recall=False)` enables only
the `vector` retriever for standard RAG routing. That means the current
`baseline_rag` is a historical vector-first baseline with rerank, not the full
product definition of `standard_retrieval`.

Closest honest description today:

- vector-first retrieval baseline
- rerank-enabled
- BM25-off in the current eval runtime
- not yet full product `standard_retrieval`

### 2. Does current `baseline_rag` include BM25?

No.

There are two blocking facts in the current path:

- `RetrievalPlanner` defaults `enable_keyword_recall=False`, so BM25 is not
  enabled for `standard_rag`.
- the eval runner writes a temporary config with
  `rag.enable_elasticsearch = False`, which disables the BM25 backend anyway.

So current `baseline_rag` should not be described as BM25-backed product
baseline behavior.

### 3. Does current `baseline_rag` include fusion?

Only in a narrow technical sense.

`RetrievalOrchestrator` always calls `RetrievalFusion.merge(...)`, but under the
current `baseline_rag` path the merged candidate set normally contains vector
documents only. That means current `baseline_rag` does not yet exercise the
intended product meaning of multi-source fusion across vector and BM25.

### 4. Does current `baseline_rag` include rerank?

Yes, but only inside the vector retrieval path.

`RagRetrieverAdapter` calls `RagHandler._retrieve_ranked_documents_rag_detail`,
and `RagHandler` applies rerank when `retrieval_settings.rerank_enabled` is
true. The eval runner sets `rerank_enabled` and a rerank model in runtime
settings. However, current runtime does not yet perform a distinct final
cross-source rerank after true multi-route fusion.

### 5. Is `enhanced_retrieval` already fully implemented?

No.

The repository already contains meaningful building blocks:

- query rewrite
- route analysis
- Local GraphRAG
- community/global route skeletons
- DRIFT-like route skeleton
- baseline-preserving fusion
- route diagnostics and fallback metadata

But product-level `enhanced_retrieval` is not fully implemented yet because the
current runtime still lacks a finished user-facing alias and a fully closed
execution contract for:

- `standard_retrieval` as guaranteed floor with BM25 on
- source-aware requery accounting in fusion outputs
- confidence-gated promotion rules documented as runtime contract
- final unified rerank across all fused routes
- fully productionized community/global and DRIFT-like evidence paths

### 6. What gap remains between current `local_graphrag` / `deep_graphrag` and product `enhanced_retrieval`?

The gap is structural:

- `local_graphrag` is an internal graph-route ablation. It explains local graph
  contribution, not the full enhanced product.
- `deep_graphrag` is an eval alias that maps to `rag_graph_deep`, then lets the
  planner choose among `standard_rag`, `local_graphrag`, `community_global`, or
  `drift_like` based on query features and index health.

Product `enhanced_retrieval` needs stronger guarantees than either current
ablation:

- standard retrieval floor must stay active
- BM25 should be part of the ordinary baseline, not optional hidden behavior
- graph/community/drift should be orchestrated as additive routes
- fallback and route confidence should be product-visible in trace metadata
- internal route names should stay hidden from ordinary users

### 7. If we want formal `standard_retrieval` / `enhanced_retrieval` aliases next, which files need changing?

Minimum alias and contract surface:

- `src/backend/zuno/services/graphrag/models.py`
  - add canonical normalization for `standard_retrieval` and
    `enhanced_retrieval`
- `src/backend/zuno/services/retrieval/planner.py`
  - map those aliases to explicit planner behavior
- `src/backend/zuno/services/retrieval/orchestrator.py`
  - preserve user-facing mode names in trace metadata while still resolving
    internal routes
- `src/backend/zuno/services/rag/handler.py`
  - ensure default retrieval mode resolution and runtime metadata expose the new
    aliases cleanly
- `tools/evals/zuno/multihop_eval/run_real_runtime_eval.py`
  - add product-mode runner labels alongside internal ablations
- related tests under `tests/`
  - update normalization, planner, runner, and eval expectations

Recommended follow-on runtime touchpoints once alias work starts:

- `src/backend/zuno/services/retrieval/models.py`
  - keep planner and trace payloads aligned with the new public names
- frontend settings or retrieval-mode selectors
  - expose only `standard_retrieval` and `enhanced_retrieval`
- docs and eval reports
  - stop leading with `baseline_rag`, `local_graphrag`, and `deep_graphrag`

If product semantics are implemented correctly, the next runner split should be:

- product comparison: `standard_retrieval` vs `enhanced_retrieval`
- internal diagnostics: `vector_only_ablation`, `local_graphrag_ablation`,
  `deep_route_ablation`, `force_graph_diagnostic`

## Immediate Conclusion

Current `baseline_rag` is not equal to the intended product
`standard_retrieval`.

It is better described as:

- historical eval alias
- vector-first baseline
- rerank-enabled
- BM25-disabled in current eval runtime
- not yet the final product baseline contract

That distinction should remain explicit until the runtime and eval runner gain
formal `standard_retrieval` and `enhanced_retrieval` aliases.

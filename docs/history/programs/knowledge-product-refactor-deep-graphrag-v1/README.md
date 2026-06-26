# Knowledge Product Refactor + Deep GraphRAG V1

## Purpose

This directory is a new independent architecture program.

It does not replace the completed closure truth recorded in:

- `docs/architecture/phases/README.md`
- `docs/architecture/phases/phase-00-stable-runtime-recovery.md`
- `docs/architecture/phases/phase-01-langgraph-runtime-deepening.md`
- `docs/architecture/phases/phase-02-graphrag-mainline-deepening.md`
- `docs/architecture/phases/phase-03-domain-pack-formalization.md`
- `docs/architecture/phases/phase-04-local-eval-strengthening.md`
- `docs/architecture/phases/phase-05-docs-and-public-explanation-sync.md`
- `docs/architecture/phases/phase-06-agent-graphrag-pluginization.md`

Those files remain the completed closure truth for the previous architecture round.

This program starts a new round focused on:

```text
Knowledge Product Refactor
  + Deep GraphRAG V1
```

## Current Program Thesis

The repo already has a stable runtime truth:

```text
src/backend/zuno
```

This program does not reopen the retired `services/` migration.

It focuses on a different problem:

```text
turn the existing Knowledge Config / Local GraphRAG capability
into a productized knowledge workflow
with a deeper enhanced retrieval runtime
```

## Product Truth

The product surface should expose only two retrieval modes:

1. `标准检索`
2. `增强检索`

Internal runtime modes may remain more detailed:

- `rag`
- `hybrid_rag`
- `local_graphrag`
- `community_global`
- `drift_like`
- `rag_graph_deep`

Users should not need to understand those internal names.

## Three Core Truths

```text
Domain Pack = reusable domain template
Knowledge Base = indexed instance that binds a Domain Pack
Enhanced Retrieval = routed retrieval umbrella, not one fixed retriever
```

## Phase Order

1. [Phase 0: Program Documentation](phase-00-program-setup.md)
2. [Phase 1: Product Skeleton And API Boundary](phase-01-product-skeleton-api-boundary.md)
3. [Phase 2: Retrieval Strategy Closure](phase-02-retrieval-strategy.md)
4. [Phase 3: Community GraphRAG V1](phase-03-community-graphrag-v1.md)
5. [Phase 4: Global Search / DRIFT-like V1](phase-04-global-drift-v1.md)
6. [Phase 5: Tests And Minimal Eval](phase-05-tests-eval.md)

## Program Rules

1. Do not overwrite the completed closure truth of the earlier `Phase 0-6`.
2. Do not reopen `services/` or `services/api`.
3. Keep runtime truth at `src/backend/zuno`.
4. Keep internal retrieval modes behind the product surface.
5. Archive expired drafts or superseded temporary plans under `docs/history/`.
6. Treat `.agent/` as local execution support only, not repo truth.

## Related Stable Specs

- `docs/history/specs/knowledge-product-boundary.md`
- `docs/history/specs/deep-graphrag-v1-runtime.md`
- `docs/history/specs/domain-pack-builder.md`
- `docs/history/specs/knowledge-config-impact-and-reindex.md`

## Archived Artifacts

- `ui-gallery/`: retired Domain Pack UI capture output from this program.
- `scripts/`: retired UI capture and responsive-check scripts that exercised
  the old Domain Pack settings pages and mock `/api/v1/domain-packs` routes.

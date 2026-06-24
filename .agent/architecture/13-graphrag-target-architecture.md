# GraphRAG Target Architecture

## Purpose

Define the official-compatible GraphRAG target architecture for Zuno.

## Current Evidence

- GraphRAG code exists under `src/backend/zuno/services/graphrag/`.
- Current graph storage uses Neo4j in `client.py`.
- Current retrieval has `GraphRetriever`, graph adapters, community detection,
  report building, global search, and drift-like search.
- Current config stores `graph_index_settings`, `community_report_prompt_id`,
  `index_version`, and `community_version`.
- Current storage and query filters still use `domain_pack_id`.

## External Alignment

Microsoft GraphRAG Query Engine documents Local, Global, DRIFT, Basic, and
Question Generation over completed indexes. Its Prompt Tuning docs place prompt
tuning on the indexing side, with auto tuning using input data and LLM calls to
generate domain-adapted graph-generation prompts.

## Target Project Layout

```text
GraphRAG Project
  settings.yaml
  prompts/
  input/
  output/
  cache/
```

## Target Services

```text
GraphRAGProjectLoader
GraphRAGSettingsValidator
PromptRegistry
PromptTuningService
GraphRAGIndexService
GraphRAGUpdateService
CommunityReportService
GraphRAGQueryRouter
GraphRAGEvidenceBuilder
GraphRAGTraceBuilder
```

## Target Rules

- Prompt Tuning is an indexing-side concern.
- Index and Update must be explicit and versioned.
- Query prompt changes usually do not rebuild the graph.
- `extract_graph` prompt, entity types, chunking, or relation schema changes
  usually require a full re-index.
- Community reports are assets for `global` and `drift`, not a first-level
  query method.
- Domain Pack is retired from the target mainline.
- Do not design a long-term Domain Pack shim.
- Start with Zuno-native official-compatible behavior.
- Keep a future Microsoft GraphRAG adapter boundary open.

## Migration Notes

Replace `domain_pack_id` with `graphrag_project_id` in target contracts. Replace
`local_graphrag`, `community_global`, and `drift_like` with
`local`, `global`, and `drift` at the public contract layer.

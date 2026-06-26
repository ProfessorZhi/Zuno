# GraphRAG Project Architecture

## Purpose

Define the near-term official-compatible GraphRAG target.

## Current Evidence

- `src/backend/zuno/services/graphrag/` contains extractor, graph store,
  retriever, orchestrator, community, and client modules.
- `services/graphrag/client.py` stores entities, relations, and communities in
  Neo4j.
- `KnowledgeService.DEFAULT_KNOWLEDGE_CONFIG` includes `graph_index_settings`,
  `community_report_prompt_id`, `index_version`, and `community_version`.
- `services/graphrag/project/loader.py` loads GraphRAG Project `settings.yaml`,
  validates the contract, discovers prompts, and exposes readiness metadata.
- `services/graphrag/prompts/registry.py` separates indexing prompts from query
  prompts and records rebuild-impact rules for prompt version changes.
- `services/graphrag/versioning.py` records active index/community/hash/status
  metadata and stale-index reasons for trace surfaces.
- `services/retrieval/planner.py` accepts public query methods
  `auto/basic/local/global/drift`, maps old names as compatibility input, and
  records requested/resolved method plus fallback reason.
- Legacy storage and migration compatibility tests still contain
  `domain_pack_id`; the target primary project field is `graphrag_project_id`,
  and graph query policy should be explicit.

## Target Project Layout

```text
GraphRAG Project
  settings.yaml
  prompts/
  input/
  output/
  cache/
```

## Target Components

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

## Rules

- Prompt Tuning is indexing-side.
- Index, Update, and Full Rebuild must be explicit and versioned.
- `extract_graph` prompt, entity types, relation schema, or chunking changes
  usually require full re-index.
- Query prompt changes usually do not rebuild the graph.
- Community reports are assets for `global` and `drift`.
- Community reports are not a first-level query method.
- Domain Pack is retired from the target mainline.
- Do not design a long-term Domain Pack shim.
- Start with Zuno-native official-compatible behavior.
- A Microsoft GraphRAG adapter is a future option, not a near-term requirement.

## Migration Notes

Replace:

```text
domain_pack_id -> graphrag_project_id
local_graphrag -> local
community_global -> global
drift_like -> drift
rag_graph_deep -> enhanced_mode_enabled + query_method
```

Do this at the contract level first. Then migrate storage and frontend fields.

## Acceptance Direction

Later implementation should prove project loading, settings validation,
prompt/index version propagation, community report readiness, frontend/API
migration to public query methods, and complete Enhanced Mode trace metadata.

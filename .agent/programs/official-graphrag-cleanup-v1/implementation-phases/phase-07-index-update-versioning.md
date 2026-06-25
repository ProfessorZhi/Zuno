# Phase 07: Index / Update / Versioning

## Goal

Make index, update, incremental rebuild, and full rebuild boundaries explicit.

## Why This Phase Exists

The current code already carries `index_version`, `community_version`,
`document_hash`, and `chunk_hash`, but the rebuild contract is not yet the
official GraphRAG Project contract.

## Required Reading

- Phase 04 and Phase 06 evidence packages
- `.agent/architecture/near-term/09-persistence-database-storage.md`
- `docs/architecture/specs/enterprise-retrieval-governance.md`

## Scope

Version fields, hash flow, rebuild decision rules, graph/vector/BM25 metadata,
and tests.

## Non-goals

- database migration before contract proof
- frontend UI work
- final runtime legacy deletion

## Candidate Files

- `src/backend/zuno/schema/chunk.py`
- `src/backend/zuno/schema/knowledge.py`
- `src/backend/zuno/services/graphrag/client.py`
- `src/backend/zuno/services/graphrag/graph_store/graph_writer.py`
- `src/backend/zuno/services/pipeline/manager.py`
- `src/backend/zuno/services/rag/vector_db/`
- `src/backend/zuno/services/rag/es_client.py`
- `src/backend/zuno/services/retrieval/models.py`
- `tests/test_hardening01_config_impact_contract.py`
- `tests/test_retrieval_orchestrator.py`

## Execution Order

1. Add tests for vector, graph, community, document, and chunk version flow.
2. Define update vs full rebuild decision inputs.
3. Ensure query traces carry the active versions.
4. Add guards for stale index reuse.
5. Update docs with version rules.

## Acceptance Criteria

- `index_version`, `community_version`, `document_hash`, and `chunk_hash` flow
  through storage and trace.
- Chunking/entity/relation schema changes trigger full rebuild.
- Query prompt changes do not require graph rebuild by default.
- Stale index use is detectable.

## Implemented Version Boundary

Phase 07 adds versioning and stale-detection contracts only. It does not perform
database migration or execute rebuild jobs.

Version flow:

- `GraphRAGVersionState` records `index_version`, `community_version`,
  `document_hash`, `chunk_hash`, and `status`.
- `GraphWriter` preserves `index_version`, `document_hash`, `chunk_hash`,
  `source_chunk_id`, and `status` on graph payloads.
- `RetrievalOrchestrator` metadata includes `index_version`, `index_health`,
  `stale_index_detected`, and `stale_index_reasons`.

Rebuild rules:

| Change | Result |
| --- | --- |
| `index_settings.chunk_mode` | full rebuild |
| `index_settings.chunk_size` | full rebuild |
| `index_settings.overlap` | full rebuild |
| `index_settings.separator` | full rebuild |
| `graph_index_settings.entity_extraction_mode` | full rebuild |
| `graph_index_settings.relation_schema` | full rebuild |
| `graphrag_project.query_prompt_version` | immediate query effect only |

Stale detection examples:

- `graph index health is stale`
- `knowledge status is archived`

## Verification Commands

```powershell
pytest -q tests/test_hardening01_config_impact_contract.py
pytest -q tests/test_retrieval_orchestrator.py
python tools\scripts\verify_docs_entrypoints.py
git diff --check
```

## GitHub Sync Requirements

Before editing:

```powershell
git branch --show-current
git status --short
git log -1 --oneline
```

Before commit:

```powershell
git status --short
git diff --stat
git diff --check
```

After validation passes:

```powershell
git add src/backend/zuno tests docs .agent
git commit -m "feat: harden graphrag index versioning"
git push
```

Forbidden: force push, force-with-lease, amend, unrelated files, or success
claims after failed validation.

## Stop Conditions

- Versioning requires destructive data migration.
- Hash flow cannot be proven with current fixtures.

## Evidence Package Required

- version field flow summary
- rebuild rule table
- trace examples
- test outputs
- commit hash and push result

## Risks

- Partial migration can mix stale graph and fresh vector data.
- Version fields can become passive metadata instead of hard constraints.

## Follow-up Phase

Phase 08: Query Method Router.

# PHASE04 Derived Index Boundary Evidence

phase_id: PHASE04
task_id: P04-T07
requirement_ids:
  - ARCH-INFRA-042
  - ARCH-INFRA-043
  - ARCH-INFRA-044
status: implementation_available
date: 2026-07-18

## Boundary

This evidence proves the PHASE04 derived-index boundary for VECTOR/Milvus, GRAPH/Neo4j and LEXICAL/BM25/Search. These services are represented as versioned, rebuildable, non-authoritative data services in the Infrastructure Capability Profile. They are excluded from the PHASE04 required real-service set and release adapter provenance bundle.

It does not prove current server adapters for Milvus, Neo4j, BM25 or Elasticsearch/Search. It only fixes the infrastructure authority boundary: derived indexes must be rebuilt from authoritative domain/source data and cannot own final facts, ontology or acceptance.

## Verification Results

- vector_index_rebuildable_non_authoritative: passed
- graph_index_rebuildable_non_authoritative: passed
- lexical_index_rebuildable_non_authoritative: passed
- derived_index_versioned_semantics: passed
- server_adapter_not_current_boundary: passed
- derived_indexes_not_required_release_adapters: passed
- derived_indexes_not_authoritative_fact_source: passed

## Commands

```powershell
python tools/scripts/verify_phase04_derived_index_boundary.py
```

Expected result:

```text
PHASE04 derived index boundary verification passed.
```

```powershell
pytest -q tests/repo/test_phase04_derived_index_boundary.py -p no:cacheprovider
```

Expected result:

```text
2 passed
```

## Current

- `VECTOR` uses `milvus-target`, is `authoritative=false`, `rebuildable=true`, `backup_restore_class="rebuild-from-source"` and supports `versioned_index`.
- `GRAPH` uses `neo4j-target`, is `authoritative=false`, `rebuildable=true`, `backup_restore_class="rebuild-from-source"` and supports `versioned_graph`.
- `LEXICAL` uses `bm25-target`, is `authoritative=false`, `rebuildable=true`, `backup_restore_class="rebuild-from-source"` and supports `versioned_lexical_index`.
- Each derived index declares `server_adapter_not_current`, so PHASE04 does not claim the enterprise server adapter is implemented.

## Remaining Target

- Milvus, Neo4j, BM25/Search server adapters, visibility receipts, acceptance gates and rebuild drills remain later implementation targets.
- Knowledge remains the owner of ontology, source evidence and index acceptance.
- Official LangGraph PostgreSQL Checkpointer and full PHASE04 recovery evidence remain blockers.

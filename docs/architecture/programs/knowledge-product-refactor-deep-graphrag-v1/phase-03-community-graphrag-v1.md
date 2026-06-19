# Phase 3: Community GraphRAG V1

## Goal

Add a first community layer on top of the existing entity relation graph.

## V1 Scope

1. read `Entity` / `RELATES_TO` graph edges
2. detect `level=0` communities
3. persist `GraphCommunity`
4. persist `Entity -> IN_COMMUNITY`
5. generate community reports
6. surface community status and metadata

## V1 Limits

1. no full multi-level hierarchy
2. no real-time incremental maintenance
3. file changes may mark community state as stale first
4. community reports are a reusable indexed artifact, not a per-query recomputation

# Near-Term Migration Roadmap

## Purpose

Define the next-stage refactor sequence. Java, microservices, event bus, and
default multi-agent work are intentionally not in this roadmap.

The formal executable implementation program now lives in:

- `.agent/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
- `.agent/programs/zuno-target-architecture-migration-v1/implementation-phases/`
- `.agent/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `.agent/programs/official-graphrag-cleanup-v1/implementation-phases/`
- `.agent/architecture/near-term/17-implementation-phase-map.md`

The compact design-level sequence has been replaced by the formal
implementation phases below. Use the phase files for scope, non-goals,
verification, commit message, and evidence package.

## Current Executable Phase Order

| Phase | Title | Primary migration intent |
| --- | --- | --- |
| 00 | Current State And Program Gate | prove 11A/11B current truth and 11C/12 blockers |
| 01 | Official Cleanup 11C Dependency Removal | remove or explicitly block Domain Pack, `DomainQAGraph`, `MultiAgentSupervisorGraph`, and compat dependencies |
| 02 | Contract Review Asset Migration | preserve useful assets without keeping Domain Pack runtime |
| 03 | GraphRAG Project Mainline Hardening | make `graphrag_project_id`, query methods, evidence, citation, and trace the stable mainline |
| 04 | Repository Layout Cleanup | align files with target ownership and history boundaries |
| 05 | Context Contract Foundation | define `AgentExecutionContext`, `ModelContextPacket`, token budget, and trace contracts |
| 06 | Memory Layer Foundation | separate raw events, short-term state, task memory, long-term memory, and external knowledge |
| 07 | Capability System | select tools, MCP, skills, memory, and evidence by metadata and relevance |
| 08 | GeneralAgent Runtime Integration | use Context Orchestrator and Post-turn Pipeline around one `GeneralAgent` loop |
| 09 | Tests Eval Trace Closure | run full tests, eval baseline, trace proof, docs sync, and final grep gates |

## Current Status

- Official cleanup Phase 01 read-only evidence is complete; Target Migration
  Phase 01 / 11C active dependency removal is still in progress and blocked
  overall.
- Phase 02 docs/spec cleanup is complete.
- Phase 03 public contract retirement introduces `graphrag_project_id` while
  keeping `domain_pack_id` as bounded migration/runtime compatibility.
- Phase 04 adds first-class GraphRAG Project contract fields without claiming a
  loader.
- Phase 05 loads and validates GraphRAG Project settings, discovers prompts,
  and exposes readiness metadata without changing retrieval behavior.
- Phase 06 defines Prompt Registry categories and prompt-version impact rules
  without implementing automatic tuning.
- Phase 07 defines index version, hash flow, full rebuild boundary, and
  stale-index trace detection without database migration.
- Phase 08 implements the backend public Query Method Router for
  `auto/basic/local/global/drift`, keeps old route names as internal or
  compatibility-only, and exposes requested/resolved/fallback trace fields.
- Phase 09 hardens Enhanced Mode pipeline trace for router, multi-retriever
  recall, fusion/rerank, evidence bundle, requery, citation coverage, and
  standard-floor preservation.
- Phase 10 migrates frontend API/types/config utilities to GraphRAG Project and
  public query-method trace fields, and removes old runtime route names from
  `apps/web`.
- Target Migration Phase 00 is ready. Phase 01 should keep already-retired
  runtime legacy, root asset, and Docker surfaces absent and delete or classify
  remaining compat surfaces only after dependency proof.

## Migration Rules

- Do not treat Java, microservices, event bus, or default multi-agent behavior
  as near-term acceptance gates.
- Do not recreate retired Domain Pack runtime, root `domain-packs/`, or the
  former `tests/compat/` holding area.
- Keep old names in history, audits, retired terminology, migration notes, and
  explicit compatibility tests until the final closure gate says otherwise.
- Make public target language GraphRAG Project, Prompt Registry, Query Method,
  Enhanced Mode, evidence, citation, trace, and versioning.

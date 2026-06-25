# Near-Term Migration Roadmap

## Purpose

Define the next-stage refactor sequence. Java, microservices, event bus, and
default multi-agent work are intentionally not in this roadmap.

The formal executable implementation program now lives in:

- `docs/architecture/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `docs/architecture/programs/official-graphrag-cleanup-v1/implementation-phases/`
- `.agent/architecture/near-term/17-implementation-phase-map.md`

The compact design-level sequence has been replaced by the formal
implementation phases below. Use the phase files for scope, non-goals,
verification, commit message, and evidence package.

## Current Executable Phase Order

| Phase | Title | Primary migration intent |
| --- | --- | --- |
| 01 | Legacy Surface Audit | classify old Domain Pack, query-mode, agentchat, compat, and alias surfaces |
| 02 | Docs / Spec / Current Truth Cleanup | prevent current docs and Agent references from steering implementation toward retired surfaces |
| 03 | Domain Pack Contract Retirement | move public contracts toward GraphRAG Project while keeping bounded compatibility reads |
| 04 | GraphRAG Project Contracts | add project identity, settings, prompt, index, query method, and version contract fields |
| 05 | GraphRAG Project Loader / Settings | load `settings.yaml`, discover prompts, and report project readiness |
| 06 | Prompt Registry And Tuning Boundary | make prompt versions and indexing-side prompt tuning explicit |
| 07 | Index / Update / Versioning | define index, update, full rebuild, document hash, chunk hash, and community version semantics |
| 08 | Query Method Router | expose `auto/basic/local/global/drift` and keep old names migration-only |
| 09 | Enhanced Mode Pipeline | prove Enhanced Mode is a complete router, recall, fusion, rerank, evidence, requery, citation pipeline |
| 10 | Frontend API Contract Migration | migrate frontend public contract and UI language to target names |
| 11 | Runtime Legacy Deletion | delete or archive old runtime surfaces only after dependency proof |
| 12 | Tests / Eval / Trace Closure | close tests, evals, trace evidence, grep gates, docs, and phase material |

## Current Status

- Phase 01 is complete as read-only evidence.
- Phase 02 docs/spec cleanup is complete.
- Phase 03 public contract retirement introduces `graphrag_project_id` while
  keeping `domain_pack_id` as bounded migration/runtime compatibility.
- Phase 04 is next and should make GraphRAG Project contracts first-class.

## Migration Rules

- Do not treat Java, microservices, event bus, or default multi-agent behavior
  as near-term acceptance gates.
- Do not delete Domain Pack runtime or `tests/compat/` during docs cleanup.
- Keep old names in history, audits, retired terminology, migration notes, and
  explicit compatibility tests until the final closure gate says otherwise.
- Make public target language GraphRAG Project, Prompt Registry, Query Method,
  Enhanced Mode, evidence, citation, trace, and versioning.

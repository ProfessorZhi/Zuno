# Project Machine Reference

status: canonical-project-machine-index
owner: Project Documentation Owner
human_source: docs/project/project.md
provenance_source: docs/governance/project-fact-provenance.md
current_evidence_source: docs/evidence/

## Project identity

- project: Zuno
- domain: legal intelligence / smart justice
- context: Nanjing University LIPLAB smart-justice research and engineering background; Tianjin court-side related scenarios
- Zuno is not the whole smart-court program.

## Historical baseline

- user joined around 2026-03.
- project and code already existed; a simple custom frontend already existed.
- greenfield: false.
- core R&D team: approximately 7–8 people based on currently recoverable evidence.
- historical milestones currently support: existing product/code → internal demo → customer/smart-court-side demo → quality feedback → iteration → court-side testing → Pilot Validation.
- Pilot Validation does not establish Production.

## Confirmed personal participation

Direction-level participation currently supportable:

- partial Agent development;
- early important Memory work;
- OpenViking Memory / Context integration;
- Tool Calling Strategy related development;
- database inspection / debugging against actual data.

Do not upgrade these into claims that the user independently built the entire Agent Runtime, GraphRAG, RAG stack, backend, or whole Zuno system.

## Claim boundaries

Supported distinction:

```text
team capability != personal implementation
historical pilot != production
current target architecture != historical architecture ownership
research lineage != user implementation
```

## Current / Target / Unknown routing

- History and personal participation → `docs/project/project.md` + provenance.
- Ideal design → `docs/architecture/`.
- Module-level Target → `docs/modules/`.
- Current implementation / tests / eval / runtime facts → `docs/evidence/`.
- Exact personal task PR/interface/SQL/bug/test/result closure → still Unknown unless separately recovered and evidenced.

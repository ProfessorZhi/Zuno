# Project Machine Reference

status: canonical-project-machine-index
owner: Project Documentation Owner
human_source: docs/project/README.md
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

Recovered public Git history additionally supports bounded personal slices in Tool/MCP, GraphRAG retrieval-quality work, and later Context/Memory V2. These do not upgrade into ownership of the whole runtime, retrieval stack, backend, or current architecture.

## Claim boundaries

Supported distinction:

```text
team capability != personal implementation
historical pilot != production
current target architecture != historical architecture ownership
research lineage != user implementation
Target design != Current implementation
```

## Current architecture caveats

- Memory / Context is an optional non-authoritative provider boundary. Provider records do not replace Domain truth; recall/lifecycle policy belongs to Security/Governance, and consumers use only currently eligible snapshots.
- Provenance / source ids establish lineage, not truth, authorization, or semantic-preservation guarantees.
- Current Effect evidence proves durable UNKNOWN recording, duplicate-dispatch suppression, typed restart replay certainty, and a minimal conclusive reconciliation path. Provider remote-query integration and stronger manual-judgment authority binding remain unproven.
- Current `MANDATORY_BEFORE_EFFECT` evidence proves the send gate consumes committed audit proof, fails closed when proof is missing, scopes audit storage by tenant, closes sent rows as `effect_observed`, and closes deterministic pre-send `NOT_DISPATCHED / NO_EFFECT` rows as `dispatch_aborted` so capacity is released without falsifying an observed effect. Audit class and crash/restart lifecycle repair remain unproven.
- GraphRAG tiny-smoke evidence supports a bounded regression-fix story, not general superiority.
- Long-term Memory, Persistent Multi-Agent, Native Runtime and GraphRAG remain measurement-gated complexity.

These caveats describe Current / Target boundaries, not historical-project claims.

## Current / Target / Unknown routing

- History and personal participation → `docs/project/README.md` + provenance.
- Ideal design → `docs/architecture/`.
- Module-level Target → `docs/modules/`.
- Current implementation / tests / eval / runtime facts → `docs/evidence/`.
- Historical negative evidence remains Evidence after a fix; keep the failing run and the later closing SHA/run together instead of rewriting the failure as if it never happened.
- Exact personal task PR/interface/SQL/bug/test/result closure → Unknown unless separately recovered and evidenced.

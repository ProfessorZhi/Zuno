# Modules Machine Reference

status: canonical-module-router
owner: Cross-module Architecture Owner
human_entry: docs/modules/README.md
overall_architecture: docs/architecture/reference.md
current_evidence: docs/evidence/

## Documentation rule

`modules/` contains responsibility units produced by the Target Architecture. Documentation does not assume a permanent module count or permanent numbering in filesystem paths. The current accepted Target decomposition still uses responsibility numbers 01–09 in architecture prose and ADRs; the physical directories use stable semantic names. Future merge/split decisions require Architecture + ADR justification.

## Current Target module routes

- `application/README.md` — 01 Application & Integration: product / integration boundary and delivery semantics.
- `domain/README.md` — 02 Legal Domain & Work Product: formal legal business facts and work products.
- `knowledge/README.md` — 03 Knowledge & Evidence: knowledge generation, readiness, retrieval lineage and candidates.
- `runtime/README.md` — 04 Agent Runtime & Control: long-running task control, planning and recovery state.
- `capability/README.md` — 05 Capability & Skill: stable professional capability and provider qualification.
- `effects/README.md` — 06 Tool Runtime & Effects: prepared actions, external attempts, effect truth and reconcile.
- `model-gateway/README.md` — 07 Model Gateway: model role, routing, attempts, quota and cost facts.
- `security/README.md` — 08 Security & Governance: authorization, approval, security epoch and policy decisions.
- `evaluation/README.md` — 09 Observability & Evaluation: telemetry, evaluation and complexity evidence.

## For a module implementation task

Read in this order:

```text
overall architecture Part B
→ target semantic module README Part B
→ target module Part C
→ relevant neighboring semantic module B/C
→ ADR
→ Evidence
→ code / migration / tests
```

Part A is explanatory context and interview-ready narrative. Part B/C is the implementation contract. Evidence decides whether the contract is already Current.

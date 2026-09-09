# Modules Engineering Reference

status: canonical-module-router
owner: Cross-module Architecture Owner
human_entry: docs/modules/README.md
overall_architecture: docs/architecture/reference.md
current_evidence: docs/evidence/

## Documentation rule

`modules/` contains responsibility units produced by the Target Architecture. Documentation does not assume a permanent module count or permanent numbering in filesystem paths. The current accepted Target decomposition still uses responsibility numbers 01–09 in architecture prose and ADRs; physical directories use stable semantic names. Future merge/split decisions require Architecture + ADR justification.

Each semantic module has two coordinated views:

```text
README.md      Human Narrative: why this responsibility exists and how it behaves
reference.md   Part B Engineering Reference + Part C Cross-Module Consistency
```

The split changes information density, not ownership. A module reference may specify Target contracts and failure semantics, but `docs/evidence/` remains the authority for whether they are Current.

## Current Target module routes

| Current Target | Human narrative | Engineering reference |
| --- | --- | --- |
| 01 Application & Integration | `application/README.md` | `application/reference.md` |
| 02 Legal Domain & Work Product | `domain/README.md` | `domain/reference.md` |
| 03 Knowledge & Evidence | `knowledge/README.md` | `knowledge/reference.md` |
| 04 Agent Runtime & Control | `runtime/README.md` | `runtime/reference.md` |
| 05 Capability & Skill | `capability/README.md` | `capability/reference.md` |
| 06 Tool Runtime & Effects | `effects/README.md` | `effects/reference.md` |
| 07 Model Gateway | `model-gateway/README.md` | `model-gateway/reference.md` |
| 08 Security & Governance | `security/README.md` | `security/reference.md` |
| 09 Observability & Evaluation | `evaluation/README.md` | `evaluation/reference.md` |

## For a module implementation task

Read in this order:

```text
overall architecture reference.md
→ target semantic module reference.md
→ relevant neighboring module reference.md
→ ADR
→ Evidence
→ code / migration / tests
```

If the task requires reconstructing why a boundary exists, read the corresponding README before changing the reference. Do not alter Owner, Authority, Recovery, Security or Current/Target semantics merely to make the two views read more smoothly.

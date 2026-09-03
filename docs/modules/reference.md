# Modules Machine Reference

status: canonical-module-router
owner: Cross-module Architecture Owner
human_entry: docs/modules/README.md
overall_architecture: docs/architecture/reference.md
current_evidence: docs/evidence/

## Documentation rule

`modules/` contains responsibility units produced by the Target Architecture. Documentation does not assume a permanent module count. The current accepted Target decomposition still uses the existing numbered module set; future merge/split decisions require Architecture + ADR justification.

## Current Target module routes

- `01-application-integration.md` — product / integration boundary and delivery semantics.
- `02-legal-domain-work-product.md` — formal legal business facts and work products.
- `03-knowledge-evidence.md` — knowledge generation, readiness, retrieval lineage and candidates.
- `04-agent-runtime-control.md` — long-running task control, planning and recovery state.
- `05-capability-skill.md` — stable professional capability and provider qualification.
- `06-tool-runtime-effects.md` — prepared actions, external attempts, effect truth and reconcile.
- `07-model-gateway.md` — model role, routing, attempts, quota and cost facts.
- `08-security-governance.md` — authorization, approval, security epoch and policy decisions.
- `09-observability-evaluation.md` — telemetry, evaluation and complexity evidence.

## For a module implementation task

Read in this order:

```text
overall architecture Part B
→ target module Part B
→ target module Part C
→ relevant neighboring module B/C
→ ADR
→ Evidence
→ code / migration / tests
```

Part A is explanatory context and interview-ready narrative. Part B/C is the implementation contract. Evidence decides whether the contract is already Current.

# RB-ARCH-REFRAME-V1 Blue Change Set

## CHANGE-001

Source Cluster IDs: CLUSTER-001, CLUSTER-002, CLUSTER-003, CLUSTER-004
User Gate: APPROVED
Sync Status: APPLIED
Canonical Paths: docs/decisions/0009-python-only-backend.md; docs/decisions/0010-microservice-target-and-service-boundaries.md; docs/project/architecture/architecture.md; docs/project/services/service-architecture.md; docs/project/deployment/microservice-deployment.md
Applied Commit SHA: d264dbd
Validation Run: architecture reframe, link, governance, red-blue and focused pytest suite passed
Validation Not Run: full CI and production service/eval evidence
Retest IDs: RETEST-001

Decision: Python-only and Microservice remain Target constraints; five network-facing services are the current Target candidate; workers, protocols, K8s and physical DB splits remain evidence-gated.

## CHANGE-002

Source Cluster IDs: CLUSTER-005, CLUSTER-006
User Gate: APPROVED
Sync Status: APPLIED
Canonical Paths: docs/project/README.md; docs/project/architecture/README.md; docs/project/architecture/architecture-views.md; docs/project/architecture/architecture.html; docs/project/product/; docs/project/domain/; docs/project/agents/; docs/project/knowledge/; docs/project/services/; docs/project/data/; docs/project/security/; docs/project/eval/; docs/project/deployment/; .agent/system.yaml; AGENTS.md
Applied Commit SHA: d264dbd
Validation Run: architecture reframe, link, governance, red-blue and focused pytest suite passed
Validation Not Run: full CI and production service/eval evidence
Retest IDs: RETEST-001

Decision: replace 11 Module + 1 Architecture as canonical taxonomy; old module documents are explicitly Superseded/History and no longer own current Target facts.

# Round-002 Canonical Snapshot

BASE_SHA: 19ba6e050e1334f71c511a5968c9ea9d15c68111
Snapshot status: ACCEPTED_TARGET
Snapshot rule: Round-002 attacks current Canonical docs, not old Lab candidates.

## Sources

- docs/project/architecture/
- docs/project/product/
- docs/project/domain/
- docs/project/agents/
- docs/project/knowledge/
- docs/project/services/
- docs/project/data/
- docs/project/security/
- docs/project/eval/
- docs/project/deployment/
- docs/governance/architecture-gate-policy.md
- docs/status/production-readiness.md

## Frozen constraints

Python-only Target, Microservice Deployment Target, Domain Owner of Canonical State, Runtime/Domain
State separation, Single Controller, Provider Proposal boundary, Security/Approval/Evidence gates.

## Attackable candidates

Service count, Graph, Memory Provider, Model Gateway, LangGraph, Tool/Sandbox physical boundary,
Database/Queue/Storage providers, Multi-Agent profiles and all unmeasured quality or efficiency claims.

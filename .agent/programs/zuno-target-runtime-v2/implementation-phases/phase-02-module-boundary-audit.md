# Phase 02 Module Boundary Audit

## Goal

Document the first low-risk backend boundary candidates and add verifier gates
before moving files.

## Deliverables

- `evidence/module-boundary-audit.md`
- `.agent/scripts/verify_module_boundaries.py`

## Candidate Areas

- `src/backend/zuno/api/services/knowledge_query.py`
- `src/backend/zuno/services/application/context/`
- `src/backend/zuno/services/application/capabilities/`
- `src/backend/zuno/services/graphrag/query_service.py`

## Stop Conditions

- import impact becomes broad.
- a move requires database schema, dependency, frontend, or streaming rewrite.
- a verifier would force Target wording into Current documentation.

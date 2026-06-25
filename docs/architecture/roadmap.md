# Architecture Roadmap

## Current

The completed Phase 0-6 architecture closure is historical truth.

The active program is official GraphRAG cleanup and alignment.

Phase 01 through Phase 10 are complete.

Those phases cover contract, loader, prompt registry, index versioning, query
router, Enhanced Mode, and frontend API migration stages.

## Next Step

Phase 11 is Runtime Legacy Deletion.

Do not start Phase 11 by deleting files. First prove that each deletion
candidate has no active import, route, launcher, eval, or test dependency.

## Blocked Legacy

These surfaces are confirmed legacy directionally, but still current or blocked
by active dependencies:

- `domain-packs/`
- `src/backend/zuno/services/domain_pack/`
- `src/backend/zuno/core/graphs/domain_qa_graph.py`
- `tests/compat/`

## Non-Goals

The active roadmap does not implement Java services, split microservices,
event workers, database migrations, dependency upgrades, or default multi-agent
mode.

## Agent Execution Sources

Detailed implementation planning lives in:

- `.agent/programs/current.md`
- `.agent/programs/official-graphrag-cleanup-v1/`
- `.agent/architecture/near-term/17-implementation-phase-map.md`

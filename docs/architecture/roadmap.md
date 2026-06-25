# Architecture Roadmap

## Current

The completed Phase 0-6 architecture closure is historical truth.

The active program is official GraphRAG cleanup and alignment.

Phase 01 through Phase 10 are complete. Those phases cover contract, loader,
prompt registry, index versioning, query router, Enhanced Mode, and frontend API
migration stages.

## Phase Status

- Phase 11A: complete. Commit `24abdd9` introduced the project query runtime:
  `KnowledgeQueryService`, `GraphRAGQueryService`,
  `GraphRAGProjectSnapshot`, and `KnowledgeQueryResult`.
- Phase 11B: complete. Commit `b160c4b` unified knowledge queries under the
  single `GeneralAgent` path through `search_knowledge_base` and
  `KnowledgeQueryService`.
- Phase 11C: blocked. Active dependencies remain in `domain-packs/`, Domain
  Pack route/service/frontend/eval/Docker surfaces, `DomainQAGraph`,
  `MultiAgentSupervisorGraph`, and `tests/compat/`.
- Phase 12: partial / not closed. Focused tests exist, but final full `pytest`
  and formal Eval baseline comparison are not complete.

## Next Actions

1. 11C active dependency removal
2. Contract Review asset migration
3. full pytest
4. eval baseline comparison
5. program closure

## Next Candidate

Context Memory Agent Runtime V1 is the next candidate / design-ready program.
It is not active Current implementation. Phase 00 must wait for 11C/12 closure
or explicitly re-verify dependencies before implementation starts.

## Blocked Legacy

These surfaces are confirmed legacy directionally, but still current or blocked
by active dependencies:

- `domain-packs/`
- `src/backend/zuno/api/v1/domain_packs.py`
- `src/backend/zuno/services/domain_pack/`
- `src/backend/zuno/core/graphs/domain_qa_graph.py`
- `src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py`
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

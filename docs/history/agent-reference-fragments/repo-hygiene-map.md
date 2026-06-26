# Repository Hygiene Map

## Purpose

Classify repository directories for cleanup decisions.

## Current

- `apps/`: Current
- `src/backend/zuno/`: Current
- `docs/`: Current formal docs
- `.agent/`: Current Agent workflow library
- `examples/graphrag-projects/`: Target examples
- `docs/history/domain-packs/root-contract-review/`: History
- `docs/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/`:
  History for retired Domain Pack UI gallery capture/check scripts and old
  Phase 6 bundle staging helpers
- `docs/history/programs/official-graphrag-cleanup-v1/`: History
  for the completed GraphRAG cleanup source program absorbed by target
  migration
- `docs/history/specs/`: History for superseded migration specs
  that no longer belong on the active specs front path
- `docs/history/decisions/`: History for superseded architecture
  decisions that no longer influence the current mainline
- `tests/compat/`: Retired
- `data/`: Generated unless promoted
- `reports/`: Generated unless promoted
- `.local/`: Local
- `.codex/`: Local
- `node_modules/`: Generated

## Phase 11C Progress

The current FastAPI router no longer mounts `/domain-packs`, and active Vue
knowledge route/settings entrypoints no longer open Domain Pack pages. The
old frontend Domain Pack API/page files are retired from `apps/web/src/`.
`KnowledgeService.get_runtime_settings` no longer auto-loads `DomainPackLoader`
from `domain_pack_id`. `GraphRetriever` policy resolution also no longer loads
`DomainPackLoader` from `domain_pack_id`. `GraphRetrieverAdapter`,
`GraphRetriever`, `GraphWriter`, structured graph extraction, pipeline graph
indexing, and the Neo4j client use `graphrag_project_id` as the primary graph
scope while dual-reading legacy graph properties for pre-backfill data.
Stackless local eval and the
dedicated Contract Review eval can build from GraphRAG Project assets, and
their extractor calls use `project_payload=project_payload`. The direct
`DomainQAGraph` source, legacy graph state module, and
`src/backend/zuno/services/domain_pack/` runtime service package are retired
from current backend source. Root Domain Pack assets have moved to
`docs/history/domain-packs/root-contract-review/`, and Docker no
longer copies or mounts `/app/domain-packs`. The former `tests/compat/`
holding area is retired; remaining migration compatibility coverage now lives
in root `tests/`.

## Rule

Do not delete Blocked Legacy. Do not commit Generated or Local outputs.
`tests/compat/` must not be restored as target repository layout. Archived root
Domain Pack assets must not be restored as target repository layout.
Retired Phase 6 bundle helpers must not be restored under active
`tools/scripts/`. Superseded migration specs under
`docs/history/specs/` must stay reachable as history instead of
returning to the active specs front path. Active public-release staging helpers
must not stage or name already-retired Domain Pack route/API, graph, runtime,
or service source paths as current release groups, and must not use broad
backend add paths that cross release-group boundaries.
Read `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
before directory-boundary work.
Superseded executable programs must live under `docs/history/programs/`,
not under `.agent/programs/`. API route modules under `src/backend/zuno/api/v1/`
should call API service adapters instead of importing runtime/service/core/tool
modules directly.

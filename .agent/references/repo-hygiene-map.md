# Repository Hygiene Map

## Purpose

Classify repository directories for cleanup decisions.

## Current

- `apps/`: Current
- `src/backend/zuno/`: Current
- `docs/`: Current formal docs
- `.agent/`: Current Agent workflow library
- `examples/graphrag-projects/`: Target examples
- `docs/architecture/history/domain-packs/root-contract-review/`: History
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
`DomainPackLoader` from `domain_pack_id`. Stackless local eval and the
dedicated Contract Review eval can build from GraphRAG Project assets. The
direct `DomainQAGraph` source, legacy graph state module, and
`src/backend/zuno/services/domain_pack/` runtime service package are retired
from current backend source. Root Domain Pack assets have moved to
`docs/architecture/history/domain-packs/root-contract-review/`, and Docker no
longer copies or mounts `/app/domain-packs`. The former `tests/compat/`
holding area is retired; remaining migration compatibility coverage now lives
in root `tests/`.

## Rule

Do not delete Blocked Legacy. Do not commit Generated or Local outputs.
`tests/compat/` must not be restored as target repository layout. Archived root
Domain Pack assets must not be restored as target repository layout.
Read `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
before directory-boundary work.

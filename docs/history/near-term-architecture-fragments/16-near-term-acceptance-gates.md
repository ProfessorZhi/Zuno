# Near-Term Acceptance Gates

## Purpose

State what would prove the near-term architecture is actually ready later.

## Documentation Gates

- `near-term/` remains the main refactor design path.
- `future/` topics do not appear as near-term acceptance requirements.
- `decisions/` records locked choices and retired surfaces.
- the formal implementation program is linked from
  `docs/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
  and `.agent/architecture/near-term/17-implementation-phase-map.md`.

## Contract Gates

- API route tests prove routes delegate use cases to services.
- Service tests prove runtime context and command mapping.
- Graph tests prove node order, fallback, citation check, and trace finalization.
- Retrieval tests prove Basic, Local, Global, and DRIFT routing semantics.
- Frontend API tests prove public fields use target names.

## Evidence Gates

- Basic RAG includes BM25 when available, dense vector, fusion, rerank or
  fallback ranking, evidence check, requery, and citations.
- Enhanced Mode trace records requested method, resolved method, retrievers,
  fallback reason, evidence bundle, and citation coverage.
- GraphRAG Project trace records project id, prompt version, index version, and
  community version where applicable.

## Program Closure Gates

- every implementation phase returns its evidence package.
- final grep gates classify retired terms by allowed and disallowed location.
- final docs are updated from fresh runtime, test, eval, and trace evidence.

## Scope Gates

Do not close a near-term phase by claiming Java, service extraction, event bus,
worker extraction, or default multi-agent behavior is ready. Those belong to
future direction until the user opens a separate implementation program.

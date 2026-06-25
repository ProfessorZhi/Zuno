# Repository Layout And Module Boundaries

## Purpose

Define Target / Proposed repository layout rules for future architecture and
directory work. This file is normative text; the visual reference remains
`./zuno-ideal-architecture-and-repo-layout.html`.

## Target Top-Level Directories

- `apps/`: product clients such as web and desktop.
- `src/backend/zuno/`: current Python modular-monolith backend.
- `docs/`: human-facing Current, Target, Roadmap, evidence, and history.
- `.agent/`: Agent workflow, design-stage target detail, verifier scripts, and
  local operating aids.
- `tools/`: repo maintenance, launchers, and eval tooling.
- `tests/`: repository verification and focused regression tests.
- `infra/`: Docker, database, and deployment infrastructure.

## Backend Dependency Direction

Dependencies should flow inward by responsibility:

```text
api -> application services -> core/runtime -> providers/adapters
services -> retrieval / graphrag / storage / persistence boundaries
```

Core/runtime must not depend backward on API routes. API routes must not own
business logic or retrieval strategy. Shared DTO or contract changes must sync
API, frontend clients, and tests in the same change set.

## Package Ownership

- `src/backend/zuno/api/`: HTTP route and request/response boundary.
- `src/backend/zuno/api/services/`: API-facing use cases and orchestration
  adapters.
- `src/backend/zuno/core/`: Agent, graph, and runtime orchestration.
- `src/backend/zuno/services/graphrag/`: GraphRAG Project query/index service
  concepts.
- `src/backend/zuno/services/retrieval/`: retrieval planning and orchestration.
- `src/backend/zuno/services/storage/` and `database/`: persistence and storage
  integration.
- `apps/web/src/apis/`: frontend API clients.
- `.agent/references/`: current code path and command indexes, not target
  architecture prose.

## Current To Target Migration Principles

- Classify every touched surface as Current, Target, Future, History, Generated,
  Local, or Blocked Legacy before moving it.
- Keep formal Current facts in `docs/architecture/current-architecture.md`.
- Keep high-level Target direction in `docs/architecture/target-architecture.md`.
- Keep detailed target contracts in `.agent/architecture/near-term/`.
- Keep executable phase work in `.agent/programs/`.
- Keep superseded evidence under `docs/architecture/history/`.

## Forbidden Catch-All Packages

Do not create vague catch-all packages named only `services`, `core`, `utils`,
`common`, or `helpers` without a clear owner and boundary. New modules must name
the business or infrastructure capability they own.

## Generated / Local / History Destinations

- Generated artifacts: ignore or place under a generated output directory.
- Local machine state: `.agent/local/`, `.local/`, or another ignored local
  path.
- Historical evidence: `docs/architecture/history/`.
- Agent-only reusable workflow: `.agent/workflows/`, `.agent/references/`, or
  `.agent/templates/`.

## Blocked Legacy Rule

`domain-packs/`, Domain Pack route/service/frontend/eval/Docker surfaces, and
`tests/compat/` are Blocked Legacy until 11C proves active dependency removal.
The direct `DomainQAGraph`, legacy graph state, and
`MultiAgentSupervisorGraph` sources are retired from current backend source and
must not be recreated as target repository layout. Blocked Legacy surfaces must
not be deleted to satisfy a layout verifier unless the relevant active
dependency removal proof exists.

## File Move Acceptance Gates

Before moving or deleting files:

1. `git status --short`
2. Reference search for imports, routes, scripts, evals, docs, and tests.
3. Classification of Current / Target / Future / History / Generated / Local /
   Blocked Legacy.
4. Update affected docs, `.agent` references, verifiers, and tests.
5. Run the smallest meaningful verifier set plus `git diff --check`.

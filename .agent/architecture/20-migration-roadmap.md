# Migration Roadmap

## Purpose

Define later implementation phases. This file is a proposed roadmap, not proof
of completion.

## Phase A: Docs / Spec Cleanup

Goal: make this target architecture readable and synchronized.
Scope: `.agent/architecture`, docs entrypoints, program README.
Candidate files: `.agent/`, `docs/architecture/`, `AGENTS.md`.
Acceptance gates: workflow verification and docs entrypoint tests.
Runtime code: no.

## Phase B: agentchat / legacy Surface Deletion

Goal: remove retired compatibility front paths.
Candidate files: legacy/compat modules and tests after inventory.
Acceptance gates: public import tests and runtime chain guard.
Runtime code: yes.

## Phase C: Domain Pack Retirement

Goal: remove Domain Pack from future front-path architecture.
Candidate files: API, service, config, frontend, graph filters.
Acceptance gates: replacement GraphRAG project contract tests.
Runtime code: yes.

## Phase D: GraphRAG Project Loader And Settings

Goal: introduce `graphrag_project_id`, `settings.yaml`, and project loader.
Runtime code: yes.

## Phase E: Prompt Tuning And Indexing

Goal: prompt registry, prompt versioning, indexing-side prompt tuning.
Runtime code: yes.

## Phase F: Query Method Router And Enhanced Mode

Goal: public query methods `auto/basic/local/global/drift`.
Runtime code: yes.

## Phase G: Storage Versioning

Goal: prompt, index, document, chunk, and community versions.
Runtime code: yes.

## Phase H: Frontend API Surface

Goal: standard/enhanced product UI plus advanced query methods.
Runtime code: yes.

## Phase I: Java Business Layer Integration

Goal: business service adapter and context propagation.
Runtime code: yes, future extension.

## Phase J: Microservices Readiness

Goal: service contracts, queues, data ownership, deployment boundaries.
Runtime code: maybe.

## Phase K: Multi-Agent Mode

Goal: supervisor and specialist contracts for complex tasks.
Runtime code: yes.

## Phase L: Tests / Eval / Closure

Goal: prove no regression and close the program.
Runtime code: tests/evals only unless failures require fixes.

## Dependencies

Do not start C before D has a replacement contract. Do not start I/J/K as
runtime work until A-F give a stable AI runtime boundary.

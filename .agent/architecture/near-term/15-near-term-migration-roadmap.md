# Near-Term Migration Roadmap

## Purpose

Define the next-stage refactor sequence. Java, microservices, event bus, and
default multi-agent work are intentionally not in this roadmap.

The formal executable implementation program now lives in:

- `docs/architecture/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `docs/architecture/programs/official-graphrag-cleanup-v1/implementation-phases/`
- `.agent/architecture/near-term/17-implementation-phase-map.md`

The phase notes below remain the compact design-level sequence. Use the formal
implementation phases for target-mode execution.

## Phase 01: docs/spec cleanup

Goal: keep architecture entrypoints clear and route future material out of the
near-term path.

Scope: docs, `.agent`, program README, target summaries.

Candidate files: `.agent/architecture/`, `.agent/references/`,
`docs/architecture/`, `AGENTS.md`.

Acceptance gates: workflow verification and docs entrypoint tests.

Verification commands: `.agent/scripts/verify-workflow.ps1`,
`python tools/scripts/verify_docs_entrypoints.py`,
`pytest -q tests/test_docs_entrypoints.py`.

Risks: stale links, future material leaking into near-term acceptance gates.

## Phase 02: agentchat / legacy surface deletion

Goal: remove retired compatibility front paths from current architecture.

Scope: legacy entrypoint inventory, imports, tests, route/docs references.

Candidate files: legacy/compat modules, alias tests, docs references.

Acceptance gates: public import tests, runtime chain guard, route smoke tests.

Verification commands: targeted pytest for public entrypoints and runtime guard.

Risks: hidden compatibility dependency in tests or launchers.

## Phase 03: Domain Pack retirement

Goal: replace Domain Pack as GraphRAG front-path concept.

Scope: API config, runtime settings, graph filters, frontend config names,
docs, migration notes.

Candidate files: `api/services/knowledge.py`, `services/domain_pack/`,
`services/graphrag/`, frontend knowledge config, docs.

Acceptance gates: GraphRAG Project contract tests pass; retired fields appear
only in migration/retired docs or compatibility reads.

Verification commands: targeted knowledge config/API tests and grep for retired
fields.

Risks: data compatibility and graph filters still rely on `domain_pack_id`.

## Phase 04: GraphRAG Project loader and settings

Goal: introduce `graphrag_project_id`, settings validation, project layout, and
project context.

Scope: project loader, settings validator, runtime context, tests.

Acceptance gates: project can load settings/prompts and expose project context
to retrieval traces.

Verification commands: unit tests for loader, settings validator, service
context, and trace.

Risks: confusing Knowledge Base and GraphRAG Project ownership.

## Phase 05: Prompt tuning and indexing

Goal: define prompt registry/versioning and indexing-side prompt tuning.

Scope: prompt version metadata, index/update/full rebuild decision rules.

Acceptance gates: prompt/index changes produce correct rebuild decisions.

Verification commands: config impact tests and graph index tests.

Risks: query prompt changes accidentally triggering graph rebuilds.

## Phase 06: Query method router and enhanced mode

Goal: expose `auto/basic/local/global/drift` and keep Enhanced Mode as pipeline.

Scope: planner, orchestrator, trace fields, tests.

Acceptance gates: auto router chooses expected method and fallback is traceable.

Verification commands: retrieval planner/orchestrator tests and eval fixtures.

Risks: graph paths hurting Basic baseline quality.

## Phase 07: storage versioning

Goal: align prompt, index, document, chunk, and community versions.

Scope: database config, graph store metadata, vector/BM25 metadata, trace.

Acceptance gates: query trace proves version consistency.

Verification commands: persistence and GraphRAG tests.

Risks: partial migrations and stale index reuse.

## Phase 08: frontend API surface

Goal: update product contract to GraphRAG Project and query methods.

Scope: frontend API types, config utils, settings pages, backend DTOs.

Acceptance gates: standard/enhanced product UX stays simple; advanced method
controls use target names.

Verification commands: frontend contract tests and UI route checks.

Risks: exposing old route names to users.

## Phase 09: tests/eval/closure

Goal: prove the near-term architecture does not regress retrieval quality.

Scope: docs checks, unit tests, real runtime/eval checks where applicable.

Acceptance gates: docs entrypoints pass, target runtime tests pass, eval gates
show Basic baseline preservation and trace coverage.

Verification commands: workflow/docs checks plus targeted pytest and eval runs.

Risks: narrow tests being treated as broad architecture proof.

# Architecture Docs

This directory is the formal architecture entrypoint for Zuno.

It keeps four boundaries explicit:

1. `docs/` is the formal documentation truth.
2. `AGENTS.md` is the repository-level Agent entrypoint.
3. `.agent/` is the Agent workflow library, not formal truth.
4. `docs/architecture/history/` archives superseded plans, old programs, and replaced designs.

## Start Here

If you want the shortest current path, read:

1. [Current Architecture](current-architecture.md)
2. [Target Architecture](target-architecture.md)
3. [Architecture Upgrade Phases](./phases/README.md)
4. [Official GraphRAG Cleanup V1](./programs/official-graphrag-cleanup-v1/README.md)
5. [Architecture Upgrade Design](./specs/architecture-upgrade-2026-06.md)

For the detailed design-stage target architecture v0.1, also read:

- `../../.agent/architecture/README.md`
- `../../.agent/architecture/00-architecture-index.md`

That working set is more detailed than the formal summary here, but it remains
target/proposed design material until synchronized into formal docs and runtime
code.

## Directory Map

```text
docs/architecture/
  README.md
  current-architecture.md
  target-architecture.md
  transition-strategy.md
  phases/
  programs/
  specs/
  decisions/
  audits/
  history/
    programs/
```

Related Agent working set:

```text
.agent/
  architecture/
```

## What Each Layer Means

- `current-architecture.md`
  - what the repo is today
- `target-architecture.md`
  - what the active direction is trying to make true
- `transition-strategy.md`
  - migration rules and constraints
- `phases/`
  - completed Phase 0-6 closure truth for the previous architecture round
- `programs/`
  - active independent architecture programs
- `specs/`
  - stable architecture definitions
- `decisions/`
  - major architecture choices and why they were made
- `audits/`
  - evidence gathered before or during implementation phases
- `history/`
  - older plans, archived programs, readiness notes, and legacy execution materials
- `.agent/architecture/`
  - detailed target architecture v0.1 design-stage working set, not formal truth

## Agent Workflow Boundary

- `AGENTS.md` tells Agents how to enter the repository and maintain the workflow system.
- `.agent/` stores Agent references, templates, and read-only verification scripts.
- `.agent/` may point to `docs/`, but it must not become the only place where formal conclusions live.

## Current Rule

Do not treat historical execution notes as the active architecture path.

The current active program is:

- [Official GraphRAG Cleanup V1](./programs/official-graphrag-cleanup-v1/README.md)

The superseded knowledge-product program is archived at:

- [Knowledge Product Refactor + Deep GraphRAG V1](./history/programs/knowledge-product-refactor-deep-graphrag-v1/README.md)

Use `history/` only when you need:

- historical phase evidence
- older refactor reasoning
- older readiness or staging context

Relative path hints:

- `./current-architecture.md`
- `./target-architecture.md`
- `./phases/README.md`
- `./history/README.md`
- `./specs/enterprise-retrieval-governance.md`

## Stable Spec Reading Order

If you want the deeper technical model after reading the current path:

1. [Architecture Upgrade Design](./specs/architecture-upgrade-2026-06.md)
2. [LangGraph Runtime](./specs/langgraph-runtime.md)
3. [Retrieval Orchestrator](./specs/retrieval-orchestrator.md)
4. [Enterprise Retrieval Governance](./specs/enterprise-retrieval-governance.md)
5. [RAG Evaluation And Observability](./specs/rag-evaluation-and-observability.md)
6. [Layered Backend And Service Evolution](./specs/layered-backend-and-service-evolution.md)
7. [Platform Evolution And Future Direction](./specs/platform-evolution-and-future-direction.md)

## Maintenance Rule

After every major structure, runtime, evaluation, feature, refactor, or architecture replacement, review:

- this index
- the current architecture file
- the target architecture file
- the active program or phase file
- the affected specs, ADRs, and audits
- `AGENTS.md`
- `.agent/references/`

The goal is simple:

```text
keep architecture docs smaller, current, and structurally honest
```

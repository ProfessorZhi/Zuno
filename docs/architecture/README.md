# Architecture Docs

This directory is the current architecture truth for Zuno.

Its job is to keep four things aligned:

1. the current repo reality
2. the target architecture
3. the completed and active architecture programs
4. the stable architecture specs that explain why the system is shaped this way

## Start Here

If you want the shortest current path, read:

1. [Current Architecture](current-architecture.md)
2. [Stable Baseline Recovery And Runtime Deepening Plan](./plans/stable-baseline-recovery-and-runtime-deepening-plan.md)
3. [Target Architecture](target-architecture.md)
4. [Transition Strategy](transition-strategy.md)
5. [Architecture Upgrade Phases](./phases/README.md)
6. [Knowledge Product Refactor + Deep GraphRAG V1](./programs/knowledge-product-refactor-deep-graphrag-v1/README.md)
7. [Architecture Upgrade Design](./specs/architecture-upgrade-2026-06.md)

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
  history/
```

## What Each Layer Means

- `current-architecture.md`
  - what the repo is today
- `target-architecture.md`
  - what this upgrade is trying to make true
- `transition-strategy.md`
  - migration rules and constraints
- `phases/`
  - phase model for the architecture program
  - current phase completion truth and closure gates
- `programs/`
  - new independent architecture programs that start after a previous round is already closed
  - use this layer when future work should not overwrite earlier completion truth
- `specs/`
  - stable architecture definitions
- `decisions/`
  - major architecture choices and why they were made
- `history/`
  - older plans, audits, readiness notes, and legacy execution materials
  - see [Architecture History](./history/README.md)

Relative path hints:

- `./current-architecture.md`
- `./target-architecture.md`
- `./phases/README.md`
- `./history/README.md`
- `./specs/enterprise-retrieval-governance.md`

## Current Rule

Do not treat historical execution notes as the active architecture path.

Use `history/` only when you need:

- historical phase evidence
- older refactor reasoning
- older readiness or staging context

## Stable Spec Reading Order

If you want the deeper technical model after reading the current path:

1. [Architecture Upgrade Design](./specs/architecture-upgrade-2026-06.md)
2. [Domain Pack + LangGraph + GraphRAG Architecture](./specs/domain-pack-langgraph-graphrag-architecture.md)
3. [LangGraph Runtime](./specs/langgraph-runtime.md)
4. [Retrieval Orchestrator](./specs/retrieval-orchestrator.md)
5. [Enterprise Retrieval Governance](./specs/enterprise-retrieval-governance.md)
6. [RAG Evaluation And Observability](./specs/rag-evaluation-and-observability.md)
7. [Layered Backend And Service Evolution](./specs/layered-backend-and-service-evolution.md)
8. [Platform Evolution And Future Direction](./specs/platform-evolution-and-future-direction.md)

## Maintenance Rule

After every major structure, runtime, or evaluation change, review:

- this index
- the current architecture file
- the target architecture file
- the active phase file
- the affected specs

The goal is simple:

```text
keep architecture docs smaller, current, and structurally honest
```

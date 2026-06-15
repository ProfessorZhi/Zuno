# Stable Baseline Recovery And Runtime Deepening Plan

## Purpose

This plan records a deliberate pause of the root-level `services/` migration line.

The immediate priority is no longer:

```text
keep forcing the paused repo-boundary migration forward before the runtime is stable
```

The immediate priority is:

```text
return to one stable, runnable backend baseline
  -> keep apps/web and apps/desktop as the app shells
  -> keep src/backend/zuno as the Python backend main package
  -> then deepen LangGraph, GraphRAG, Domain Pack, and local eval
```

This is a recovery-and-realignment plan, not a claim that the repo has already been restored.

## Why This Pivot Exists

The paused migration attempt exposed a real constraint:

1. part of the runnable surface was redirected into a new root
2. but the remaining runtime still depended on unresolved compatibility surfaces elsewhere in the repo
3. once those surfaces were only partially split, the import and startup story stopped being single and obvious

The most valuable next step is therefore not to keep pushing the repo-boundary move.
It is to recover a stable backend runtime first, then continue architecture upgrades from a working baseline.

## Decision

Until the recovery work is complete:

1. do not continue treating root-level `services/` as the active backend runtime destination
2. treat the current `services/` migration tree as a work-in-progress snapshot, not the mainline target
3. keep `apps/web` and `apps/desktop` as valid top-level app shells
4. restore `src/backend/zuno` as the stable Python backend runtime root
5. shift architecture effort toward runtime quality, not repo-boundary motion

## Stable Baseline Shape

The recovery target is:

```text
Zuno/
  apps/
    web/
    desktop/
  src/
    backend/
      zuno/
        main.py
        api/
        core/
        services/
        database/
        schema/
        tools/
        utils/
        prompts/
        domain_packs/
  docs/
  infra/
  tools/
  tests/
```

This plan does not propose reverting `apps/` back into `src/frontend`.
The stable baseline keeps the app shells under `apps/`.

## Non-Goals

This recovery plan explicitly does not do the following:

1. it does not introduce root-level `services/` as the active backend code root
2. it does not rename `src/backend/zuno` to `apps/api`
3. it does not split real microservices
4. it does not require multi-repo decomposition
5. it does not remove `uvicorn zuno.main:app` as the backend entrypoint
6. it does not force large directory churn that does not improve runtime stability

The guiding rule is:

```text
monorepo now, service-ready later
```

## Recovery Program Phases

This recovery line should be executed as a separate phased program.

Its order is:

```text
Phase 0: Stable Runtime Recovery
  -> Phase 1: LangGraph Runtime Deepening
  -> Phase 2: GraphRAG Mainline Deepening
  -> Phase 3: Domain Pack Formalization
  -> Phase 4: Local Eval Strengthening
  -> Phase 5: Docs And Public Explanation Sync
```

### Phase 0: Stable Runtime Recovery

This phase exists for one reason:

```text
get back to one stable, runnable version first
```

Work in this phase:

1. preserve the paused migration-era runtime surface as reference, not as current truth
2. restore `src/backend/zuno` as the stable backend runtime root
3. restore one valid backend startup path
4. restore import closure for the main runtime modules
5. restore focused runtime and entrypoint tests

The stable backend path should again prove:

```text
src/backend/zuno/main.py exists
uvicorn zuno.main:app is the backend entry
README, Docker, and local launcher docs all point to a real startup path
```

The baseline must support direct imports from:

- `zuno.main`
- `zuno.core.graphs.domain_qa_graph`
- `zuno.services.retrieval.orchestrator`
- `zuno.services.graphrag.retriever`
- `zuno.services.domain_pack.loader`

Phase 0 exit rule:

```text
the repo can start, import, and pass focused runtime checks again
```

Phase 0 user checkpoint:

```text
once Phase 0 is complete, stop and let the user personally try the runtime
before moving into deeper architecture upgrades
```

### Phase 1: LangGraph Runtime Deepening

Do not start this phase until Phase 0 is complete and the recovered baseline has been user-checked.

Primary targets:

- `src/backend/zuno/core/graphs/domain_qa_graph.py`
- `src/backend/zuno/core/graphs/states.py`
- `src/backend/zuno/core/runtime/agent_runtime.py`

Goals:

- make LangGraph the explicit runtime backbone
- standardize state fields
- keep node boundaries clean
- centralize finalize and failure handling

### Phase 2: GraphRAG Mainline Deepening

Do not start this phase until Phase 1 has produced a cleaner runtime backbone.

Primary targets:

- `src/backend/zuno/services/retrieval/orchestrator.py`
- `src/backend/zuno/services/retrieval/planner.py`
- `src/backend/zuno/services/retrieval/fusion.py`
- `src/backend/zuno/services/graphrag/retriever.py`

Goals:

- keep `RetrievalOrchestrator` as the unified retrieval entry
- make retrieval mode decisions explicit
- reduce business-specific hardcoding inside GraphRAG internals

### Phase 3: Domain Pack Formalization

Do not start this phase until GraphRAG has a cleaner orchestration boundary.

Primary target:

- `src/backend/zuno/domain_packs/contract_review/`

Goals:

- move contract-review-specific retrieval cues and aliases into pack data
- keep loader and validator behavior explicit
- make templates and prompts part of a stable pack contract

### Phase 4: Local Eval Strengthening

Do not start this phase until the runtime and retrieval contracts are stable enough to compare repeatably.

Primary targets:

- `tools/evals/zuno/rag_eval/`
- `tools/evals/zuno/contract_review_eval/`
- `tests/compat/`

Goals:

- preserve stackless local evaluation
- keep profile-to-profile comparison stable
- make GraphRAG gains provable against baseline RAG

### Phase 5: Docs And Public Explanation Sync

Do not treat this as optional cleanup.
It is the point where the recovered architecture and the deeper runtime story become explainable again.

Goals:

- make README match the recovered stable structure
- make architecture docs match the real runtime shape
- remove stale migration-first language from first-read surfaces
- keep abandoned or paused migration material in history, not on the front path

## Validation Gates For Recovery

Recovery is not complete until the repo can prove all of the following from the restored stable structure:

```text
python -c "import zuno.main"
python -c "from zuno.core.graphs.domain_qa_graph import DomainQAGraph"
python -c "from zuno.services.retrieval.orchestrator import RetrievalOrchestrator"
python -c "from zuno.services.graphrag.retriever import GraphRetriever"
```

And from the repo root:

- focused import and entrypoint tests pass
- focused LangGraph runtime tests pass
- focused retrieval-mode tests pass
- focused Domain Pack tests pass
- repo-structure and docs-entrypoint verification still pass

## Documentation Rule During Recovery

Until the stable structure is actually restored:

1. `current-architecture.md` should keep describing the real current repo state
2. this plan should carry the recovery intent
3. historical migration attempt details should remain reachable through `history/`
4. README and support docs may describe mixed runtime facts, but they must not present the paused migration line as the current execution goal

## Expected End State

After this recovery-and-realignment plan is executed, the repo should be explainable in one clean sentence:

```text
Zuno is a local-first Agent Workspace that keeps apps/web and apps/desktop as app shells,
keeps src/backend/zuno as the stable Python backend package,
uses LangGraph as the explicit runtime backbone,
uses a Retrieval Orchestrator to unify RAG and GraphRAG,
uses Domain Packs to hold contract-review-specific knowledge contracts,
and uses local eval to prove retrieval quality improvements.
```

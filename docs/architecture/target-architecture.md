# Target Architecture

## Purpose

This file describes the target shape for the current architecture direction. It is the desired structure, not the current state.

## Target Shape Now

The next target is not immediate root-level service extraction.

The next target is:

```text
one stable, explainable monorepo baseline
  -> apps/web
  -> apps/desktop
  -> src/backend/zuno
  -> strong LangGraph runtime
  -> official GraphRAG-aligned project settings, prompt tuning, and query method boundaries
  -> strong local evaluation proof
  -> self-maintaining docs and Agent workflow
```

The detailed design-stage version of this target is:

- `.agent/architecture/`

That directory is Zuno Target Architecture v0.1. It is intentionally more
detailed than this formal summary and includes proposed future boundaries for
Java business services, microservices, and multi-agent mode. Treat those
sections as target/proposed, not current implementation truth.

## Target Repository Shape

```text
Zuno/
  apps/
    web/
    desktop/
  src/
    backend/
      zuno/
  infra/
  tools/
  tests/
  docs/
  .agent/
  AGENTS.md
```

## Target Directory Meaning

```text
apps              = user-facing application shells
src/backend/zuno  = stable Python backend package
infra             = deployment and environment infrastructure
tools             = scripts, launchers, eval tooling, migration helpers
tests             = repo-level verification and end-to-end checks
docs              = current truth, programs, specs, workflow, history
.agent            = Agent workflow references, templates, and scripts
AGENTS.md         = Agent entrypoint
```

## Target Runtime Mainline

The backend should be easy to explain as:

```text
LangGraph runtime
  -> retrieval planning
  -> Basic RAG with BM25 + dense vector + fusion + rerank
  -> Local GraphRAG retrieval
  -> official GraphRAG-aligned project settings
  -> prompt tuning and query method selection
  -> later Global search over community reports
  -> evidence fusion
  -> answer + citation check
  -> evaluation + proof
```

The GraphRAG target order should remain:

```text
Query Method: basic
  BM25 + dense vector + fusion + rerank, no graph/community assets

Query Method: local
  entity-specific graph + raw chunk search

Query Method: global
  map-reduce over community reports

Query Method: drift
  community primer + follow-up local/basic retrieval
```

Community reports are target assets for `global` and `drift`; they are not a
first-level query method.

## Target Evolution Rule

The repo should remain:

```text
monorepo now, service-ready later
```

That means:

1. keep `src/backend/zuno` stable first
2. deepen runtime quality second
3. only reopen repo-boundary migration after the runtime is stable and testable
4. keep docs and Agent workflow synchronized as the architecture changes

## Target Documentation Rule

The docs system should expose only these current-truth layers on the front path:

1. `current`
2. `target`
3. `program`
4. `phase`
5. `spec`
6. `decision`

Everything older belongs in:

- `history`
- `reference`
- `development`

Agent workflow has its own boundary:

- `AGENTS.md` is the Agent entrypoint.
- `.agent/` is the Agent workflow library.
- `.agent/` does not replace formal docs.

# Migration Notes

## Agent Entrypoint

`agent.md` has been replaced by `AGENTS.md`.

Do not recreate `agent.md` as a long-term stub. If a script or test depends on it, update that dependency to `AGENTS.md`.

## Program Archival

Superseded programs move to:

```text
docs/architecture/history/programs/
```

The current active program remains under:

```text
docs/architecture/programs/
```

## Domain Pack Mainline

Domain Pack remains historical and supporting context, but the current cleanup program should align the future front path with official GraphRAG Project, Prompt Tuning, and Query Method concepts.

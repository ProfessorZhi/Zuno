# Migration Notes

## Agent Entrypoint

`agent.md` has been replaced by `AGENTS.md`.

Do not recreate `agent.md` as a long-term stub. If a script or test depends on it, update that dependency to `AGENTS.md`.

## Program Archival

Superseded programs move to:

```text
docs/architecture/history/programs/
```

Completed programs move under:

```text
docs/architecture/history/programs/
```

`.agent/programs/current.md` records whether a new executable Agent program is
active. After the target architecture migration closure, there is no active
executable program.

## Domain Pack Mainline

Domain Pack remains historical and supporting context. The current front path is
official GraphRAG Project, Prompt Tuning, and Query Method concepts.

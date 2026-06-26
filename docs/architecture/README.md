# Architecture

This is the formal architecture entrypoint for Zuno.

## Read First

1. [Current Architecture](current-architecture.md)
2. [Target Architecture](target-architecture.md)
3. [Roadmap](roadmap.md)
4. [Public Evidence](../evidence/public-demo.md)
5. [Architecture Decisions](decisions/README.md)

## Program Status

The active executable Agent program is:

- `.agent/programs/zuno-target-runtime-v2/`

It follows the completed target architecture migration closure with controlled
runtime and documentation phases. Completed detailed V2 Phase 00-04 files are
archived under:

- `docs/architecture/history/programs/zuno-target-runtime-v2/`

The completed target architecture migration program is archived under:

- `docs/architecture/history/programs/zuno-target-architecture-migration-v1/`

`docs/architecture/history/programs/official-graphrag-cleanup-v1/` preserves
the completed 11A/11B/11C cleanup evidence as history. It is not an active
executable Agent program.

The completed Phase 0-6 architecture closure remains historical truth. It is
archived under:

- [history/phases/](history/phases/)

## Directory Map

```text
docs/architecture/
  README.md
  current-architecture.md
  target-architecture.md
  roadmap.md
  decisions/
  history/
```

## Boundaries

- Current: what the repository really does now.
- Target: the near-term direction, without claiming it is implemented.
- Roadmap: current status, next step, blockers, and accepted non-goals.
- History: completed or superseded plans, programs, phases, audits, and older
  Agent workflow material.

`AGENTS.md` is the repository-level Agent entrypoint. Agent workflow aids live
in `.agent/`. Formal conclusions that humans should read live in `docs/`.

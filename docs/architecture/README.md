# Architecture

This is the formal architecture entrypoint for Zuno.

## Read First

1. [Current Architecture](current-architecture.md)
2. [Target Architecture](target-architecture.md)
3. [Roadmap](roadmap.md)
4. [Public Evidence](../evidence/public-demo.md)
5. [Architecture Decisions](decisions/README.md)

## Current Program

The active program is target architecture migration. Its detailed execution
material is maintained for Agents under:

- `.agent/programs/zuno-target-architecture-migration-v1/`
- `.agent/programs/official-graphrag-cleanup-v1/`
- `.agent/architecture/near-term/`

`official-graphrag-cleanup-v1` remains referenced because its completed 11A/11B
work and blocked 11C/12 cleanup are dependencies of the target migration.

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

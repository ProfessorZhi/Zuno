# Current Architecture Reference

This directory is an Agent quick reference. It does not replace formal truth in `docs/architecture/`.

Use it to orient quickly, then verify against:

1. `docs/architecture/README.md`
2. `docs/architecture/current-architecture.md`
3. `docs/architecture/target-architecture.md`
4. `docs/architecture/history/programs/zuno-target-architecture-migration-v1/README.md`

The current rule is simple: docs hold decisions, `AGENTS.md` tells Agents how to enter, `.agent/` helps Agents work, and `history/` keeps superseded material out of the front path.

For the detailed target architecture v0.1 design, read:

- `.agent/architecture/README.md`
- `.agent/architecture/00-architecture-index.md`
- `.agent/architecture/near-term/README.md`

For near-term refactor work, prioritize `.agent/architecture/near-term/`.
Read `.agent/architecture/future/` only for Java, microservices, event/workers,
or multi-agent direction. This directory remains the quick current-reality
reference.

When the task is to implement the near-term target architecture, use the formal
implementation roadmap first:

- `docs/architecture/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
- `docs/architecture/history/programs/zuno-target-architecture-migration-v1/implementation-phases/README.md`
- `.agent/architecture/near-term/17-implementation-phase-map.md`

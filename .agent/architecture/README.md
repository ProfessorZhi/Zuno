# Zuno Target Architecture v0.1

This directory holds the detailed target architecture design for Zuno v0.1.

This is design-stage material. It is not an implementation-complete claim. The
documents may describe proposed or future capabilities, but those sections must
stay labeled as `Target Design`, `Future Extension`, `Migration Notes`, or
`Open Questions`.

## Boundary

- `docs/architecture/` is the formal human documentation truth.
- `.agent/references/current_architecture/` is the quick current-reality snapshot for Agents.
- `.agent/architecture/` is the detailed ideal target architecture working set.
- `AGENTS.md` remains the repository workflow contract.

Before implementation work starts, read this directory after the formal docs.
When a target decision becomes accepted formal truth, synchronize the smaller
conclusion into `docs/architecture/` instead of leaving it only here.

## Reading Order

Start with [00-architecture-index.md](00-architecture-index.md), then follow the
sequence from system context through migration, decisions, open questions, and
glossary.

# Current Agent Program

The current executable program is:

- [Zuno Target Architecture Migration V1](zuno-target-architecture-migration-v1/README.md)

Current status:

- Phase 00 is complete for the current run: Git, focused Phase 11A/11B tests,
  and legacy grep evidence were re-verified.
- Phase 01 is in progress and still blocked overall. The current FastAPI router
  no longer mounts `/domain-packs`, and active Vue knowledge routes/pages no
  longer open Domain Pack entrypoints.
- Phase 11A and Phase 11B from `official-graphrag-cleanup-v1` are complete.
- Phase 11C remains blocked by Domain Pack services/assets, retained legacy
  endpoint/frontend files, `AgentRuntime`, `DomainQAGraph`,
  `MultiAgentSupervisorGraph`, Docker/eval surfaces, and `tests/compat/`
  dependencies.
- Phase 12 is partial / not closed.
- Context/Memory implementation is folded into this program after repository
  layout and GraphRAG mainline gates.

Superseded candidate program:

- `context-memory-agent-runtime-v1` is archived under
  `docs/architecture/history/programs/context-memory-agent-runtime-v1/`.

Formal public status is summarized in:

- `docs/architecture/roadmap.md`

# Current Agent Program

The current executable program is:

- [Zuno Target Architecture Migration V1](zuno-target-architecture-migration-v1/README.md)

Current status:

- Phase 00 is complete for the current run: Git, focused Phase 11A/11B tests,
  and legacy grep evidence were re-verified.
- Phase 01 is in progress and still blocked overall. The current FastAPI router
  no longer mounts `/domain-packs`, and active Vue knowledge routes/pages no
  longer open Domain Pack entrypoints. Workspace knowledge prefetch/tools no
  longer import `AgentRuntime` or call `_run_domain_pack_query`; they use
  `KnowledgeQueryService`.
- Phase 11A and Phase 11B from `official-graphrag-cleanup-v1` are complete.
- Phase 11C remains blocked by Domain Pack services/assets, retained legacy
  endpoint/frontend files, `DomainQAGraph`, Docker/eval surfaces, and
  `tests/compat/` dependencies. The standalone `AgentRuntime` facade and
  direct `MultiAgentSupervisorGraph` source have been removed from current
  backend source and exports. `DomainQAGraph` and
  `MultiAgentSupervisorGraph` are no longer exported from current core package
  public surfaces; only the direct `DomainQAGraph` source remains Blocked
  Legacy.
- Phase 12 is partial / not closed.
- Context/Memory implementation is folded into this program after repository
  layout and GraphRAG mainline gates.

Superseded candidate program:

- `context-memory-agent-runtime-v1` is archived under
  `docs/architecture/history/programs/context-memory-agent-runtime-v1/`.

Formal public status is summarized in:

- `docs/architecture/roadmap.md`

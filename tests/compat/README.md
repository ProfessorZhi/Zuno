# Compatibility Tests

This folder keeps repo-level runtime regression tests that are still useful even when they are not part of the main front path.

Why it lives here instead of `src/backend/zuno/`:

- `src/backend/zuno/` is the runtime package, not a source-owned test tree
- keeping these checks under the repo-level `tests/` tree keeps the runtime boundary cleaner
- legacy-oriented assertions can be rewritten here without reintroducing alias packages

## Phase 11C Classification

This directory is a mixed Current / Blocked Legacy surface. Some tests still
protect active legacy runtime paths such as standalone `AgentRuntime`,
`DomainQAGraph`, `MultiAgentSupervisorGraph`, Domain Pack loader, and eval
compatibility. Other tests are retired compatibility or replacement evidence
and should prove that replaced surfaces stay removed.

`test_general_agent_domain_pack_runtime.py` is retired compatibility evidence:
the current `GeneralAgent` no longer exposes the old
`KnowledgeService` / `AgentRuntime` / `RagHandler` Domain Pack path.

`test_workspace_domain_pack_runtime.py` is replacement evidence for Phase 11C:
the current Workspace knowledge prefetch/tool path no longer exposes
`AgentRuntime`, `domain_qa_runtime`, or `_run_domain_pack_query`; it uses the
GraphRAG Project query runtime through `KnowledgeQueryService`.

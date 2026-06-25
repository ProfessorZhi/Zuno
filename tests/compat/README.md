# Compatibility Tests

This folder keeps repo-level runtime regression tests that are still useful even when they are not part of the main front path.

Why it lives here instead of `src/backend/zuno/`:

- `src/backend/zuno/` is the runtime package, not a source-owned test tree
- keeping these checks under the repo-level `tests/` tree keeps the runtime boundary cleaner
- legacy-oriented assertions can be rewritten here without reintroducing alias packages

## Phase 11C Classification

This directory is a mixed Current / Blocked Legacy surface. Some tests still
protect eval or asset compatibility. Other tests are retired compatibility or
replacement evidence and should prove that replaced surfaces stay removed,
including `DomainQAGraph`, the Domain Pack runtime service, and
`MultiAgentSupervisorGraph`.

`test_general_agent_domain_pack_runtime.py` is retired compatibility evidence:
the current `GeneralAgent` no longer exposes the old
`KnowledgeService` / `AgentRuntime` / `RagHandler` Domain Pack path.

`test_workspace_domain_pack_runtime.py` is replacement evidence for Phase 11C:
the current Workspace knowledge prefetch/tool path no longer exposes
`AgentRuntime`, `domain_qa_runtime`, or `_run_domain_pack_query`; it uses the
GraphRAG Project query runtime through `KnowledgeQueryService`.

`test_agent_runtime_multi_agent.py` is retired compatibility evidence: the
standalone `AgentRuntime` facade module no longer exists. `DomainQAGraph` and
`MultiAgentSupervisorGraph` are no longer public core package exports or
current backend source modules.

`test_domain_qa_graph_retirement.py` proves the former direct
`DomainQAGraph` module and its legacy graph state module stay retired from the
current backend source. Root-level runtime import tests track the GraphRAG
Project mainline.

`test_domain_pack_runtime_service_retirement.py` proves the former
`zuno.services.domain_pack` runtime service stays retired from current backend
source.

`test_contract_review_domain_pack.py` keeps Contract Review compatibility
coverage through the GraphRAG Project payload shape instead of the old Domain
Pack loader. It remains here until the root `domain-packs/` assets and Docker
surfaces are fully retired.

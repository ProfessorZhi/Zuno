# Compatibility Tests

This folder keeps repo-level runtime regression tests that are still useful even when they are not part of the main front path.

Manual probes without default pytest tests have been removed from this folder.
Do not add new human-run scripts here; either create a hermetic root test or
preserve evidence under `docs/architecture/history/`.

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

Root Phase 11C tests now own retired-source and retired-import guards for
`AgentRuntime`, `DomainQAGraph`, `MultiAgentSupervisorGraph`, legacy graph
state modules, and the former `zuno.services.domain_pack` runtime service.

`test_contract_review_domain_pack.py` keeps Contract Review compatibility
coverage through the GraphRAG Project payload shape instead of the old Domain
Pack loader. It remains here until the remaining compatibility coverage is
either promoted to current tests or retired; root `domain-packs/` assets and
Docker `/app/domain-packs` mounts are already retired.

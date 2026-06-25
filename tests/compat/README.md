# Compatibility Tests

This folder keeps repo-level runtime regression tests that are still useful even when they are not part of the main front path.

Why it lives here instead of `src/backend/zuno/`:

- `src/backend/zuno/` is the runtime package, not a source-owned test tree
- keeping these checks under the repo-level `tests/` tree keeps the runtime boundary cleaner
- legacy-oriented assertions can be rewritten here without reintroducing alias packages

## Phase 11C Classification

This directory is a mixed Current / Blocked Legacy surface. Some tests still
protect active legacy runtime paths such as `DomainQAGraph`,
`MultiAgentSupervisorGraph`, Domain Pack loader, and eval compatibility. Other
tests are retired compatibility or replacement evidence and should prove that
replaced surfaces stay removed.

`test_general_agent_domain_pack_runtime.py` is retired compatibility evidence:
the current `GeneralAgent` no longer exposes the old
`KnowledgeService` / `AgentRuntime` / `RagHandler` Domain Pack path.

`test_workspace_domain_pack_runtime.py` is replacement evidence for Phase 11C:
the current Workspace knowledge prefetch/tool path no longer exposes
`AgentRuntime`, `domain_qa_runtime`, or `_run_domain_pack_query`; it uses the
GraphRAG Project query runtime through `KnowledgeQueryService`.

`test_agent_runtime_multi_agent.py` is retired compatibility evidence: the
standalone `AgentRuntime` facade module no longer exists. `DomainQAGraph` and
`MultiAgentSupervisorGraph` are no longer public core package exports, while
their direct source modules remain Blocked Legacy.

`test_domain_qa_graph_runtime.py` and `test_multi_agent_supervisor_runtime.py`
are moved Phase 5 legacy runtime tests. They remain here as Blocked Legacy
coverage while root-level runtime import tests track the GraphRAG Project
mainline.

`test_domain_qa_graph_langgraph_runtime_deepening.py` is moved Phase 1
legacy graph/runtime behavior coverage. It remains here as Blocked Legacy
coverage because the current mainline is the single `GeneralAgent` project
query path.

`test_domain_pack_formalization.py` and `test_contract_review_domain_pack.py`
are moved Domain Pack / Contract Review asset-runtime coverage. They remain
here until Contract Review assets migrate to GraphRAG Project ownership in
Phase 02.

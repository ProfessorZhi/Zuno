# Zuno Target Runtime V2 Implementation Roadmap

## Objective

Implement the target runtime architecture in small, verifiable phases after the
completed target architecture migration closure.

The program must keep this distinction:

- Current: code and tests already prove it.
- Foundation: a minimal callable slice exists, but product behavior is not
  mature.
- Target: the next architecture to implement.
- Future: outside this program.
- History: archived evidence and superseded plans.

## Completed Foundation Slice

| Phase | Status | Result |
| --- | --- | --- |
| 00 | Complete | Re-verified current state before writing. |
| 01 | Complete | Opened this executable program and updated pointers. |
| 02 | Complete | Added module boundary audit and migration gates. |
| 03 | Complete | Moved the first low-risk backend boundary. |
| 04 | Complete | Added minimal callable Context Orchestrator runtime. |

Detailed Phase 00-04 files and evidence are archived under:

- `docs/history/programs/zuno-target-runtime-v2/`

## Future Execution Phases

### Phase 05: Memory Engine

Goal: mature the Context / Memory Engine without changing product claims before
tests prove behavior.

Scope:

- Raw Event Log append and replay contract.
- L0 Working Context and L1 Recent Interaction Window policy.
- L2 Task Summary Memory using Summary Compression.
- L3 Structured Long-term Memory candidates using Structured Extraction.
- `source_event_ids` preservation for summaries and structured memories.
- ContextTrace for selection, eviction, and token budget decisions.

Non-scope:

- database schema changes unless a later approved phase explicitly opens them.
- product-level memory UX.
- treating External Knowledge as Agent Memory.

Exit criteria:

- `prepare_context` can consume recent window, summaries, structured memory
  candidates, and evidence without breaking the single `GeneralAgent` path.
- post-turn memory commit preserves raw events before summaries.
- tests prove Raw Event Log is not replaced by summary memory.
- docs update Current / Foundation / Target wording after code is proven.

Verification:

- focused memory/context tests.
- `python .agent/scripts/verify_agent_system.py`
- `python .agent/scripts/verify_doc_boundaries.py`
- `python tools/scripts/verify_repo_structure.py`
- `git diff --check`

### Phase 06: Capability / Tool Retrieval

Goal: stop relying on broad all-tool schema injection by introducing a
retrievable ToolCard layer.

Scope:

- ToolCard registry contract.
- keyword and alias exact lookup.
- Native BM25 over ToolCard text.
- optional vector capability retrieval behind an adapter boundary.
- permission, health, side-effect, cost, and latency filtering.
- `CapabilitySelectionTrace`.

Non-scope:

- changing tool behavior itself.
- adding new external dependencies for BM25.
- making product-level dynamic orchestration claims before focused tests pass.

Exit criteria:

- selected ToolCards and injected schemas are traceable.
- rejected capability candidates include reasons.
- Native BM25 has deterministic scoring tests and `explain_score`.
- all-tool injection remains available only as bounded fallback where needed.

Verification:

- focused capability selector tests.
- Native BM25 unit tests for tokenization, idf, scoring, and ranking.
- permission/filter trace tests.
- documentation/verifier suite.

### Phase 07: Knowledge Retrieval / Fusion

Goal: implement the target retrieval/fusion path around the existing
`KnowledgeQueryService` and `GraphRAGQueryService` boundaries.

Scope:

- Native BM25 document retriever.
- multi-query variant generation in enhanced / expensive mode only.
- multi-retriever recall across Native BM25, dense vector, graph local, and
  community global sources.
- stable-id deduplication.
- RRF fusion with default `k = 60`.
- optional rerank adapter boundary.
- evidence bundle, citation coverage, fusion trace, and optional rerank trace.
- GraphRAG methods `basic`, `local`, `global`, `drift`; `auto` remains a
  router, not a fifth mode.

Non-scope:

- replacing GraphRAG Project with Domain Pack.
- treating Elasticsearch as the BM25 algorithm.
- overwriting historical eval baselines.

Exit criteria:

- original query is preserved in trace when query variants are generated.
- requested and resolved GraphRAG method are both recorded.
- fallback reasons are explicit when graph/community assets are unavailable.
- RRF and citation coverage are test-covered.

Verification:

- focused retrieval/fusion tests.
- focused GraphRAG router tests.
- selected eval smoke only when the phase explicitly needs it.
- documentation/verifier suite.

### Phase 08: GeneralAgent LangGraph Runtime

Goal: make the runtime graph explicit while preserving the single
`GeneralAgent` conversational path.

Scope:

- explicit `prepare_context -> agent_loop -> post_turn_commit` graph.
- LangGraph checkpoint, resume, interrupt, and recovery boundaries.
- LangChain model/message/tool/structured-output adapters.
- per-step trace ids and context/capability/retrieval trace propagation.
- streaming behavior compatibility.

Non-scope:

- restoring `DomainQAGraph`, `MultiAgentSupervisorGraph`, or `AgentRuntime`.
- introducing default multi-agent chat behavior.
- broad package moves.

Exit criteria:

- old streaming behavior remains compatible.
- one chat request enters exactly one `GeneralAgent` mainline.
- LangGraph state transitions are test-covered.
- post-turn commit is observable and failure-safe.

Verification:

- focused GeneralAgent runtime tests.
- streaming contract tests.
- trace propagation tests.
- documentation/verifier suite.

### Phase 09: Product Boundary / Trace / Eval Closure

Goal: close the V2 implementation with user-facing boundaries, trace evidence,
and eval documentation.

Scope:

- typed API fields for context, capability, query method, evidence, citation,
  trace, latency, and cost metadata.
- frontend display boundaries for memory/capability/evidence state.
- eval profile updates only when the phase explicitly authorizes them.
- closure evidence for full selected test suite, targeted evals, and grep
  classification.
- front-path slimming closure for `docs/` and `.agent/`: active entrypoints stay
  small, superseded plans/lessons/fragments stay reachable under
  `docs/history/`, and transient screenshots/caches stay out of
  git.
- archive completed phase evidence under
  `docs/history/programs/zuno-target-runtime-v2/`.

Non-scope:

- full frontend redesign.
- full pytest/eval reruns unless required for closure.
- Java services, microservices, event workers, or default multi-agent mode.

Exit criteria:

- product/API docs distinguish Current, Foundation, Target, Future, and History.
- `docs/` and `.agent/` expose only the necessary current entrypoints,
  executable workflow, target design, references, scripts, skills, templates,
  and archived history pointers.
- trace/eval evidence records prompt version, query prompt version, index
  version, community version, latency, and nullable cost.
- legacy grep has no unclassified active mainline hits.
- active program surface remains slim after closure.

Verification:

- selected docs/verifier suite.
- focused API/frontend contract tests where touched.
- targeted evals only when this phase opens eval scope.
- final `git diff --check`, commit, and push.

## Cross-phase Guardrails

- Do not move whole packages at once.
- Do not rewrite `GeneralAgent.astream()` streaming behavior without focused
  streaming tests.
- Do not add database schema, dependency, Docker, or eval-runner changes unless
  the current phase explicitly authorizes them.
- Do not restore `DomainQAGraph`, `MultiAgentSupervisorGraph`, `AgentRuntime`,
  root `domain-packs/`, or Domain Pack frontend pages.
- Do not make `domain_pack_id` an active public target field.
- Do not write Target behavior as Current until code and tests prove it.

## Source Of Truth

Implementation phases read the canonical target design first:

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`

Completed evidence moves to history; active program docs stay small.

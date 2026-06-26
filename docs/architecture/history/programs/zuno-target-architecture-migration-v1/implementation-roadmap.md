# Zuno Target Architecture Migration V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move Zuno from the current Phase 11A/11B state to the near-term target architecture and repository layout.

**Architecture:** Keep the current Python/FastAPI modular monolith, finish GraphRAG Project migration, remove Domain Pack from the active path, then add Context/Memory and Capability boundaries around the single `GeneralAgent`. Historical and superseded plans stay in `docs/architecture/history/`; executable Agent work stays in `.agent/programs/`.

**Tech Stack:** Python, FastAPI, LangGraph, Vue, GraphRAG/RAG services, pytest, `.agent` workflow verifiers.

---

## Program Gate

Do not start implementation phases until Phase 00 proves current state from
Git, code, tests, and grep. Do not remove any Blocked Legacy surface until the
phase that owns it proves active dependency removal.

## Phase Overview

| Phase | Status | Main Output |
| --- | --- | --- |
| 00 | complete | current-state and dependency gate |
| 01 | complete for active runtime cleanup | official cleanup 11C dependency removal |
| 02 | complete | Contract Review asset migration |
| 03 | complete for public GraphRAG Project mainline | GraphRAG Project mainline hardening |
| 04 | complete | repository layout cleanup |
| 05 | complete | Context contract foundation |
| 06 | complete | Memory layer foundation |
| 07 | complete | Capability System |
| 08 | complete | single GeneralAgent runtime integration |
| 09 | final | full tests, eval, trace, docs, and grep closure |

Current Phase 01/03 closure includes GraphRAG Project scoped graph writes and
retrieval through `graphrag_project_id`, eval/extractor paths using
`project_payload` as the primary GraphRAG Project payload name, and bounded
dual-read compatibility for pre-backfill graph data.

Phase 04 closure archives superseded executable programs out of
`.agent/programs/`, keeps `official-graphrag-cleanup-v1` under
`docs/architecture/history/programs/`, and tightens API controller boundaries
so capability/tool routes call API service adapters instead of importing
runtime service modules directly.

Phase 05 closure adds typed context contracts under
`zuno.services.application.context`: `AgentExecutionContext`,
`ModelContextPacket`, `TokenBudgetPolicy`, `ContextTrace`, `ContextItem`,
`ContextSource`, and `ContextSelectionReason`. These contracts are Current
code, while Context Orchestrator runtime integration remains Phase 08.

Phase 06 closure adds typed memory layer foundation contracts under
`zuno.services.memory.layers`: `MemoryLayer`, `MemoryScope`, `RawMemoryEvent`,
`TaskMemorySummary`, `MemoryCandidate`, `ExternalKnowledgeRecord`,
`RetentionPolicy`, and `InMemoryLayerStore`. Existing `memory_client`
persistence remains unchanged; Phase 08 owns runtime integration.

Phase 07 closure adds typed capability foundation contracts under
`zuno.services.application.capabilities`: `CapabilityRecord`,
`CapabilityType`, `CapabilityRegistry`, `CapabilitySelectionRequest`,
`CapabilitySelectionTrace`, and `DynamicCapabilitySelector`. The existing
capability search service now returns unified capability metadata
(`type`, `schema`, `permissions`, `cost`, `health`, `source`, and `owner`)
for tools, skills, MCP servers, and MCP tools while preserving previous
API-facing fields. GeneralAgent runtime selection remains Phase 08.

Phase 08 closure wires the existing single `GeneralAgent` loop through a
minimal `prepare_context -> agent_loop -> post_turn_commit` shape. The agent
creates a `ModelContextPacket`, passes context trace metadata into the React
loop state, selects only bounded capability schemas from the currently
available tools, and records a scoped raw event plus task summary into the
memory layer when memory is enabled. Mature memory retrieval/consolidation and
Phase 09 full test/eval/trace closure remain open.

## Execution Rules

- [ ] Run the phase gate before editing phase files or runtime code.
- [ ] Keep one active phase at a time unless independent read-only audits are
  explicitly requested.
- [ ] Write failing tests before implementation changes.
- [ ] Commit after each verified phase.
- [ ] Push only after required verification passes.

## Phase Dependencies

```text
00
  -> 01 -> 02 -> 03 -> 04
  -> 05 -> 06 -> 07 -> 08 -> 09
```

Phase 01 absorbed the archived `official-graphrag-cleanup-v1` 11C evidence.
Phase 09 owns final tests/eval/trace closure. Phases 05-08 replace the
archived `context-memory-agent-runtime-v1` candidate path.

## Required Global Verifiers

```powershell
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
git diff --check
```

Phase 09 adds full `pytest -q` and formal Eval baseline comparison.

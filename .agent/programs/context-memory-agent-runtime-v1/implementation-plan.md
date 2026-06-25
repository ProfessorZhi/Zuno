# Context Memory Agent Runtime V1 Implementation Plan

## Program Goal

Status: Candidate / Design-ready, not active Current implementation.

Implement the ideal architecture as a sequence of bounded changes:

```text
single GeneralAgent
  -> Context Orchestrator
  -> Memory & State Engine
  -> dynamic capability selection
  -> GraphRAGProjectSnapshot query boundary
  -> context/memory eval proof
```

## Current State

- Zuno is still a Python monorepo with FastAPI, LangGraph, retrieval services,
  GraphRAG services, frontend apps, and tests.
- The current executable program remains
  `.agent/programs/official-graphrag-cleanup-v1/`.
- Phase 11A and Phase 11B are complete in that cleanup program.
- Phase 11C active dependency removal and Phase 12 closure are still the
  dependency gate for implementation work in this program unless dependencies
  are explicitly re-verified.
- Existing memory-related runtime exists under `src/backend/zuno/services/memory/`,
  but the ideal Context Orchestrator and post-turn pipeline are not yet proven
  as the central runtime contract.

## Target State

The target state is:

- one `GeneralAgent` conversation loop
- a typed `AgentExecutionContext`
- a typed `ModelContextPacket`
- a `TokenBudgetPolicy`
- a `ContextTrace`
- append-only raw event logging
- checkpoint-backed short-term state
- source-linked task summaries
- scoped long-term memory stores
- dynamic tool/skill/memory/evidence selection
- a `GraphRAGProjectSnapshot` passed into GraphRAG query execution
- evals for recall, false memory rate, summary faithfulness, token cost,
  cross-session consistency, privacy deletion, and tool-result compression

The existing `GraphRAGProjectSnapshot` and `GraphRAGQueryService` from the
cleanup program must be reused. This program must not implement a second
snapshot or query service.

## Non-Goals

This program does not implement:

- Java business services
- microservice extraction
- event-driven workers
- default multi-agent mode
- a second GraphRAG runtime
- a long-term Domain Pack shim

## Phase Overview

| Phase | Title | Dependency | Main Output |
| --- | --- | --- | --- |
| 00 | Dependency Gate And Design Alignment | none | proof that current GraphRAG cleanup state allows this program to begin |
| 01 | Context Contract Foundation | 00 | `AgentExecutionContext`, `ModelContextPacket`, budget policy, trace contract |
| 02 | Short-term State And Raw Event Log | 01 | thread/session ids, append-only events, checkpoint persistence |
| 03 | Compaction And Task Memory | 02 | source-linked structured summaries and artifact refs |
| 04 | Long-term Memory Stores | 03 | semantic/episodic/procedural stores with scope and governance |
| 05 | Dynamic Context And Capability Selection | 01-04 | selected memories, skills, tool schemas, and evidence packets |
| 06 | GraphRAG Snapshot Query Boundary | 05 | `GraphRAGProjectSnapshot` as immutable query input |
| 07 | GeneralAgent Runtime Integration | 02-06 | one Agent loop with capability calls and post-turn pipeline |
| 08 | Context Memory Eval Closure | 07 | eval suite and trace proof for context/memory behavior |

## Dependency Rules

- Phase 00 must run before implementation edits.
- Phase 01 must define contracts before persistence or compaction phases.
- Phase 02 must protect raw events before Phase 03 summary compaction.
- Phase 03 must keep source event pointers; summaries are derived views.
- Phase 04 must include scope, confidence, dedupe, TTL, and privacy rules.
- Phase 05 must not inject every tool, skill, memory, or evidence item.
- Phase 06 must keep Agent Context, GraphRAG Project Snapshot, and Knowledge
  Evidence separate.
- Phase 07 must not preserve parallel conversational runtimes.
- Phase 08 must verify behavior with eval evidence, not only unit tests.

## Completion Gate

The program is complete only when:

- the runtime has one front-path Agent loop
- context assembly is typed and traced
- raw events remain the source of truth
- summaries and memories can be traced back to source events
- GraphRAG queries receive a project snapshot rather than mutable Agent context
- evals prove recall, faithfulness, memory safety, token cost, and tool-result
  compression behavior

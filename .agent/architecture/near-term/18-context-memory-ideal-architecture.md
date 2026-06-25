# Context Memory Ideal Architecture

## Purpose

Document the ideal architecture from the local design source:

- `C:\Users\Administrator\Downloads\zuno_ideal_architecture_with_context_memory.html`

This is Agent-side target design. It does not claim current runtime behavior.
It refines the near-term Python/FastAPI/LangGraph target by separating Agent
context, durable memory, external knowledge, and GraphRAG project execution.

## Core Decision

All user messages enter one `GeneralAgent`.

RAG, GraphRAG, APIs, CLI tools, MCP connectors, and skills are capabilities the
Agent can call or load. They are not separate conversational agents and they
must not create parallel chat runtimes.

Before each model call, a Context Orchestrator decides what enters the model
window. After each turn, a Post-turn Pipeline persists raw events, updates
state, extracts memory candidates, and records trace evidence.

## Target Runtime Shape

```text
Vue Web / Electron
  -> FastAPI Typed API
  -> Application Services
  -> GeneralAgent
       -> Context Orchestrator
       -> Memory & State Engine
       -> LLM Provider Adapter
       -> Dynamic Capability Selector
       -> Knowledge Capability
       -> Action Tools
       -> MCP Connector
       -> Skills
  -> Post-turn Pipeline
  -> PostgreSQL / Vector Index / Redis / MinIO or files
```

## Layered Context System

The product language may call memory "short, medium, and long." The architecture
must use stricter boundaries because each layer has a different lifecycle,
writer, retention rule, and permission rule.

| Layer | Meaning | Lifecycle |
| --- | --- | --- |
| L0 Working Context | The exact content visible to one model call: system instructions, current task, recent messages, selected memories, retrieval evidence, and tool results. | transient, token-budgeted |
| L1 Short-term Memory | Current thread's recent messages, graph state, current plan, incomplete tool-call group, and scratchpad. | thread/checkpointer |
| L2 Task Memory | Compacted session/task state: goal, decisions, constraints, TODOs, artifact pointers, unresolved questions, and summary checkpoints. | task/session resumable |
| L3 Long-term Memory | Cross-session semantic, episodic, and procedural memory scoped to user, agent, project, or thread. | durable, retrievable |
| L4 External Knowledge | RAG, GraphRAG, files, and web evidence. It is domain knowledge, not Agent memory. | on-demand evidence |
| Source of Truth | Append-only raw event log of messages, model outputs, tool calls/results, interrupts, and memory updates. | durable audit trail |

## Pre-call Context Orchestration

```text
ContextOrchestrator.prepare(step)
  1. Load pinned instructions
  2. Load thread checkpoint
  3. Keep recent coherent message window
  4. Load latest task summary
  5. Retrieve relevant long-term memories
  6. Add current knowledge/tool evidence
  7. Select relevant tool schemas + skills
  8. Allocate token budget
  9. Compact / trim low-priority items
 10. Build ModelContextPacket
 11. Emit context trace
```

## Post-turn Pipeline

```text
PostTurnPipeline.commit(turn)
  1. Append raw events
  2. Save LangGraph checkpoint
  3. Update task state
  4. Extract memory candidates
  5. Deduplicate / resolve conflicts
  6. Promote approved memories
  7. Trigger compaction if threshold reached
  8. Save summary with source_event_ids
  9. Record cost / latency / selection trace
```

## Compaction Rules

| Mechanism | Rule | Must Protect |
| --- | --- | --- |
| Recent Window | Keep recent coherent interactions by token budget and complete interaction groups, not by blind message count. | system instructions, latest user question, incomplete tool call/result |
| Structured Summary | Compress older continuous messages into goals, facts, decisions, constraints, TODOs, artifact refs, and open questions. | source event/message ids; raw messages are not deleted |
| Tool Result Compression | Store large tool results as artifacts and inject summaries, key fields, and references. | errors, permission results, paths, hashes, evidence pointers |
| Selective Retrieval | Retrieve old events, memories, and knowledge only when relevant to the current task. | scope, permission, time, confidence, source |
| Priority Eviction | Remove low-priority context before critical constraints when budget is tight. | explicit user constraints, key decisions, safety rules |

## Capability Boundaries

| Capability | Answers | Notes |
| --- | --- | --- |
| Knowledge | What does Zuno know? | RAG, GraphRAG, and search; usually read-only; returns evidence and citations. |
| Action Tools | What can Zuno do? | Local functions, CLI, HTTP API, browser, and file actions; may have side effects and need audit. |
| MCP Connector | How do external tools/resources/prompts connect? | Protocol adapter; not a business capability by itself. |
| Skills | How should the Agent work? | Guidance package with instructions, workflow, rules, and examples; loaded on demand. |

The Agent should not load every capability on every turn. A Capability Registry
records names, descriptions, types, permissions, costs, schemas, and health.
A Dynamic Capability Selector injects only the relevant tool schemas, MCP tools,
skills, memories, and knowledge evidence.

## GraphRAG Boundary

Do not create two GraphRAG concepts called "runtime context."

Use:

```text
Agent Context
= what the model sees for this call

GraphRAGProjectSnapshot
= the immutable project configuration and index assets used by one knowledge query

Knowledge Evidence
= the query result returned to the Agent
```

`GraphRAGProjectSnapshot` is an input to `GraphRAGQueryService.query(...)`, not
a sibling runtime beside the Agent context.

Snapshot fields:

| Field | Meaning |
| --- | --- |
| `project_id` | Project and permission boundary. |
| `settings.yaml` | Project-level indexing, model, chunking, entity, community, and query configuration truth. |
| `prompts` | Extract, summarize, community, local, global, and drift prompt templates. |
| `versions` | Reproducibility and update/full-rebuild decisions. |
| `readiness` | Graph, community, and report readiness for method availability and fallback. |

## Migration Direction

The implementation direction is captured in:

- `.agent/programs/context-memory-agent-runtime-v1/`

That program should run after the current `official-graphrag-cleanup-v1` runtime
legacy-deletion dependency is satisfied, or explicitly document any earlier
phase that is read-only/design-only.

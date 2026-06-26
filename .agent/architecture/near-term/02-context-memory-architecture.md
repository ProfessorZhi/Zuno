# Context Memory Architecture

## Purpose

Define the canonical target for context, state, and memory. This replaces the
old context-state-memory and context-memory ideal fragments.

## Core Rule

Memory is not "whatever text we put back into the prompt." Zuno separates:

```text
Agent Context
= model-visible input for one call

Raw Event Log
= append-only source of truth

Task Summary Memory
= compressed task/session state with source_event_ids

Structured Long-term Memory
= extracted durable facts/preferences/procedures with source_event_ids

External Knowledge
= RAG/GraphRAG/file/web evidence, not Agent memory
```

## Layer Model

| Layer | Name | Meaning | Current Status |
| --- | --- | --- | --- |
| L0 | Working Context | Exact content visible to one model call. | Minimal foundation current. |
| L1 | Recent Interaction Window | Recent coherent messages and incomplete tool groups. | Target policy; basic windowing current through ContextOrchestrator. |
| L2 | Task Summary Memory | Compressed session/task state: goals, constraints, decisions, TODOs, artifact refs, open questions. | Foundation current, mature extraction target. |
| L3 | Structured Long-term Memory | Cross-session semantic, episodic, and procedural memory scoped by user/agent/project/thread. | Target. |
| L4 | External Knowledge | RAG, GraphRAG, files, and web evidence. | Current query runtime exists; not Agent memory. |
| Source | Raw Event Log | Append-only messages, model outputs, tool calls/results, interrupts, memory updates. | Foundation current; mature use target. |

## Main Memory Strategy

The target memory strategy is:

```text
Summary Compression + Structured Extraction
```

Summary Compression keeps older conversational material usable by compressing
continuous events into task summaries. Structured Extraction turns durable
facts, preferences, decisions, and procedures into typed memory candidates.

Sliding Window still exists, but only as L1 recent-window and token-budget
protection. It is not the main memory strategy.

Importance Filtering may support retention or selection policy, but it is not
the main memory strategy.

Prompt Caching is a compute-layer hint. It can reduce provider cost or latency,
but it is not memory compression and does not replace summary or structured
memory.

## Invariants

- Summary cannot replace the Raw Event Log.
- Task Summary Memory must store `source_event_ids`.
- Structured Long-term Memory must store `source_event_ids`.
- Memory promotion must preserve scope: user, agent, project, thread, and
  permission boundary.
- External Knowledge is not Agent Memory.
- Knowledge evidence may enter L0 Working Context for one turn, but it remains
  evidence with citations and trace, not durable memory.
- Tool result compression must preserve errors, permission results, paths,
  hashes, artifact refs, and evidence pointers.

## Pre-call Context Preparation

```text
ContextOrchestrator.prepare(step)
  1. Load pinned instructions
  2. Load thread checkpoint
  3. Keep recent coherent message window
  4. Protect incomplete tool call/result groups
  5. Load latest task summary
  6. Retrieve relevant structured memories
  7. Add current knowledge/tool evidence
  8. Select relevant ToolCards / skills / MCP tools
  9. Allocate token budget
 10. Evict low-priority context before hard constraints
 11. Build ModelContextPacket
 12. Emit ContextTrace
```

The current minimal `ContextOrchestrator` is a foundation slice. Mature
retrieval, summarization, conflict resolution, and memory promotion are Target.

## Post-turn Pipeline

```text
PostTurnPipeline.commit(turn)
  1. Append raw events
  2. Save LangGraph checkpoint
  3. Update task state
  4. Extract memory candidates
  5. Deduplicate and resolve conflicts
  6. Promote approved memories
  7. Trigger compaction when thresholds are crossed
  8. Save summaries with source_event_ids
  9. Record latency, cost, context trace, and capability trace
```

The full Post-turn Pipeline remains Target until implemented and verified.

## Context Selection

Context selection must protect:

- system and developer instructions
- latest user query
- explicit user constraints
- complete tool call/result groups
- unresolved task decisions
- high-confidence relevant structured memory
- current knowledge evidence needed for citations

Low-priority older messages, redundant summaries, stale tool results, and
irrelevant memories are evicted first.

## Boundary With GraphRAG

Use three names consistently:

```text
Agent Context
= what the model sees for this call

GraphRAGProjectSnapshot
= immutable project/index/config snapshot used by one knowledge query

Knowledge Evidence
= query result returned to the Agent with citations and trace
```

`GraphRAGProjectSnapshot` is not inserted wholesale into Agent Context. It is an
input to `GraphRAGQueryService.query(...)`. The Agent receives selected
Knowledge Evidence, not internal project configuration.

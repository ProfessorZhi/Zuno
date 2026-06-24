# Context State Memory

## Purpose

Separate context, durable state, and transient graph state.

## Current Evidence

- `DomainQAGraph` carries runtime settings, domain pack, retrieval plan,
  evidence bundle, trace metadata, cost metadata, and failure metadata.
- `KnowledgeService.get_runtime_settings()` returns knowledge config, model
  configs, and current Domain Pack state.
- `src/backend/zuno/services/memory/` exists for memory-related behavior.

## Target Context Types

| Context | Lifecycle | Owner | Persisted | Trace |
| --- | --- | --- | --- | --- |
| Request Context | one request | API/service | no | request id, user id |
| Runtime Context | one request | service | no | selected config |
| Graph State | one graph run | LangGraph | no | yes |
| Conversation State | session/dialog | service/database | yes | summary/id |
| Knowledge Context | query | retrieval | derived | evidence ids |
| GraphRAG Project Context | project/index | GraphRAG | yes | id/version |
| Evidence Context | answer run | retrieval/graph | derived | citations |
| Tool Context | tool call | adapter | maybe | tool call id |
| Persistence State | durable | database/storage | yes | ids/version |
| Trace Context | cross-cutting | all layers | yes/logged | yes |

## Non-Responsibilities

Do not put credentials, raw database sessions, or frontend display state in
Graph State. Do not store transient retrieval artifacts as durable truth unless
they are intentionally part of trace/eval output.

## Migration Notes

Replace Domain Pack context with GraphRAG Project context in target contracts.
Keep migration fields only where needed to read existing data safely.

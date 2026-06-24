# Context State Memory

## Purpose

Separate context types so state does not drift across layers.

## Current Evidence

- `src/backend/zuno/core/graphs/states.py` defines graph state shapes.
- `DomainQAGraph` uses runtime settings, domain pack, retrieval plan, evidence,
  trace, cost, and failure metadata.
- `KnowledgeService.get_runtime_settings()` returns knowledge config, model
  configs, domain pack, and runtime settings.
- `src/backend/zuno/services/memory/` contains memory services and vector store
  adapters.

## Context Types

| Context | Lifecycle | Layer | Persisted | Trace |
| --- | --- | --- | --- | --- |
| Request Context | one request | API/service | no | request id, user id |
| Graph State | one graph run | LangGraph | no by default | yes |
| Conversation State | dialog/session | service/database | yes | summary only |
| Knowledge Context | query/session | retrieval | no, derived | yes |
| GraphRAG Project Context | project/index version | GraphRAG | yes | id/version |
| Evidence Context | answer run | retrieval/graph | derived | citations |
| Tool Context | tool call | adapter | maybe | tool call id |
| Java Business Context | business call | service/tool | Java-owned | trace id |
| Persistence State | durable | database/storage | yes | ids/version |
| Trace Context | cross-cutting | all layers | yes/logged | yes |

## Non-Responsibilities

Graph state should not store raw credentials, long-lived provider clients, or
business-transaction truth. Frontend state should not carry internal graph
planner fields.

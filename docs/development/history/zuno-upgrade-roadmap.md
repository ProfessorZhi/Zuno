# Zuno Upgrade Roadmap

## Goal

Strengthen the project around a single-agent architecture that can be defended in interviews and extended in production:

- PostgreSQL as the primary transactional database
- Redis for cache and short-lived runtime state
- RabbitMQ for asynchronous knowledge-processing tasks
- LangSmith for tracing and evaluation
- Dual retrieval modes: standard RAG and GraphRAG

## Guiding Principle

Do not add keywords in isolation. Every new component must sit in a clear chain:

- business role
- data boundary
- runtime boundary
- observable execution path

## Recommended Build Order

1. PostgreSQL migration
2. LangSmith tracing
3. Knowledge pipeline abstraction
4. RabbitMQ-backed async processing
5. Minimal GraphRAG
6. Frontend retrieval mode selection

## Architecture Decisions

### Data Responsibilities

- PostgreSQL:
  - users
  - sessions
  - messages
  - knowledge metadata
  - task records
  - execution logs
- Redis:
  - login/session cache
  - transient execution progress
  - idempotency keys
  - rate-limit or short-lived coordination keys
- RabbitMQ:
  - document processing jobs
  - indexing jobs
  - graph extraction jobs
  - retryable background tasks

### Retrieval Responsibilities

Each knowledge base should support two index families:

- standard RAG index
- GraphRAG index

Frontend retrieval mode should expose:

- `rag`
- `graphrag`
- `hybrid`
- `auto`

`auto` should be handled by retrieval orchestration, not by letting the agent freely guess after two raw result sets are returned.

## Iteration Plan

### Iteration 1: PostgreSQL + LangSmith

Deliverables:

- replace MySQL-specific configuration with generic database config
- migrate to PostgreSQL driver stack
- introduce Alembic
- wire LangSmith environment-based tracing
- attach metadata: `user_id`, `session_id`, `knowledge_id`, `trace_id`, `retrieval_mode`

Acceptance:

- app boots on PostgreSQL
- core CRUD paths pass
- LangSmith can show at least one complete agent run

### Iteration 2: Knowledge Pipeline + RabbitMQ

Deliverables:

- formalize pipeline stages:
  - upload
  - parse
  - split
  - rag indexing
  - graph extraction
  - graphrag indexing
  - status writeback
- add task table and task status transitions
- add producer/consumer boundary for background processing

Acceptance:

- knowledge ingestion can run asynchronously
- failures are visible and retryable
- frontend can poll or subscribe to progress

### Iteration 3: Minimal GraphRAG

Deliverables:

- extract entities and relations from chunks
- persist graph structure
- retrieve subgraph context for relation-heavy questions
- merge GraphRAG context with standard RAG context in `hybrid` mode

Acceptance:

- at least one example where GraphRAG improves over standard RAG
- retrieval mode is selectable from frontend

## Open Product Decisions

These should be decided before implementation starts:

1. Graph storage choice:
   - PostgreSQL tables first
   - or external graph DB later
2. Async UX:
   - polling first
   - SSE progress later
3. Retrieval product shape:
   - per-knowledge-base default mode
   - plus per-query override in workspace

## What To Avoid

- do not add RabbitMQ before the async task chain exists
- do not claim GraphRAG before graph build and graph retrieval both exist
- do not let the agent choose retrieval blindly without orchestration and evaluation
- do not keep MySQL-specific prompts once PostgreSQL becomes the main path

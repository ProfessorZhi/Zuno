# Zuno Platform Upgrade Design

## Goal

Upgrade Zuno's core platform around a defendable, production-shaped single-agent architecture:

- PostgreSQL for transactional truth
- Redis for short-lived state
- RabbitMQ for async pipeline execution
- Neo4j for GraphRAG graph storage and graph retrieval
- LangSmith for end-to-end observability
- one knowledge base supporting `rag`, `graphrag`, `hybrid`, and `auto`

## Scope

This design covers five implementation tracks:

1. PostgreSQL migration
2. Redis and LangSmith foundation
3. Knowledge pipeline state model
4. RabbitMQ pipeline execution
5. Neo4j GraphRAG and dual retrieval

Multi-agent behavior is explicitly out of scope. The target is a stronger single-agent platform.

## Future Optimization Targets

The first delivery focus remains single-agent depth, but the platform should leave room for future upgrades:

- subagent orchestration for bounded parallel research or execution
- task decomposition only after the single-agent path, observability, and retrieval quality are stable
- explicit governance so subagents remain auditable through trace, task, and result aggregation

## Core Principles

### Responsibility Boundaries

- PostgreSQL stores business truth
- Redis stores transient or performance-oriented state
- RabbitMQ moves work between stages
- Neo4j stores graph entities, relationships, and graph-to-chunk references
- LangSmith observes online and offline execution

### Evolution Strategy

The system will not jump directly to a full GraphRAG-first platform. The first version of GraphRAG must be:

- real
- queryable
- testable
- observable

Then it can be expanded later into the dominant retrieval path.

### Delivery Strategy

Implementation happens in five gated rounds:

1. PostgreSQL
2. Redis + LangSmith
3. Knowledge pipeline
4. RabbitMQ
5. Neo4j + GraphRAG

Each round must pass engineering verification, business verification, and evidence verification before the next round begins.

## Runtime Architecture

### Online Query Path

`FastAPI -> retrieval orchestrator -> RAG/GraphRAG/hybrid routing -> agent -> SSE response`

### Offline Knowledge Processing Path

`upload -> task record -> async pipeline -> parse -> split -> rag index -> graph extract -> graph index -> status writeback`

## Product Surface

### Knowledge Base

Each knowledge base has:

- identity and description
- file set
- default retrieval mode
- indexing status summary

### Knowledge File

Each knowledge file exposes:

- upload state
- parse state
- RAG index state
- GraphRAG index state
- latest task id
- latest error

### Workspace Query Mode

Workspace requests support:

- `default`
- `rag`
- `graphrag`
- `hybrid`
- `auto`

`default` follows the knowledge base default. `auto` is conservative in the first version.

## Retrieval Model

### `rag`

Use query rewrite, vector or hybrid retrieval, rerank, and chunk-context answering.

### `graphrag`

Use entity recognition, graph lookup, limited hop expansion, graph-context assembly, and answer grounding back to chunk evidence when possible.

### `hybrid`

Run standard RAG and GraphRAG in parallel, normalize result structures, fuse, then answer.

### `auto`

Use a lightweight routing layer:

- relation-heavy questions prefer GraphRAG
- direct evidence questions prefer standard RAG
- ambiguous questions fall back to hybrid

## Task Model

The knowledge pipeline revolves around one task model:

- one uploaded file creates one top-level task
- a task moves through named stages
- task truth lives in PostgreSQL
- task live progress is mirrored to Redis
- pipeline workers exchange work through RabbitMQ

## GraphRAG Model

The first version of GraphRAG uses Neo4j for:

- entity nodes
- chunk nodes
- optional document nodes
- entity-to-entity relationships
- chunk-to-entity mention edges
- document-to-chunk ownership edges

The first version supports:

- entity hit lookup
- 1-hop and 2-hop expansion
- path-based relation context assembly
- graph-to-chunk grounding

It does not include:

- advanced graph algorithms
- community detection
- graph embeddings as the main ranking path
- large-scale global graph summarization

## Observability

LangSmith must trace:

- workspace request entry
- retrieval orchestration
- tool calls
- rerank
- agent execution
- pipeline task execution
- graph extraction and graph lookup

Required metadata:

- `trace_id`
- `user_id`
- `session_id`
- `knowledge_id`
- `file_id`
- `task_id`
- `retrieval_mode`
- `actual_retrieval_strategy`

## Validation Standard

Every implementation round must satisfy all three:

### Engineering Verification

- services boot
- APIs respond
- migrations work
- tests pass

### Business Verification

- a real user flow completes

### Evidence Verification

- logs
- database state
- LangSmith traces
- queue state or graph state when relevant

## Deliverables

This master design is implemented through five subsystem specs:

- PostgreSQL design
- Redis and LangSmith design
- knowledge pipeline design
- RabbitMQ integration design
- Neo4j GraphRAG design

# Zuno Knowledge Pipeline Design

## Goal

Convert knowledge ingestion from an opaque synchronous flow into a named, staged, stateful pipeline that supports observability, retries, async execution, and later GraphRAG expansion.

## Scope

This spec defines:

- pipeline stages
- task records
- task events
- file status behavior
- stage transitions
- retry boundaries

## Non-Goals

This spec does not define:

- RabbitMQ queue wiring
- Neo4j schema
- retrieval orchestration behavior

## Pipeline Stages

The first version uses these stages:

- `uploaded`
- `queued`
- `parsing`
- `splitting`
- `rag_indexing`
- `graph_extracting`
- `graph_indexing`
- `completed`
- `failed`

## Task Model

One uploaded knowledge file creates one top-level task.

That task has:

- a global status
- a current stage
- retry metadata
- event history
- summary fields for latest outcome

## Status Model

### Global Status

- `pending`
- `running`
- `success`
- `failed`
- `cancelled`

### Current Stage

One of the pipeline stages listed above.

This split is deliberate:

- global status answers "did the task succeed?"
- current stage answers "where is it now?"

## Core Tables

### `knowledge_task`

Purpose:

- canonical task record

Key fields:

- `id`
- `knowledge_id`
- `knowledge_file_id`
- `task_type`
- `status`
- `current_stage`
- `retry_count`
- `error_message`
- `payload`
- `result_summary`
- `started_at`
- `finished_at`

### `knowledge_task_event`

Purpose:

- append-only event log

Key fields:

- `id`
- `task_id`
- `stage`
- `status`
- `message`
- `detail`
- `created_at`

## File Status Model

Knowledge file records should expose stage-specific states:

- parse status
- RAG index status
- graph index status
- latest task id
- latest error

This keeps the file list useful for the user, while the task tables preserve operational truth.

## Stage Semantics

### `parsing`

- raw file to normalized content

### `splitting`

- normalized content to chunks

### `rag_indexing`

- chunks written to standard retrieval indexes

### `graph_extracting`

- chunks transformed into entity and relation candidates

### `graph_indexing`

- graph candidates written into Neo4j and graph mapping structures

## Failure Rules

Each failure must:

- write a task event
- update the task global status
- update the file latest error
- preserve the failed stage

## Retry Rules

The first version retries at the task level, not arbitrary stage fragments.

Meaning:

- a retry reruns from a defined restart point
- not from an undefined mid-stage snapshot

This keeps behavior simpler and easier to explain.

## Acceptance Criteria

- uploading a file creates a task record
- each stage change writes an event
- success updates file state and task state
- failure updates file state and task state
- task history can be queried through an API

## Risks

- mixing file status and task status can produce contradictions if ownership is unclear
- unclear restart rules make retries dangerous
- stage names that are too implementation-specific will be hard to evolve

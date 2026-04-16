# Zuno RabbitMQ Integration Design

## Goal

Use RabbitMQ to turn the knowledge pipeline into a real asynchronous execution flow without making RabbitMQ the source of truth for system state.

## Scope

This spec defines:

- queue responsibilities
- producer and consumer boundaries
- message payload rules
- retry and idempotency expectations
- status writeback rules

## Non-Goals

This spec does not define:

- PostgreSQL schema details
- Neo4j graph model
- LangSmith metadata rules

## RabbitMQ Role

RabbitMQ only moves work.

It does not own:

- canonical task state
- file truth
- business truth

Those remain in PostgreSQL.

Redis mirrors live progress. RabbitMQ moves stage execution.

## Queue Design

The first version uses three worker responsibilities:

- `knowledge.parse`
- `knowledge.index`
- `knowledge.graph`

This is intentionally simple.

## Message Flow

1. upload creates `knowledge_task`
2. producer sends parse message
3. parse worker completes and emits index message
4. index worker completes and emits graph message
5. graph worker completes and marks task success

## Message Payload

Messages should contain references, not large business payloads.

Required fields:

- `task_id`
- `knowledge_id`
- `knowledge_file_id`
- `stage`
- `trace_id`
- optional small execution hints

Workers should load canonical state from PostgreSQL.

## Consumer Rules

Every consumer must:

- load task truth from PostgreSQL
- update task stage and task event records
- mirror progress to Redis
- write success or failure back to PostgreSQL
- emit the next stage only after the current stage is committed

## Idempotency

Each stage execution must be safe against duplicate delivery.

The worker should check:

- whether this task already completed this stage
- whether the next stage was already scheduled or completed

Idempotency keys can be backed by Redis, but final truth must remain in PostgreSQL.

## Retry Strategy

The first version should support bounded retries.

Rules:

- retry count is stored in PostgreSQL
- consumers increment retry count on failure
- repeated failure moves the task to `failed`
- manual retry creates a controlled rerun path

Dead-letter infrastructure can be postponed if it slows the first version down, but failure must still be explicit and visible.

## Acceptance Criteria

- upload triggers async processing
- stage progress is visible while workers run
- failures are stored and reviewable
- retries do not corrupt task truth
- duplicate messages do not create duplicate success paths

## Risks

- worker code can accidentally split state ownership across PostgreSQL and Redis
- duplicate delivery can create inconsistent downstream work if idempotency is weak
- oversized payloads make queue debugging harder

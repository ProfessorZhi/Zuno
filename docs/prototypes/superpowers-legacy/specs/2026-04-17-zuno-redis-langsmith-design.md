# Zuno Redis And LangSmith Foundation Design

## Goal

Turn Redis from scattered utility usage into a defined short-lived state layer, and wire LangSmith into the core execution paths so Zuno has real observability rather than isolated logs.

## Scope

This spec covers:

- Redis responsibility boundaries
- Redis key naming
- LangSmith tracing entry points
- metadata standards
- relationship between request trace ids and LangSmith runs

## Non-Goals

This spec does not define:

- RabbitMQ queue topology
- Neo4j graph model
- Graph extraction logic
- PostgreSQL schema migration details

## Redis Role

Redis is not the source of truth. It stores data that is:

- short-lived
- performance-sensitive
- coordination-oriented
- safely reconstructable from PostgreSQL or runtime execution

### Redis Stores

- auth/session cache
- captcha values
- rate-limit counters
- idempotency keys
- streaming progress
- task progress mirrors
- optional hot retrieval cache

### Redis Must Not Store As Truth

- final task records
- final error history
- canonical knowledge metadata
- canonical pipeline state

## Redis Key Convention

Recommended keys:

- `auth:user:{user_id}:token`
- `captcha:{captcha_key}`
- `rate_limit:{scope}:{id}`
- `idempotency:{scene}:{key}`
- `stream:{session_id}:latest`
- `task_progress:{task_id}`
- `retrieval_cache:{knowledge_id}:{query_hash}`

Each key family should define:

- owner path
- TTL
- value shape
- invalidation rule

## LangSmith Role

LangSmith is the system-level execution observability layer.

It must make visible:

- which path the request took
- which tools ran
- which retrieval mode was selected
- which task stage failed
- how graph retrieval contributed to the final answer

## Tracing Entry Points

LangSmith tracing must cover:

- workspace request entry
- simple agent execution
- retrieval orchestration
- rerank
- tool call execution
- knowledge task processing
- graph extraction
- graph retrieval

## Metadata Standard

Every meaningful run should attach:

- `trace_id`
- `user_id`
- `session_id`
- `knowledge_id`
- `file_id`
- `task_id`
- `retrieval_mode`
- `actual_retrieval_strategy`

## Trace Alignment

The existing request `trace_id` should remain the main correlation handle.

Alignment rule:

- request headers and logs use `trace_id`
- LangSmith run metadata includes the same `trace_id`
- pipeline tasks also attach task-scoped metadata

This gives one path from:

- frontend event
- backend log
- LangSmith trace

## Acceptance Criteria

- a complete workspace query appears in LangSmith
- retrieval strategy is visible in trace metadata
- Redis keys follow the new namespaces
- SSE or streaming behavior is not broken by tracing

## Risks

- tracing too many low-level operations can create noisy runs
- inconsistent metadata keys reduce analysis value
- Redis key growth can become unmanageable without TTL rules

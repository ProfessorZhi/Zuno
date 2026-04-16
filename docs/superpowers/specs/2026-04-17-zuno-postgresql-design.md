# Zuno PostgreSQL Migration Design

## Goal

Replace MySQL as Zuno's primary transactional database with PostgreSQL, and establish a clean schema and migration path for later pipeline, observability, and GraphRAG integration work.

## Why PostgreSQL

PostgreSQL is a better fit than MySQL for this project's next stage because it offers:

- stronger JSON support
- better complex query support
- a more flexible extension and metadata story
- a cleaner path for task records and semi-structured operational data

It remains a relational database. The main data model is still tables, rows, columns, keys, and SQL.

## Non-Goals

This spec does not define:

- RabbitMQ queues
- Neo4j graph schema
- GraphRAG retrieval
- LangSmith tracing rules

## Current Problems

The current codebase contains MySQL-specific assumptions:

- settings key named `mysql`
- sync and async URLs using MySQL drivers
- MySQL bootstrap database creation
- MySQL-specific text-to-SQL assumptions
- MySQL-focused prompts

## Target State

### Configuration

Replace `mysql` config with a generic `database` section:

- `sync_endpoint`
- `async_endpoint`
- `echo`
- `pool_size`
- `max_overflow`

Driver target:

- sync: `postgresql+psycopg`
- async: `postgresql+asyncpg`

### Migration System

Introduce Alembic as the canonical schema change mechanism.

Rules:

- startup must not silently reshape schema
- schema changes must be versioned
- development and production paths should use the same migration logic

### Data Ownership

PostgreSQL stores:

- users
- roles
- dialogs
- messages
- workspace sessions
- knowledge bases
- knowledge files
- task records
- task events
- execution logs and later metadata references

### Backward Compatibility Policy

This is a primary-path migration, not a long-term dual-database strategy.

Meaning:

- we may support a one-time migration path
- we should not maintain MySQL and PostgreSQL as equal first-class paths forever

## Schema Direction

The existing tables remain, but later iterations must be able to add:

- `knowledge_task`
- `knowledge_task_event`
- retrieval mode fields on knowledge bases
- GraphRAG readiness fields on knowledge files

## Required Refactors

### Database Module

Refactor database initialization so it no longer encodes MySQL assumptions in names or bootstrap logic.

### DAO and Model Review

Review SQLModel fields for PostgreSQL compatibility, especially:

- JSON columns
- text defaults
- timestamp defaults
- unique constraints

### MySQL-Specific Cleanup

Clean or isolate:

- MySQL bootstrap database creation
- MySQL-specific text-to-SQL agent logic
- prompts or docs that explicitly claim MySQL

## Acceptance Criteria

- app boots on PostgreSQL
- migrations can create all required core tables
- login, session, message, and knowledge CRUD work
- no required runtime path depends on MySQL drivers

## Risks

- SQLModel or SQLAlchemy column defaults may behave differently
- async driver behavior may differ from current assumptions
- startup initialization code may rely on MySQL bootstrap behavior

## Design Choice

Choose clear cutover over permanent dual support.

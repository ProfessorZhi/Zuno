# Persistence Database Storage

## Purpose

Define near-term storage responsibilities.

## Current Evidence

- `src/backend/zuno/database/__init__.py` creates SQLModel/SQLAlchemy engines
  from PostgreSQL config.
- `database/models/knowledge.py` stores `default_retrieval_mode` and JSON
  `knowledge_config`.
- `database/models/knowledge_file.py` stores parse, RAG index, graph index,
  task, and error status fields.
- `services/rag/vector_db/` contains vector backends.
- `services/graphrag/client.py` stores Neo4j entities, relations, communities,
  `domain_pack_id`, `index_version`, `document_hash`, and `chunk_hash`.
- Config files include PostgreSQL, Neo4j, and storage settings.

## Target Design

```text
PostgreSQL:
  users, agents, dialogs, messages, knowledge, files, tasks, configs, versions

Vector Store:
  chunks, text embeddings, image embeddings, modality indexes

Graph Store:
  entities, relationships, graph paths, communities, community reports

Object/File Storage:
  original files, parsed output, exported reports, index artifacts

Cache:
  optional LLM result cache, retrieval cache, prompt tuning cache, job cache
```

## Target GraphRAG Fields

```text
graphrag_project_id
prompt_version
index_version
query_method
query_prompt_version
document_hash
chunk_hash
status
community_version
```

## Retired Field Direction

`domain_pack_id` is current evidence, but it is not the future primary
GraphRAG key. Near-term migration should introduce `graphrag_project_id` before
removing compatibility reads.

## Acceptance Direction

Later implementation should prove index/version fields in config, trace, and
storage agree for a query or reindex run.

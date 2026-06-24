# Persistence Database Storage

## Purpose

Define storage responsibilities and target GraphRAG version fields.

## Current Evidence

- `src/backend/zuno/database/__init__.py` imports SQLModel tables and creates
  sync/async SQLAlchemy engines from PostgreSQL config.
- `src/backend/zuno/database/models/knowledge.py` stores `default_retrieval_mode`
  and JSON `knowledge_config`.
- `src/backend/zuno/database/models/knowledge_file.py` stores parse, RAG index,
  and graph index status fields.
- `src/backend/zuno/services/rag/vector_db/` contains vector store clients.
- `src/backend/zuno/services/graphrag/client.py` stores Neo4j entities,
  relations, `domain_pack_id`, `index_version`, `document_hash`, `chunk_hash`,
  and `GraphCommunity` reports.
- `src/backend/zuno/config.example.yaml` contains PostgreSQL, Neo4j, and storage
  configuration.

## Target Storage Split

```text
PostgreSQL:
  users, agents, dialogs, messages, knowledge, files, tasks, configs, versions

Vector Store:
  chunks, embeddings, modality indexes

Graph Store:
  entities, relationships, communities, graph paths, reports

Object/File Storage:
  original files, parsed output, exported reports, index artifacts

Cache:
  LLM result cache, retrieval cache, prompt tuning cache, temporary job cache
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

## Migration Notes

`domain_pack_id` is a retired target field. It may appear in current evidence
and migration bridges, but it should not be the future primary graph or query
surface.

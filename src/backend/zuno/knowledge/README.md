# Knowledge 层边界

分类：`target-layer`

## 当前角色

`src/backend/zuno/knowledge/` 目前是 Knowledge / GraphRAG / retrieval 的 facade，部分稳定导出直接来自 GraphRAG contract，较重的 retrieval 和 query service 通过 lazy import 暴露。当前已提供 `contracts.py`、`agentic_graphrag.py`、`query_service.py`、`evidence.py`、`citation.py`、`trace.py`、`retrieval/`、`fusion/`、`graphrag/`、`ingestion/` 和 `indexing/` import guard。`GraphRAGExtractorConfig` 当前是 extractor config contract，不是生产级 LLM 抽取执行器；`agentic_graphrag.py` 当前已提供 Agentic Retrieval Router、Evidence / Citation、GraphRAG index pipeline contract、local evidence provenance、citation source tracing、local RRF/rerank trace、deterministic graph extraction / community report trace 和 unsupported claim metrics。`knowledge/indexing/` 当前是 PHASE05 本地 index job runtime surface，不是生产级 Elasticsearch / Milvus / Neo4j。真实查询、GraphRAG、retrieval、RAG、convert_files 和 pipeline 实现仍在 `src/backend/zuno/platform/services/application/knowledge.py`、`platform/services/graphrag/`、`platform/services/retrieval/`、`platform/services/rag/`、`platform/services/convert_files/` 和 `platform/services/pipeline/`。

## Target role

目标状态下，Knowledge 层负责 KnowledgeQueryService、GraphRAGQueryService、retrieval planning、fusion、citation 和 evidence trace。GraphRAG 是被选择的 Knowledge Capability，不是第二套聊天 runtime。

`knowledge/ingestion/` 是 Document Ingestion / Parse Gateway 的目标 owner，当前只证明边界存在，不证明 parser runtime 已经迁移。

## 允许新增内容

- 查询 contract、retrieval model、trace model、轻量 settings validator 或 lazy facade。
- 帮助区分 basic / local / global / drift 查询边界的文档。
- Agentic Retrieval Router、EvidenceBundle、Citation Builder、unsupported claim check、GraphRAG index pipeline contract、local RRF/rerank trace、deterministic graph extraction / community report trace 和 source-provenance evidence payload。
- 本地 deterministic knowledge indexing runtime surface、manifest 和 focused tests。
- 不 eager load DB、vector runtime、API service 或 provider client 的 re-export。

## 禁止事项

- 禁止直接迁移 GraphRAG、retrieval、RAG、vector DB 或 query method 行为。
- 禁止破坏 `zuno.services.graphrag.*`、`zuno.services.retrieval.*`、`zuno.services.rag.*` 和 application knowledge 旧 import path。
- 禁止把本地 deterministic RRF/rerank trace 写成生产 reranker 服务；禁止把本地 deterministic graph extraction / community report trace 写成生产级 LLM GraphRAG extraction、真实 community report pipeline 或外部图索引服务。

## Focused tests

- `tests/repo/test_backend_facade_layers.py`
- `tests/agent/test_knowledge_layer_surfaces.py`
- `tests/agent/test_knowledge_graphrag_runtime_contracts.py`
- `tests/api/test_knowledge_api_contract.py`
- `tests/graphrag/**`
- `tests/retrieval/**`
- `tests/agent/test_general_agent_project_query_runtime.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/repo/test_static_target_layer_imports.py`

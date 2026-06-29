# PHASE04 Knowledge 层 Foundation Surfaces

状态：completed

## 目标

让 `src/backend/zuno/knowledge/` 拥有 query service、contracts、evidence、citation、trace、retrieval、fusion 和 graphrag 的薄入口，同时避免 import 时加载 DB、vector runtime、API service 或 provider client。

## 完成内容

- `contracts.py`：KnowledgeQuery、KnowledgeQueryResult、GraphRAGProjectSnapshot 等 contract 入口。
- `query_service.py`：KnowledgeQueryService 和 GraphRAGQueryService lazy 入口。
- `evidence.py`：Evidence / citation 相关 contract 入口。
- `citation.py`：citation formatter / model 入口。
- `trace.py`：query trace 入口。
- `retrieval/`：retrieval planner / orchestrator / mode contract 入口。
- `fusion/`：fusion contract 入口。
- `graphrag/`：GraphRAG project / query service contract 入口。

## 边界

本 phase 不改 GraphRAG、retrieval、RAG、vector DB 或 query method 行为；不把 Native BM25、RRF、完整 evidence fusion 或生产级 GraphRAG 能力写成 Current。

## 验证

```powershell
pytest -q tests/agent/test_knowledge_layer_surfaces.py -p no:cacheprovider
```

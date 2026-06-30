# Knowledge Indexing 边界

PHASE05 status: runtime-current-production-target

## 当前角色

`knowledge/indexing/` 是 PHASE05 的 index job 与 knowledge space runtime owner。当前实现是本地 deterministic runtime surface：

- `KnowledgeSpaceManifest`：记录 workspace、knowledge space、graph project 和 index version。
- `IndexJobManifest`：记录 document source、targets、target status、retry、error、source block ids 和 graph project reference。
- `KnowledgeIndexRuntime`：把 `CanonicalDocumentIR` 送入 BM25 / vector / graph 三类本地 index，并提供 query、job replay、failure retry 和 retrieval payload。

## Target 边界

当前不是生产级 Elasticsearch / Milvus / Neo4j runtime，也不是 worker queue 或 durable index store。PHASE05 的 Current 是可测试 index job runtime surface；生产持久化和外部引擎接入仍属于后续平台化。

## Focused tests

- `pytest -q tests/knowledge/test_index_jobs_runtime.py -p no:cacheprovider`
- `pytest -q tests/knowledge tests/retrieval tests/graphrag -p no:cacheprovider`

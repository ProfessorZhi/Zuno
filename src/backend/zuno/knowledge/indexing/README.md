# Knowledge Indexing 边界

PHASE05-PHASE06 status: runtime-current-production-target

## 当前角色

`knowledge/indexing/` 是 PHASE05 的 index job 与 knowledge space runtime owner。当前实现是本地 deterministic runtime surface：

- `KnowledgeSpaceManifest`：记录 workspace、knowledge space、graph project 和 index version。
- `IndexJobManifest`：记录 document source、targets、target status、retry、error、source block ids、graph project reference、parse job id、parse attempt id、document version id、source sha256、parser config hash、IR schema version、diagnostics digest、parser diagnostics 和 block/table/figure count。
- `KnowledgeIndexRuntime`：把 `CanonicalDocumentIR` 送入 BM25 / vector / graph 三类本地 index，并提供 query、job replay、failure retry 和 retrieval payload。
- Citation lineage：`index_document(..., parse_job_snapshot=...)` 会把 parse lineage 写入 manifest、source provenance 和 retrieval chunk metadata 的 `citation_lineage`，让 evidence / citation 能回追到 source hash、document version、parse job、parse attempt、source span、block 和 chunk。
- Citation chunk retrieval：本地 retrieval payload 当前返回 citation-sized chunk，并在 metadata 中携带 parent context 与 neighbor chunk refs；parent context 不挤掉 citation span。
- Lexical / phrase candidate metadata：本地 ranking 当前输出 `retriever_source`、`raw_score`、`normalized_score`、`rank`、`matched_terms`、`matched_phrase` 和 `candidate_reason`。Exact / normalized phrase match 会作为 `normalized_phrase` 候选信号参与排序；该路径不读取 eval gold answer 或 gold evidence text。

## Target 边界

当前不是生产级 Elasticsearch / Milvus / Neo4j runtime，也不是 worker queue 或 durable index store。PHASE05-PHASE06 的 Current 是可测试 index job runtime surface 与 local parse lineage handoff；生产持久化和外部引擎接入仍属于后续平台化。

## Focused tests

- `pytest -q tests/knowledge/test_index_jobs_runtime.py -p no:cacheprovider`
- `pytest -q tests/knowledge tests/retrieval tests/graphrag -p no:cacheprovider`

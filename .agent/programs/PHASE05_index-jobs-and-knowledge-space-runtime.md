# PHASE05 index-jobs-and-knowledge-space-runtime

status: completed

## 目标

把 Document IR 真实送入 BM25 / vector / graph 目标 index job，让“上传文档 -> index 完成 -> 可检索”成为稳定运行时。

## 范围

- 实现 knowledge space、ingest job、index job、版本化 manifest、失败重试和回放。
- 固定 BM25、vector、graph 三类索引的最小接口。
- 让 index manifest 与 source document block 可追踪。

## 禁止范围

- 不把 handoff payload 当作 index runtime。
- 不引入完整微服务作为第一版要求。
- 不跳过失败和重试语义。

## 验收闸门

- tests 能从 Document IR 建立可查询 index。
- job manifest 记录 source、version、status、error、retry 和 graph project reference。
- retrieval phase 能消费该 index runtime。

## 完成证据

- `src/backend/zuno/knowledge/indexing/` 新增 PHASE05 runtime owner surface。
- `KnowledgeIndexRuntime` 支持 knowledge space、index job、BM25 / vector / graph 本地 index、query、retrieval payload、job manifest replay 和 failed job retry。
- `IndexJobManifest` 记录 source、index version、targets、target status、error、retry、previous job、graph project reference 和 source block ids。
- `tests/knowledge/test_index_jobs_runtime.py` 证明 Document IR 可建立可查询 index、失败和重试可回放、retrieval payload 可消费。
- `pytest -q tests/knowledge tests/retrieval tests/graphrag -p no:cacheprovider` 通过。

## Current / Target 边界

Current 是本地 deterministic index job runtime surface；不是生产级 Elasticsearch / Milvus / Neo4j，也不是完整 GraphRAG extraction / community report runtime。

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge tests/retrieval tests/graphrag -p no:cacheprovider
```

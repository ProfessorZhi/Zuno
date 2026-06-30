# PHASE05 index-jobs-and-knowledge-space-runtime

status: active

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

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge tests/retrieval tests/graphrag -p no:cacheprovider
```

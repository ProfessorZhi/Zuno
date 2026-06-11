# mixed_realistic_v1

这套数据集用于同时观察三类能力：

1. `标准 RAG / 向量检索`
2. `RAG + BM25` 混合召回
3. `RAG + BM25 + GraphRAG`

## 样本结构

- `keyword_exact`: 精确标识符、header、queue、配置项，主要看 BM25 增益
- `semantic_fact`: 同义表达、概念解释，主要看向量召回
- `cross_doc_summary`: 跨文档整合，主要看融合与排序
- `graph_relation`: 关系链推理，主要看 GraphRAG

当前首版共有 `16` 条样本，每类 `4` 条。

## 建议评测组合

先跑这三组：

- `baseline_rag`
- `rag_rerank_recall_first`
- `rag_graph_chunk_backed`

如果你希望口径更接近产品文案，可以把它们解释为：

- `baseline_rag`: 向量主路径
- `rag_rerank_recall_first`: 向量 + 更宽召回 / 更强排序
- `rag_graph_chunk_backed`: 图谱增强检索

后续如果要更严格地区分 `RAG` 和 `RAG + BM25`，建议单独增加一个显式 profile，把 Elasticsearch 开关与 planner trace 一起写进 metadata。

## 典型执行

```powershell
python src/backend/agentchat/evals/rag_eval/ingest_prepared_corpus.py `
  --manifest src/backend/agentchat/evals/rag_eval/corpus/mixed_realistic_v1/manifest.json `
  --knowledge-name ZunoMixedRealisticV1 `
  --output src/backend/agentchat/evals/rag_eval/runs/mixed_realistic_v1_ingest.json
```

```powershell
python src/backend/agentchat/evals/rag_eval/run_eval.py `
  --dataset src/backend/agentchat/evals/rag_eval/datasets/mixed_realistic_v1_eval.jsonl `
  --knowledge-id <knowledge_id> `
  --profiles baseline_rag,rag_rerank_recall_first,rag_graph_chunk_backed `
  --output-dir src/backend/agentchat/evals/rag_eval/runs/mixed_realistic_v1_first_pass `
  --trace-langsmith
```

## 你应该重点看什么

- `keyword_exact` 上，`BM25` 或混合召回是否优于纯向量
- `semantic_fact` 上，GraphRAG 是否没有明显拖累
- `cross_doc_summary` 上，融合后的 top-k 证据是否更完整
- `graph_relation` 上，GraphRAG 是否明显提升 Recall 和 Answer Correctness

## LangSmith 追踪建议

至少给每个 run 带这些 metadata：

- `dataset_name=mixed_realistic_v1`
- `sample_id`
- `category`
- `profile`
- `retrieval_mode`
- `knowledge_id`

如果 retrieval trace 已开启，再把下面这些一起挂上去：

- `resolved_mode`
- `enabled_retrievers`
- `retriever_runs`
- `rounds`
- `fallback_reason`

这样在 LangSmith 里可以直接筛：

- 哪些 `keyword_exact` 是 BM25 救回来的
- 哪些 `graph_relation` 题没有走出有效路径
- 哪些题是 recall 不足，哪些题是 answer 阶段失真

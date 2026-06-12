# RAG Local Eval Scheme

## Goal

建立一套本地可重复运行的 `RAG vs GraphRAG` 评测方案，并明确：

- 本地 embedding 模型如何接入
- 用哪些 profile 对比
- 至少看哪五个检索指标
- 什么时候认为 GraphRAG 值得保留

## Scope

这套方案优先覆盖：

- 本地运行的文本 embedding 模型
- `baseline_rag`
- `rag_rerank`
- `rag_graph_chunk_backed`
- `rag_graph_chunk_backed_3hop`

第一阶段先不强依赖线上 LLM judge。主线先把检索指标做稳定，再把答案层指标叠加上去。

## Retrieval Metrics

本地 RAG / GraphRAG 对比必须至少看这五项：

1. `Retrieval Recall@K`
2. `Hit Rate@K`
3. `Context Precision@K`
4. `MRR@K`
5. `NDCG@K`

答案层可选补充：

- `Faithfulness`
- `Answer Correctness`
- `Citation Accuracy`

## Test Matrix

### Profile Set: `local_compare`

- `baseline_rag`
- `rag_rerank`
- `rag_graph_chunk_backed`

用途：

- 判断 GraphRAG 是否比纯向量和 rerank 更有收益
- 适合作为第一轮本地 embedding 基准

### Profile Set: `graph_compare`

- `baseline_rag`
- `rag_graph_chunk_backed`
- `rag_graph_chunk_backed_3hop`

用途：

- 判断 3-hop 是否真的提升图关系类问题
- 防止 hop 增加后 recall 上升但 precision 明显下降

## Local Embedding Binding

导入评测知识库时，必须显式绑定本地 embedding 模型：

```powershell
python tools/evals/zuno/rag_eval/ingest_prepared_corpus.py `
  --manifest .local/evals/agentchat/rag_eval/corpus/python_notes/manifest.json `
  --knowledge-name ZunoPythonEval `
  --text-embedding-model-id <local_embedding_llm_id> `
  --output .local/evals/agentchat/rag_eval/runs/ingest-result.json
```

说明：

- `<local_embedding_llm_id>` 应该对应 Zuno 中已注册的 `Embedding` 类型模型
- 该模型应指向本地运行的 embedding 服务
- 如果要同时比较 rerank，可额外传 `--rerank-model-id`

## Evaluation Commands

### First Pass

```powershell
python tools/evals/zuno/rag_eval/run_eval.py `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --knowledge-id <knowledge_id> `
  --profile-set local_compare `
  --output-dir .local/evals/agentchat/rag_eval/runs/<run_id>
```

### Graph Hop Comparison

```powershell
python tools/evals/zuno/rag_eval/run_eval.py `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --knowledge-id <knowledge_id> `
  --profile-set graph_compare `
  --output-dir .local/evals/agentchat/rag_eval/runs/<run_id>
```

### Optional Answer-Layer Pass

```powershell
python tools/evals/zuno/rag_eval/run_eval.py `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_tuning_v2_graph_relation_small.jsonl `
  --knowledge-id <knowledge_id> `
  --profile-set local_compare `
  --answer-mode llm `
  --judge-mode llm `
  --trace-langsmith `
  --output-dir .local/evals/agentchat/rag_eval/runs/<run_id>
```

## Acceptance Gates

第一阶段建议这样看结果：

1. `rag_graph_chunk_backed` 在 `graph_relation` 类问题上，`Recall@K` 和 `MRR@K` 不应低于 `baseline_rag`
2. 如果 `3hop` 提升了 `Recall@K`，但明显拉低 `Context Precision@K`，则不默认推广
3. `Citation Accuracy` 不能因为 GraphRAG 打开而明显下降
4. 如果 `rag_rerank` 已经和 GraphRAG 持平，则优先保守保留 `rag_rerank`

## Evidence Output

每次 run 至少保留：

- `retrieval_results.jsonl`
- `answers.jsonl`
- `judge_results.jsonl`（如果有）
- `metrics.json`
- `report.md`

这样后续才能回看：

- 哪个 profile 赢
- 赢在 recall 还是 precision
- GraphRAG 是否真的改善了图关系类问题

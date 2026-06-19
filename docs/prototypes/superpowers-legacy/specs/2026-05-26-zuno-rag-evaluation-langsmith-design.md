# Zuno RAG Evaluation And LangSmith Design

## Goal

建立一套可重复运行的 RAG / GraphRAG 评测任务，用真实本地文档验证不同知识库配置是否提升检索与回答质量，并产出可以写进简历的可信指标。

测试语料第一版使用：

```text
F:\Onboard anything\02_Notes_笔记\2llm_note\Python
```

评测覆盖五类指标：

- Retrieval Recall：该找的证据有没有找到。
- Context Precision：召回证据是否干净、有用、排序靠前。
- Faithfulness：模型回答是否严格基于证据。
- Answer Correctness：最终答案是否正确。
- Citation Accuracy：引用是否真的支撑答案。

## LangSmith Is Useful But Not Sufficient

LangSmith 不负责直接“算召回率”。召回率、MRR、NDCG 这类指标需要离线评测脚本根据 `query -> gold evidence` 数据集计算。

LangSmith 的职责是：

- 记录每次查询的完整 trace。
- 保存 retrieval mode、top-k chunks、graph paths、rerank scores、final context、final answer。
- 对比不同参数配置下的链路差异。
- 回放失败样本，定位是 chunk、embedding、rerank、GraphRAG 入口还是回答生成问题。

本地离线评测脚本的职责是：

- 构建/读取评测集。
- 批量执行不同配置。
- 计算指标。
- 输出 JSONL / Markdown 报告。

所以完整方案是：

```text
offline evaluator computes metrics
LangSmith records traces and supports failure analysis
```

如果没有 LangSmith API key，评测也必须能在本地完成；有 key 时再把 trace 上报到 LangSmith。

## Test Corpus

第一版选择 Python 笔记目录，因为它具备几个优势：

- 文档数量足够。
- Markdown 标题结构清晰。
- 覆盖语法、标准库、对象模型、函数签名等多个主题。
- 适合测试通用分段、父子分段、Q&A 片段和关系型问题。

导入范围第一版不全量吞整个目录，先选择 20 到 40 个 Markdown 文件，避免评测成本失控。

建议优先选：

- `Python 关键字.md`
- `Python 变量、命名空间与对象绑定.md`
- `Python 对象引用、命名空间实现.md`
- `Python 如何读函数与方法签名.md`
- `collections.md`
- `dataclasses.md`
- `functools.md`
- `contextlib.md`

## Evaluation Dataset

评测集使用 JSONL，放在：

```text
src/backend/zuno/evals/rag_eval/python_notes_eval.jsonl
```

每行结构：

```json
{
  "id": "py_eval_001",
  "query": "Python 中变量和对象绑定是什么关系？",
  "reference_answer": "变量名只是对象引用的绑定，赋值会让名字指向对象，而不是把对象复制到变量里。",
  "gold_evidence": [
    {
      "file_contains": "Python 变量、命名空间与对象绑定.md",
      "text_contains": "变量名只是对象的引用"
    }
  ],
  "answer_type": "fact",
  "required_citations": true
}
```

第一版 gold evidence 不要求提前知道 chunk_id，因为 chunk_id 会随 chunk 策略变化。用 `file_contains + text_contains` 做稳定证据定位。评测运行时把召回 chunk 映射回文件名和文本片段判断命中。

后续可以在每次建库后生成 `gold_chunk_id` 缓存，加速评测。

## Metrics

### 1. Retrieval Recall

问题：该找的证据有没有找到？

计算：

```text
Recall@K = 命中的 gold evidence 数 / gold evidence 总数
HitRate@K = Top K 中是否至少命中一个 gold evidence
```

命中规则第一版：

- retrieved chunk 的 `file_name` 包含 `file_contains`。
- retrieved chunk 的 `content` 包含或高度相似于 `text_contains`。

### 2. Context Precision

问题：召回结果是不是干净、有用、排序靠前？

计算：

```text
ContextPrecision@K = Top K 中相关 chunk 数 / K
MRR = 第一个 gold evidence 命中位置的倒数
NDCG@K = 按相关性加权的排序质量
```

第一版相关性判断：

- 先用 gold evidence 规则判断强相关。
- 其余 chunk 可用 LLM judge 标注为 `relevant / partially_relevant / irrelevant`。

为了可复现，脚本必须把 LLM judge 的输入输出落盘。

### 3. Faithfulness

问题：回答有没有严格基于证据？

计算方式：

- 将 final answer 拆成若干 claim。
- 对每个 claim 判断是否被 retrieved context 支持。
- 输出 0 到 1 分。

第一版使用 LLM judge：

```text
Given answer claims and retrieved context, mark each claim as supported / unsupported.
Faithfulness = supported_claims / total_claims
```

要求 judge 输出 JSON，便于审计。

### 4. Answer Correctness

问题：最终答案是否真的正确？

计算方式：

- 与 `reference_answer` 对比。
- 判断是否覆盖关键点、是否有明显错误、是否答非所问。
- 输出 0 到 1 分。

第一版使用 LLM judge；对于少量可规则判断的问题，可以补充关键词覆盖率。

### 5. Citation Accuracy

问题：引用是否真的支撑答案？

计算方式：

- 每条 citation 必须指向 retrieved context 中存在的 chunk。
- citation 对应 chunk 必须支持其附近的 answer claim。

输出：

```text
CitationAccuracy = 有效 citation 数 / citation 总数
```

如果答案没有 citation，但样本 `required_citations=true`，该项计为 0。

## Evaluation Profiles

每次评测至少跑这些 profile：

### Baseline RAG

```text
chunk_mode = general
retrieval_mode = rag
top_k = 5
rerank = off
vector_db = Chroma or Milvus
```

### RAG + Rerank

```text
chunk_mode = general
retrieval_mode = rag
top_k = 5
rerank = on
rerank_top_k = 3
score_threshold = 0.70
```

### Parent-Child RAG

```text
chunk_mode = parent_child
retrieval_mode = rag
rerank = on
```

### RAG + GraphRAG

```text
index_capability = rag_graph
retrieval_mode = rag_graph
graph_hop_limit = 2
max_paths_per_entity = 10
rerank = on
```

### RAG + GraphRAG 3-hop

```text
graph_hop_limit = 3
max_paths_per_entity = 10
```

用于观察 3-hop 是否提升关系型问题，还是引入噪声。

## Expected Reports

评测输出目录：

```text
src/backend/zuno/evals/rag_eval/runs/<timestamp>/
```

每次运行输出：

- `config.json`：本次 profile 配置。
- `retrieval_results.jsonl`：每条 query 的召回结果、scores、graph paths。
- `answers.jsonl`：最终回答和 citations。
- `judge_results.jsonl`：LLM judge 结果。
- `metrics.json`：机器可读指标。
- `report.md`：人工可读报告。

报告必须包含：

```text
Profile
Corpus summary
Overall metrics
Metrics by answer_type
Top failure cases
Parameter comparison
Resume-safe summary
```

## LangSmith Trace Metadata

每次 online / offline 查询都应附带：

- `trace_id`
- `eval_run_id`
- `eval_sample_id`
- `profile_name`
- `knowledge_id`
- `retrieval_mode`
- `index_capability`
- `chunk_mode`
- `vector_db`
- `top_k`
- `rerank_enabled`
- `rerank_top_k`
- `score_threshold`
- `graph_hop_limit`
- `max_paths_per_entity`

LangSmith run tags：

```text
zuno
rag-eval
python-notes
<profile_name>
```

## Runtime Flow

### Offline Evaluation

```text
load eval dataset
-> ensure test knowledge exists
-> upload selected Python notes
-> wait for pipeline completion
-> run retrieval for every query/profile
-> generate answer with citations
-> run judges
-> compute metrics
-> write reports
-> optionally send traces to LangSmith
```

### Online Debug

```text
user runs a test query in UI
-> backend attaches config metadata
-> retrieval result includes text evidence + graph evidence
-> answer includes citations
-> trace_id shown in UI
-> user can inspect trace in LangSmith if enabled
```

## Service Verification

完整测试必须证明基础设施真实参与链路：

### PostgreSQL

Evidence:

- knowledge row exists.
- knowledge_file rows exist.
- knowledge_config snapshot persisted.
- knowledge_task / events exist for indexing.

### Redis

Evidence:

- `task_progress:{task_id}` exists during indexing.
- optional retrieval cache key exists if cache is enabled.

### RabbitMQ

Evidence:

- `knowledge.parse`
- `knowledge.index`
- `knowledge.graph`

queues receive and drain tasks.

### MinIO

Evidence:

- uploaded source files exist as objects.
- parser can download objects for indexing.

### Vector DB: Milvus

Evidence:

- collection exists for knowledge id.
- vector count roughly matches chunk count.
- search returns scored chunks.

Chroma can remain as local fallback, but enterprise RAG profile should run on Milvus.

### Neo4j

Evidence:

- Entity nodes exist.
- RELATES_TO edges exist.
- Chunk -> Entity evidence links exist when enabled.
- Graph query returns paths for relation samples.

### LangSmith

Evidence:

- at least one offline eval run appears with metadata.
- retrieval profile and sample id visible in run metadata.
- top-k chunks and graph paths visible in trace payload or child run outputs.

## Test Commands

Final commands will be implemented later, but target shape:

```text
python -m zuno.evals.rag_eval.prepare_python_notes_corpus \
  --source "F:\Onboard anything\02_Notes_笔记\2llm_note\Python" \
  --limit-files 40

python -m zuno.evals.rag_eval.run_eval \
  --dataset src/backend/zuno/evals/rag_eval/python_notes_eval.jsonl \
  --profiles baseline_rag,rag_rerank,parent_child_rag,rag_graph \
  --knowledge-name ZunoPythonEval \
  --trace-langsmith true
```

## Resume-Safe Output

只有当报告真实生成后，才能写具体数字。

可写格式：

```text
构建 RAG 评测闭环，基于 Python 笔记知识库构造 query-gold evidence 数据集，统计 Retrieval Recall、Context Precision、Faithfulness、Answer Correctness 和 Citation Accuracy，并结合 LangSmith trace 回放失败样本，对 chunk 策略、Milvus 向量检索、Rerank 与 GraphRAG 参数进行对比调优。
```

如果跑出真实对比数据，可进一步写：

```text
在自建 Python 知识库评测集上，RAG + Rerank 相比基础 RAG 将 Recall@5 从 X 提升到 Y；RAG + GraphRAG 在关系型问题上将 Citation Accuracy 从 A 提升到 B。
```

数字必须来自 `metrics.json`，不能手写估算。

## Implementation Status

2026-05-26 已落地第一版评测骨架：

- 评测数据集：`src/backend/zuno/evals/rag_eval/python_notes_eval.jsonl`
- 指标计算模块：`src/backend/zuno/evals/rag_eval/metrics.py`
- Python 笔记语料准备：`src/backend/zuno/evals/rag_eval/prepare_python_notes_corpus.py`
- 知识库同步导入脚本：`src/backend/zuno/evals/rag_eval/ingest_prepared_corpus.py`
- 多 profile 评测 runner：`src/backend/zuno/evals/rag_eval/run_eval.py`
- 单元测试：`src/backend/zuno/test/test_rag_eval_metrics.py`

当前已实现本地离线计算：

- Retrieval Recall / HitRate@K
- Context Precision@K
- MRR@K
- NDCG@K
- Citation Accuracy
- 可读取 judge 输出中的 Faithfulness 和 Answer Correctness
- 可选 LangSmith trace：按 `eval_run_id`、`eval_sample_id`、`profile_name`、`retrieval_mode`、`knowledge_ids` 记录评测样本元数据
- 评测报告输出：每个 profile 写出 `retrieval_results.jsonl`、`answers.jsonl`、`judge_results.jsonl`、`metrics.json`，总目录写出 `report.json` 和 `report.md`
- 语料准备脚本会按文件名去重，避免 paired note 中同名标准库笔记重复污染测试集
- profile 配置已真实进入检索链路：`baseline_rag`、`rag_rerank`、`rag_graph`、`rag_graph_3hop` 会分别传入不同的 `rerank_enabled`、`score_threshold`、`graph_hop_limit` 和 `max_paths_per_entity`，保证后续指标对比能对应具体参数。
- 2026-05-27 已在 Docker worker 中用 `ZunoPythonEval` 知识库导入 40 个 Python Markdown 笔记文件，并基于 Milvus 跑通真实 smoke eval。当前 8 条样本的结果保存在本地忽略目录 `src/backend/zuno/evals/rag_eval/runs/smoke-real/`：
  - `baseline_rag`: Recall@5 0.8750，HitRate@5 1.0000，Context Precision@5 0.9500，Citation Accuracy 0.9583。
  - `rag_rerank`: Recall@5 0.8125，Context Precision@5 0.5750，Citation Accuracy 0.6250。
  - `rag_graph`: Recall@5 0.8125，Context Precision@5 0.3500，Citation Accuracy 0.5833。
  - 结论：当前小样本下 baseline RAG 优于 rerank / GraphRAG profile，说明 rerank、query rewrite 和 GraphRAG 参数仍需继续调优；这组数字可以作为“已建立评测闭环”的证据，但不应包装成 GraphRAG 提升结论。
- 2026-05-27 已补充 `--answer-mode llm` 与 `--judge-mode llm`，并在 Docker worker 中跑通 `smoke-llmjudge`：
  - `baseline_rag`: Recall@5 0.8750，Context Precision@5 0.9500，Faithfulness 0.9500，Answer Correctness 0.9500，Citation Accuracy 0.9583。
  - 本次命令同时打开了 `--trace-langsmith`，报告中 `trace_langsmith=true` 且 `langsmith_configured=false`，说明 trace 开关链路可执行，但当前环境尚未配置真实 LangSmith API key / project，因此没有验证云端可见 trace。
- 2026-05-27 已创建本地 LangSmith Personal Access Token，并只写入未提交的 `infra/docker/docker_config.local.yaml`。随后在 Docker worker 中跑通 `smoke-langsmith`：
  - `baseline_rag`: Recall@5 0.8750，Context Precision@5 0.9500，Faithfulness 0.9438，Answer Correctness 0.9438，Citation Accuracy 0.9583。
  - 本次报告中 `trace_langsmith=true` 且 `langsmith_configured=true`。
  - LangSmith 云端项目 `zuno-rag-eval` 已出现 trace，项目页显示最近 7 天 trace count 为 24；run 列表可见 `eval_run_id=smoke-langsmith`、`eval_sample_id`、`knowledge_ids` 等 metadata。

尚未完成：

- 当前 LLM judge 使用 Zuno 已配置对话模型输出 JSON 分数；如果后续需要更规范的线上评测，可以继续接 LangSmith Evaluation judge 或固定的独立裁判模型。

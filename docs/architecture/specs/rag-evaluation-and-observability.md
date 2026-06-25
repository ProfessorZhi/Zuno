# RAG Evaluation And Observability

## 目标

建立一套可重复运行的 RAG / GraphRAG 评测体系，并把可观测性正式纳入架构，而不是把评测和 trace 当作零散辅助工具。

这套体系必须支持：

- 离线评测
- 本地低成本运行
- 真实链路回放
- 失败样本分析
- 可写进项目经历的可信结果

## 核心原则

### LangSmith Useful But Not Sufficient

LangSmith 负责 trace，不直接负责计算召回率、MRR、NDCG 等指标。

离线评测脚本负责：

- 读取评测集
- 批量执行
- 计算指标
- 输出报告

完整关系：

```text
offline evaluator computes metrics
LangSmith records traces and supports failure analysis
```

### Offline First

没有 LangSmith API key 时，也必须能在本地完成评测。

### Evidence First

评测不仅看答案，还要看是否找到了真正支撑答案的证据。

## 评测对象

必须覆盖：

- pure RAG
- RAG + rerank
- RAG entry + GraphRAG
- retrieval orchestrator fallback 行为

## 评测数据集

建议采用 JSONL。

每行至少包含：

```json
{
  "id": "sample_001",
  "query": "问题",
  "reference_answer": "参考答案",
  "gold_evidence": [
    {
      "file_contains": "目标文件",
      "text_contains": "目标片段"
    }
  ],
  "required_citations": true
}
```

第一阶段不要把 `chunk_id` 当作 gold truth，因为 chunk 切分策略会变化。

## 指标体系

### Retrieval

- Recall@K
- HitRate@K
- Context Precision@K
- Graph Path Hit Rate

### Answer

- Faithfulness
- Answer Correctness
- Citation Accuracy

### Cost And Runtime

- LLM Call Count
- Embedding Call Count
- Estimated Cost
- Latency

## Observability 目标

每次运行至少要留下：

- query
- resolved mode
- rewritten queries
- enabled retrievers
- retrieved documents
- graph paths
- rerank scores
- final context
- final answer
- cost metadata

## 分层运行模式

### `dev_offline`

- fake embedding
- mock graph extraction
- mock answer
- 不依赖外部 API

### `dev_local`

- local embedding
- mock 或轻量真实抽取
- 能看到真实 retrieval path

### `demo`

- real embedding
- real extraction
- LangSmith trace
- 正式报告输出

## 与架构主线的关系

这套评测体系不是附属品，而是当前主线的一部分：

- 它验证 GraphRAG Project / query policy 是否有价值
- 它验证 GraphRAG 是否真的带来收益
- 它验证 fallback 和 hybrid 策略是否合理
- 它控制开发成本，防止盲目烧 API

## 第一阶段输出

第一阶段至少应有：

- 一套离线可运行评测入口
- 一份 contract review eval 数据集
- 一组可比较的配置结果
- 一条可回放的 trace 链路

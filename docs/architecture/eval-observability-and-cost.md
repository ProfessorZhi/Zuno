# Eval Observability And Cost

本文说明 Zuno 的 Eval / Trace / Cost / Benchmark layer。它用于证明质量、成本、耗时、安全和回归，不是上线后才补的看板。

## Current Local Slice

当前已由 PHASE08、PHASE12 和 PHASE13 证明：

- `src/backend/zuno/platform/model_gateway.py` 记录 model category、token_count、latency_ms、cost_estimate、budget verdict、timeout fallback 和 redacted trace。
- `src/backend/zuno/platform/observability/trace_eval.py` 提供 `ZunoSpan`、LangSmith-compatible metadata、EvalDatasetCase、MetricThreshold、EvalMetricResult 和 ReleaseEvalBaseline。
- `src/backend/zuno/agent/product_baseline.py` 生成 PHASE12 scenario summary / trace summary。
- `src/backend/zuno/platform/observability/product_benchmark.py` 生成 PHASE13 regression summary。
- `StageMetrics` 覆盖 file upload、object store、input gate、parse queue/worker、document IR、index queue/worker、context build、planning、retrieval、rerank、graph expand、tool call、reflection、replan、answer、output gate、artifact 和 feedback。
- `EvalComparisonReport` 区分 `basic_rag`、`static_graphrag`、`agentic_graphrag` baseline labels。

对应测试包括 `tests/evals/test_model_gateway_cost_latency.py`、`tests/evals/test_observability_trace_contract.py`、`tests/evals/test_agentic_graphrag_product_baseline.py`、`tests/evals/test_agentic_graphrag_regression_summary.py` 和全量 `tests/evals`。

## 指标对象

```text
ConversationRunMetrics
  task_id / session_id / workspace_id / selected_knowledge_spaces
  retrieval_profiles / selected_skill / strategy / model_config

StageMetrics
  stage_name / latency_ms / token_count / cost_estimate
  model_id / error_count / retry_count / security_block_count
  trace_event_ids

IngestionMetrics / RetrievalMetrics / PlanningMetrics / SecurityMetrics / CostMetric
  -> release evidence
  -> EvalComparisonReport
  -> regression summary
```

missing required stage 不能 silent pass；PHASE13 对缺失 stage 抛出明确错误。

## Release Gate 用法

PHASE15 closure 应使用这些指标回答：

- deep retrieval 是否有更高 citation coverage。
- dynamic replan 是否改变 trajectory。
- PDF / Office / OCR blocked 是否保持 no fake index。
- binary source object 是否可追溯 sha256。
- cost / latency 是否来自本地 deterministic path、model call、rerank、graph expand 或 OCR/VLM target-blocked boundary。
- security gate 是否有 block / refusal / ask_user / replan 证据。

## Launchable Prototype Target

- 本地 regression summary 进入 closure archive。
- README / AGENTS 只保留入口摘要，指标细节保留在正式专题文档和归档。
- 外部观测适配保持可替换，不把 vendor 数据结构变成唯一事实源。

## Production Scale Target

以下仍不是 Current：

- 外部 LangSmith / OTel sink runtime。
- Prometheus dashboard。
- online eval。
- 持久 trace store。
- CI release gate operations。
- 多租户成本账单和 provider SLA / quota 管理。

## 不变量

- trace / eval / cost 证据必须能回到 task、workspace、artifact、citation 或 source object。
- 不用“测试通过”替代指标覆盖说明。
- Basic RAG / Static GraphRAG 只作为 baseline，不是最终产品模式。

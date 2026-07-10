# Eval, Observability and Cost

所属运行域：Governance & Observability。

## 定位

本专题定义 Agent run 如何被追踪、如何统计模型调用和成本、如何用 fixed benchmark 判断质量。近期目标是本地持久 trace 和可查看 summary，不要求先接完整 LangSmith / OTel 平台。

## Span Tree

```text
agent_run
  -> context_build
  -> memory_read
  -> planning
  -> retrieval
  -> graph_expand
  -> rerank
  -> model_call
  -> tool_call
  -> claim_binding
  -> answer_synthesis
  -> output_gate
  -> memory_commit
  -> eval
```

每个 span 至少记录 run_id、task_id、workspace_id、span name、status、start/end、latency、error/fallback、effective config 摘要。model_call 还要记录 provider、model、slot、token/usage、cost estimate 和 retry。retrieval/citation span 还要记录 failure bucket 所需 trace 字段。

## Measurement Semantics

- measured：同一 fixed case set 完整跑完并产出可比较指标。
- runtime observed：真实运行产生 trace，但不是 benchmark。
- prepared：数据或配置准备完成，但未执行完整 runtime。
- blocked：运行被明确阻塞，有 blocked_reason。

缺少 trace 字段时输出 `unavailable_due_to_missing_trace_fields`。

## Release Gate

Agentic GraphRAG 必须与 standard_rag 使用同一 fixed case set。只有完整 measured profile 才能进入 release gate 判断。

## 当前与短期目标

Current：

- local trace/eval helpers、EnterpriseRAG paired eval runner、failure bucket diagnostics 和 release gate output surface 已存在。
- 完整 LangSmith 接入不是 Current。

Short-term：

- P0 Agent run trace 持久化并可查看。
- P0 fixed benchmark 跑通并达到 baseline gate。
- P1 trace summary 在前端可定位模型调用、retrieval、citation 和 tool failure。

Future Optional：

- LangSmith / OTel backend。
- 大规模在线 eval 平台。
- 企业级成本和合规 dashboard。

# Eval, Observability and Cost

所属运行域：Governance & Observability。

## 定位

本专题定义 Agent run 如何被追踪、如何统计模型调用和成本、如何用 fixed benchmark 判断质量。近期目标是本地持久 trace 和可查看 summary，不要求先接完整 LangSmith / OTel 平台。

## Span Tree

```text
agent_run
  -> input_gate
  -> context_build
  -> memory_read
  -> strategy_select
  -> planning
  -> execute_step
     -> retrieval
     -> graph_expand
     -> rerank
     -> model_call
     -> tool_call
  -> evidence_gate
  -> claim_binding
  -> reflection
  -> replan
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

## 分层指标

| 层 | 指标 |
| --- | --- |
| Retrieval | Recall@K、MRR、Evidence Precision/Recall、doc/text/span hit |
| Generation | Faithfulness、Answer Relevancy、Citation Accuracy、Answer Correctness、Unsupported Claim Rate |
| Agent | Plan success、step acceptance、replan success、reflection pass、average retrieval rounds、tool success、abstain correctness |
| Memory | retrieval relevance、stale/conflict rate、promotion quality、Reflexion reuse rate、repeated failure reduction |
| Product | thumbs down、follow-up、session resolution、latency、cost |

离线到线上反馈闭环：

```text
offline eval
-> release gate
-> product feedback
-> failure case
-> fixed dataset update
-> regression eval
```

Product feedback 不能直接证明质量完成；它只能生成 failure case、dataset update 或人工审查输入。质量完成仍必须由 fixed benchmark 和 release gate 证明。

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

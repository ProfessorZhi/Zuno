# PHASE13 Eval Trace Cost Benchmark

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE13_eval-trace-cost-benchmark
status: pending

## 目标

建设 Eval / Trace / Cost / Benchmark layer，记录检索质量、回答质量、规划质量、反思与重规划效果、安全阻断、成本和耗时，形成 release baseline / regression summary。

## 范围

- metrics：retrieval_rounds、retrievers_used、evidence_count、citation_coverage、unsupported_claim_rate。
- planning metrics：plan_step_count、replan_count、reflection_count、reflexion_count。
- tool / security metrics：tool_call_count、security_block_count、approval_count。
- cost / latency metrics：latency_ms、token_count、cost_estimate。
- release baseline and regression report。
- Basic RAG 和 Static GraphRAG 只作为 eval baseline。

## 目标架构拼接点

本 phase 拼到 Governance / Trace / Eval Envelope，并把“能跑”升级为“可评测、可回放、可回归”：

- Retrieval metrics 评估 standard / deep profile。
- Answer metrics 评估 citation coverage、unsupported claim、faithfulness。
- Planning metrics 评估 strategy selection、replan effectiveness、reflection usefulness、reflexion reuse。
- Security metrics 评估 gate blocking 和 policy compliance。
- Cost / latency metrics 约束 deep retrieval、rerank、multi-round 和 model calls。

这些指标是 PHASE15 closure 的证据来源，不能只保存在测试输出里。

## 并行开发可行性

本 phase 可由 Workstream G 与 PHASE09-PHASE12 交错推进，但最终 baseline 必须等 E2E event schema 稳定后生成。

可并行：

- metric collector 与 regression report generator 可并行。
- cost guard 与 trace schema tests 可并行。
- baseline label mapping 可独立实现。

不可并行：

- 不得在 E2E trace 未稳定前写最终 release baseline。
- 不得让 missing metric 默认通过。
- 不得把 Basic RAG baseline 混写成产品 Current mode。

## 详细执行卡

- 输入依赖：PHASE08 cost metrics、PHASE10 trace events、PHASE12 E2E scenario output、Program 5 benchmark target。
- 主要交付物：TraceRecord、EvalMetric、CostMetric、regression summary、release baseline、failure cases report、basic/static/agentic comparison labels。
- 可并行工作包：metric collector、report writer、baseline comparison、guardrail tests 可拆；metric schema 名称由单 owner 冻结。
- Coordinator 锁点：Basic RAG / Static GraphRAG 只能作为 eval baseline，不得写成最终产品模式。
- 下游交接：PHASE14 记录 eval/release gate；PHASE15 closure summary 引用 metrics、trace、cost、latency 和 remaining targets。
- PR / commit 建议：`feat(eval): add trace cost benchmark baseline` 与 `test(eval): cover release summary metrics`。

## 禁止范围

- 不把 eval baseline 写成产品最终模式。
- 不上传原始私有文档内容到外部评测服务。
- 不让 missing metric silent pass。

## 验收闸门

- metrics fields present test 通过。
- cost guard works test 通过。
- regression report generated test 通过。
- baseline comparison 不 silent pass。

## 验证命令

```powershell
git diff --check
pytest -q tests/evals -p no:cacheprovider
pytest -q tests/evals/test_agentic_graphrag_product_baseline.py -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/platform/observability/**`
- `src/backend/zuno/evals/**`
- `tools/evals/zuno/**`
- `tests/evals/**`
- `docs/architecture/production-readiness.md`

## 需要修改的文件

- `src/backend/zuno/platform/observability/**`
- `src/backend/zuno/evals/**`
- `tools/evals/zuno/**`
- `tests/evals/**`
- eval report fixtures under tests if existing

## 执行拆解

1. 写 metrics presence focused test。
2. 写 cost guard / budget focused test。
3. 写 regression summary generation test。
4. 实现 local deterministic metric collector。
5. 将 E2E scenario 接入 eval report。

## 多 agent 分工

- Workstream G owner。
- Workstream F/B/E 提供 planning/retrieval/security events。
- Coordinator 审查 release gate wording。

## 需要返回的证据

- metrics.json example。
- regression summary。
- cost report。
- baseline labels for Basic RAG / Static GraphRAG / Agentic GraphRAG。

## 停止条件

- metrics 需要真实外部 observability service。
- trace 输出包含未脱敏私有文档原文。
- release report 无法区分 baseline 与 target。

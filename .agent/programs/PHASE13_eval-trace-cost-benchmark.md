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

## Per Conversation / Per Stage Metrics

PHASE13 必须把每次对话、每个 task、每个关键 stage 的指标写成统一 schema，而不是只在测试末尾生成一个总分。

### ConversationRunMetrics

```text
ConversationRunMetrics
  task_id
  session_id
  workspace_id
  user_id
  selected_knowledge_spaces
  retrieval_profiles
  selected_skill
  strategy
  model_config
  started_at
  ended_at
```

### StageMetrics

```text
StageMetrics
  stage_name: file_upload / object_store_write / input_gate / parse_queue / parse_worker / document_ir / index_queue / index_worker / context_build / planning / retrieval / rerank / graph_expand / tool_call / reflection / replan / answer / output_gate / artifact / feedback
  latency_ms
  token_count
  cost_estimate
  model_id
  error_count
  retry_count
  security_block_count
  trace_event_ids
```

### RetrievalMetrics

```text
RetrievalMetrics
  retrieval_rounds
  retrievers_used
  candidate_count
  reranked_count
  evidence_count
  citation_count
  citation_coverage
  source_span_accuracy
```

### IngestionMetrics

```text
IngestionMetrics
  files_uploaded
  files_indexed
  files_failed
  files_blocked
  parse_duration_ms
  index_duration_ms
  parser_id
  parser_format
  dependency_status
  blocked_reason
  retry_count
  dead_letter_count
  reconciler_findings
  ocr_vlm_pages
  ocr_vlm_cost_estimate
  binary_bytes_processed
```

### PlanningMetrics

```text
PlanningMetrics
  plan_step_count
  strategy
  skill_selected
  replan_count
  reflection_count
  reflexion_count
  replan_reason
```

### SecurityMetrics

```text
SecurityMetrics
  input_blocks
  retrieval_acl_denied
  tool_approval_required
  output_dlp_blocks
  prompt_injection_flags
```

### EvalComparisonReport

```text
EvalComparisonReport
  baseline_label: basic_rag / static_graphrag / agentic_graphrag
  quality_delta
  latency_delta
  cost_delta
  citation_delta
  security_delta
```

### 必须回答的问题

release / regression report 必须能回答：

- 深度检索是否比标准检索提升 citation coverage？
- Agentic Replan 是否改善 evidence_count？
- Reflection 是否降低 unsupported_claim_rate？
- GraphRAG 是否值得多花成本？
- 哪一步造成 latency / cost 上升？
- 安全 gate 是在哪一步拦截的？
- 哪些文件解析失败或 blocked？
- PDF / Office / OCR blocked 是否没有 fake index？
- 二进制对象是否能追溯 sha256？
- 异步解析耗时主要在哪一步？
- deep retrieval 的额外成本是否来自 graph / rerank / OCR？
- OCR / VLM 是否因为缺 provider 被正确 blocked？

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
- 主要交付物：TraceRecord、ConversationRunMetrics、StageMetrics、IngestionMetrics、RetrievalMetrics、PlanningMetrics、SecurityMetrics、CostMetric、EvalComparisonReport、regression summary、release baseline、failure cases report、basic/static/agentic comparison labels。
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
- missing stage metrics 不得 silent pass。
- IngestionMetrics 必须覆盖 uploaded / indexed / failed / blocked、parse / index duration、parser format、dependency status、blocked reason、retry、dead letter、reconciler findings、OCR / VLM pages / cost estimate 和 binary bytes processed。
- StageMetrics 必须包含 file_upload、object_store_write、parse_queue、parse_worker、document_ir、index_queue、index_worker、retrieval、graph_expand 和 answer。
- report 必须区分 quality / cost / latency / security。
- EvalComparisonReport 必须区分 basic_rag / static_graphrag / agentic_graphrag baseline labels。
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

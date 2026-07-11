# Test Matrix

## 测试层级

| 层级 | 目的 | 禁止替代 |
| --- | --- | --- |
| contract unit | schema、serialization、routing、limits | 不能证明真实 runtime |
| node unit | 单节点输入输出和失败语义 | 不能证明图闭环 |
| graph integration | conditional edge、replan、interrupt/resume | 不能证明真实 provider 质量 |
| persistence restart | 进程重建后恢复 run/checkpoint/approval | 不能只做对象 round-trip |
| product API | Completion/Workspace/SSE/approval/trace | 不能只调用 service 内部函数 |
| retrieval paired eval | standard/deep/agentic 同 case set | 不能使用不同 case set |
| browser E2E | 上传、AgentChat、审批、引用、trace、刷新恢复 | 不能只截图静态页面 |

## 必须覆盖的场景

1. 简单请求选择 direct，并只运行必要节点。
2. 单工具请求选择 react，Tool result 变成 normalized Observation。
3. 多步骤研究选择 plan_and_execute。
4. 第一次 retrieval empty，Reflection 返回 RETRIEVE_MORE。
5. Replan 改变 query strategy 或 retrieval scope。
6. 第二轮 EvidenceLedger 增加新 evidence，且保留 round/query/source span。
7. evidence 足够但草稿错误，走 REWRITE_ANSWER，不重新检索。
8. citation coverage 不足时不得 finalize strict answer。
9. 高副作用 Tool 产生 interrupt；approve 后只执行一次。
10. reject/timeout 变成 Observation，Agent replan 或 abstain。
11. restart 后从 SQLite checkpoint 恢复。
12. Reflexion candidate 进入 pending review，approved 后出现在后续 ContextPack。
13. sensitive lesson 被 governance 阻止。
14. PDF 页面 SourceSpan 能从 citation 跳回原页/块。
15. benchmark 缺 profile/trace 字段时输出 unavailable/blocked，不得 measured pass。

## 建议新增测试文件

```text
tests/agent/runtime/
  test_runtime_state_contract.py
  test_runtime_graph_routes.py
  test_runtime_plan_execution.py
  test_runtime_reflection_replan.py
  test_runtime_interrupt_resume.py
  test_runtime_restart_persistence.py
  test_runtime_memory_reflexion.py

tests/knowledge/
  test_evidence_ledger.py
  test_corrective_retrieval_runtime.py
  test_pdf_source_span_vertical.py

tests/api/
  test_completion_unified_runtime.py
  test_workspace_runtime_recovery.py

tests/e2e/
  test_unified_agent_product_scenario.py
```

命名应遵守仓库现有测试目录；若已有相同 owner，合并而不是重复新建。

## Release Gate

```text
Agentic Recall@5 >= standard_rag
Evidence Text Available@5 >= 0.60
Source Doc Citation Accuracy >= 0.85
Citation Accuracy >= 0.30
Answer Correctness >= standard_rag
Unsupported Claim Rate 不得恶化
```

新增 Agent runtime 指标：

```text
replan_execution_success_rate
reflection_pass_after_replan_rate
approval_resume_success_rate
restart_recovery_success_rate
reflexion_reuse_rate
repeated_failure_reduction
average_retrieval_rounds
average_actions_per_step
abstain_correctness
```

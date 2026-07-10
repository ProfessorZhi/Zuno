# Evidence-Span Hardening Closure Checklist

state: completed
program: zuno-evidence-span-agentic-graphrag-hardening-v1
active_program: none
current_phase: none
latest_completed_program: `zuno-evidence-span-agentic-graphrag-hardening-v1`

## 当前关闭状态

本 program 已归档关闭。当前 active phase 是：

- none

## Program 关闭目标

本轮关闭时必须能证明：

```text
Agentic GraphRAG 的 doc-level retrieval 增益已经转化成 evidence-span retrieval / citation / answer quality 的可测增益。
```

最低质量闸门：

- [ ] `Evidence Text Available@5 >= 0.60`：未 measured pass；真实 paired eval 尝试未完成 agentic profile。
- [ ] `Source Doc Citation >= 0.85`：未 measured pass；真实 paired eval 尝试未完成 agentic profile。
- [ ] `Citation Accuracy >= 0.30`：未 measured pass；真实 paired eval 尝试未完成 agentic profile。
- [ ] `Answer Correctness >= standard_rag baseline`：未 measured pass；真实 paired eval 尝试未完成 agentic profile。
- [x] `blocked_not_measured`、`prepared`、`runtime_observed` 没有被写成 `measured`
- [x] strict citation 没有用 doc-level citation 冒充
- [x] `deep_graphrag` 没有被写成完整 product Agentic Runtime

## Phase 关闭清单

- [x] PHASE01 完成 eval truth source、gap buckets 和 failure taxonomy。
- [x] PHASE02 完成 source span provenance contract。
- [x] PHASE03 完成 citation-sized chunks 与 parent context chunks。
- [x] PHASE04 完成 lexical / phrase evidence retriever。
- [x] PHASE05 完成 entity-chunk bidirectional graph index。
- [x] PHASE06 完成 evidence-aware reranker。
- [x] PHASE07 完成 claim-level citation binder。
- [x] PHASE08 完成 hard negative coverage、release gate 输出面、归档和 no-active closure；真实 paired eval gate 保持 `blocked_not_measured_due_to_agentic_profile_incomplete`。

## 必须保留的历史边界

Program 3 Mega 仍是最近完成的 launchable baseline：

- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`

本 program 不能改写 Program 1 / Program 2 / Program 3 Mega 的 closure evidence。新的结论只能作为 evidence-span hardening 的增量 Current。

## 最小验证命令

每个 phase 关闭前至少运行相关 focused tests。本 program 收口前必须运行：

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
pytest -q tests/evals/test_enterprise_rag_paired_benchmark.py tests/evals/test_rag_eval_metrics.py -p no:cacheprovider
```

如果 runtime 代码、API、frontend 或 architecture docs 被修改，还必须追加对应 focused tests / verifier。

## 下一轮检查

- 当前 phase 是 none；本 program 已进入历史归档。
- 后续如继续 evidence-span hardening，必须打开新 program 或重开明确 phase。
- 如果进入 runtime，必须先写 tests，再改实现。
- 所有新增指标必须说明是 fixed benchmark、runtime observed、prepared 还是 blocked。

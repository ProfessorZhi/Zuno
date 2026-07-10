# PHASE01 Eval Truth Source And Gap Buckets

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE01_eval-truth-source-and-gap-buckets
status: completed
owner: Eval / Retrieval

## 目标

把 EnterpriseRAG paired eval 从平均分拆成能指导修复的 failure buckets：

- `doc_miss`：正确文档没有进入 top-k。
- `doc_hit_text_miss`：正确文档进入 top-k，但 gold evidence text 没进入 context。
- `text_hit_citation_miss`：gold evidence text 进入 context，但 citation 没绑定。
- `citation_hit_answer_wrong`：citation 绑定正确，但 answer synthesis 错。

## 范围

- 固定 EnterpriseRAG paired benchmark 为当前 truth source。
- 明确每个指标的来源：fixed benchmark、runtime observed、prepared、blocked。
- 扩展 metrics/report/failure cases，让 retrieval、evidence text、citation binding、answer synthesis 的责任边界可见。

## 禁止范围

- 不改 GraphRAG runtime 逻辑。
- 不调 citation builder。
- 不把当前诊断结果写成质量提升。
- 不把 missing dataset 或 blocked_not_measured 写成 measured。

## 验收闸门

- [x] `metrics.json` 能输出四类 failure bucket 计数。
- [x] `report.md` 解释 `Evidence Text Available@5` 和 strict citation 的关系。
- [x] `failure_cases.md` 能按 bucket 列出样本。
- [x] 当前质量目标仍保持 Target，不写成 Current。

## 完成事实

PHASE01 已完成 eval 诊断能力，不表示 evidence-span 质量目标已经达标。

新增 `evidence_conversion_diagnostics` 字段：

- `failure_buckets`：四类互斥 failure bucket 计数，包含 `doc_miss`、`doc_hit_text_miss`、`text_hit_citation_miss`、`citation_hit_answer_wrong`。
- `bucket_items`：按 case/profile 记录可判定 bucket 和对应指标值。
- `unavailable_items`：trace 或 per-sample 字段不足时记录 `unavailable_due_to_missing_trace_fields`。
- `measured_failure_bucket_count`：只统计 fixed benchmark 中真实可判定的 failure bucket 数。

报告边界：

- `Evidence Text Available@5` 只证明 gold evidence text 进入 top-k context。
- strict `Citation Accuracy` 还要求 answer citation 绑定到 gold evidence text。
- `Source Doc Citation Accuracy` 只是 source document 级中间指标，不能冒充 strict citation。
- `blocked_not_measured` 和 `prepared_not_measured` 的 bucket 计数保持 0，不写成 measured。

本轮没有运行完整 EnterpriseRAG paired eval；当前完成证据来自 focused tests 和 guardrail verifier。

## 验证命令

```powershell
pytest -q tests/evals/test_enterprise_rag_paired_benchmark.py tests/evals/test_rag_eval_metrics.py -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
git diff --check
```

## 需要先读取

- `tools/evals/zuno/AGENTS.md`
- `tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py`
- `tools/evals/zuno/rag_eval/run_eval.py`
- `tools/evals/zuno/rag_eval/metrics.py`
- `tests/evals/test_enterprise_rag_paired_benchmark.py`
- `tests/evals/test_rag_eval_metrics.py`

## 需要修改的文件

预计修改范围：

- `tools/evals/zuno/rag_eval/**`
- `tests/evals/**`
- `.agent/programs/**`

## 执行拆解

1. 读取当前 EnterpriseRAG paired run 输出结构。
2. 找出 per-sample retrieval context、citation、answer metrics 的可用字段。
3. 为可判定 bucket 写真实分类。
4. 对缺少 trace 字段的 bucket 输出 `unavailable_due_to_missing_trace_fields`，不编造。
5. 更新 report 和 tests。

## 多 agent 分工

默认挂机模式即可。若拆分，只允许 Eval 工具和 tests 两条独立 workstream。

## 需要返回的证据

- 修改文件列表。
- 新增 bucket 字段示例。
- focused tests 结果。
- 当前哪些 bucket 仍因 trace 字段不足不可判定。

## 停止条件

PHASE01 只能在诊断可测后关闭；不得因为写完 README 或计划而关闭。

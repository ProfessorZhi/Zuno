# PHASE06 Evidence-Aware Reranker

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE06_evidence-aware-reranker
status: active
owner: Retrieval / Eval

## 目标

把 rerank 从“相关性排序”升级为“可回答、可引用证据排序”。

## 范围

rerank score 至少考虑：

- relevance
- answerability
- exact evidence presence
- citation span quality
- source authority
- ACL allowed
- freshness / stale risk

## 禁止范围

- 不引入未验证的外部 reranker 作为 Current。
- 不为 benchmark 泄漏 gold evidence。

## 验收闸门

- top-k context 更像 evidence bundle。
- `gold_doc_recalled_but_low_rank` 下降。
- `graph_context_non_gold` 和无用背景噪声下降。

## 验证命令

```powershell
pytest -q tests/evals/test_enterprise_rag_paired_benchmark.py tests/evals/test_rag_eval_metrics.py -p no:cacheprovider
git diff --check
```

## 需要先读取

- `src/backend/zuno/knowledge/agentic_graphrag.py`
- `tools/evals/zuno/rag_eval/run_eval.py`
- `tools/evals/zuno/rag_eval/metrics.py`

## 需要修改的文件

预计修改范围：

- `src/backend/zuno/knowledge/**`
- `tools/evals/zuno/rag_eval/**`
- `tests/evals/**`

## 执行拆解

1. 定义 evidence-aware score components。
2. 为 each context 输出 score breakdown。
3. 更新 report，解释质量收益和成本。

## 多 agent 分工

可拆 score design 与 report/test workstream，主线程收口。

## 需要返回的证据

- score breakdown 示例。
- per-question-type 指标变化。
- failure bucket 变化。

## 停止条件

只有 rerank 对 evidence availability 或 citation 指标产生真实改善后才能关闭。

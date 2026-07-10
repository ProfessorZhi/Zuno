# PHASE06 Evidence-Aware Reranker

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE06_evidence-aware-reranker
status: completed
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

- [x] top-k context 使用 evidence-aware score，不只按 relevance 排序。
- [x] trace 输出 pre-rerank rank、post-rerank rank、rank delta、feature scores 和 selected reason。
- [x] local tests 覆盖 phrase evidence 优先于 keyword noise、ACL denied 不进入 final context、graph/support/span feature 可见。

## 完成事实

PHASE06 已完成 local deterministic evidence-aware reranker baseline，不表示 external reranker provider 已接入，也不表示 fixed benchmark quality gate 已达标。

Current 已实现：

- `EvidenceItem` 保留 `rerank_features`、`rank_before`、`rank_after`、`rank_delta`、`evidence_selected_reason` 和 `demotion_reason`。
- Reranker 综合 semantic relevance、lexical / phrase match、answerability、exact evidence presence、citation span quality、source authority、freshness、ACL allowed、graph support、duplicate penalty 和 context diversity。
- Trace payload 中每条 evidence item 输出 feature breakdown 和排序变化。
- Local deterministic tests 证明 phrase evidence 能排在 keyword noise 前，ACL denied evidence 不进入 final context。

边界：

- 当前没有接 external reranker provider。
- 当前没有把 local tests 写成 EnterpriseRAG measured improvement；真实质量门仍留到 PHASE08 fixed paired benchmark。

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

# PHASE07 Claim-Level Citation Binder

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE07_claim-level-citation-binder
status: active
owner: Answer / Citation

## 目标

把回答生成从 paragraph-first 改为 claim-first：每个 claim 必须绑定 candidate evidence span。

## 范围

- answer -> claims。
- claim -> candidate evidence spans。
- support / contradict / insufficient verdict。
- 无证据 claim 的 rewrite / abstain / focused retrieval。

## 禁止范围

- 不硬贴 citation。
- 不把 doc-level source citation 写成 strict span citation。
- 不在证据不足时生成确定性 claim。

## 验收闸门

- `text_hit_citation_miss` 下降。
- `Citation Accuracy >= 0.30`。
- `Answer Correctness >= standard_rag baseline`。
- unsupported claims 不上升。

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

1. 审计现有 answer / citation 生成路径。
2. 增加 claim extraction / binding contract。
3. 对低 citation confidence 触发 rewrite、abstain 或 focused retrieval。
4. 更新 eval metrics 和 failure cases。

## 多 agent 分工

默认单线程，claim/citation contract 由主线程集中控制。

## 需要返回的证据

- claim -> evidence span 示例。
- citation accuracy 变化。
- unsupported claim 变化。

## 停止条件

只有 claim-level citation 在 fixed benchmark 中可测后才能关闭。

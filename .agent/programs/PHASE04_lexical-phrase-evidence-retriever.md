# PHASE04 Lexical Phrase Evidence Retriever

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE04_lexical-phrase-evidence-retriever
status: pending
owner: Retrieval

## 目标

把 BM25、phrase / normalized substring、vector、entity 和 graph neighbor 作为一等候选来源，再做 merge / RRF / rerank。

## 范围

- lexical exact evidence path。
- normalized text phrase matching。
- retriever provenance 和 failure diagnostics。

## 禁止范围

- 不为了提高分数使用 gold answer 泄漏。
- 不把 phrase hit 当成最终 answer correctness。

## 验收闸门

- strict evidence text 命中不只依赖 embedding。
- failure cases 能标出 lexical path 是否命中。
- hard negatives 下不会大量误命中相似噪声。

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

1. 找出当前 BM25 / vector / graph 候选融合点。
2. 增加 phrase candidate source。
3. 给每个 context 标记 retriever source。
4. 更新 eval diagnostics。

## 多 agent 分工

可拆 retrieval implementation 和 eval diagnostics，最后由主线程合并。

## 需要返回的证据

- retriever source 分布。
- phrase path 命中样本。
- hard negative 误命中情况。

## 停止条件

只有 lexical path 对 Evidence Text Available 产生真实可测影响后才能关闭。

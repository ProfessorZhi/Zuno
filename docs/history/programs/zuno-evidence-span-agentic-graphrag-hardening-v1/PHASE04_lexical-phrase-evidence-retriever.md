# PHASE04 Lexical Phrase Evidence Retriever

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE04_lexical-phrase-evidence-retriever
status: completed
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

- [x] strict evidence text 命中不只依赖 embedding，exact / normalized phrase 是本地候选信号。
- [x] failure bucket items 能标出 `lexical_phrase_hit`。
- [x] hard negative / punctuation / newline focused tests 覆盖 phrase path 不被关键词噪声压过。

## 完成事实

PHASE04 已完成 local deterministic lexical / phrase evidence retriever baseline，不表示 PHASE05 graph evidence lineage 或 PHASE06 evidence-aware reranker 已完成。

Current 已实现：

- `KnowledgeIndexRuntime` ranking 输出 `retriever_source`、`raw_score`、`normalized_score`、`rank`、`matched_terms`、`matched_phrase` 和 `candidate_reason`。
- Exact / normalized phrase match 作为 `normalized_phrase` 候选信号参与排序，支持常见标点、大小写、换行和版本号点号规范化。
- Agentic retrieval EvidenceItem / trace payload 保留 lexical candidate metadata。
- EnterpriseRAG paired diagnostics 在可用 trace 下输出 `lexical_phrase_hit`；缺 trace 时仍输出 unavailable，不猜测。

边界：

- 当前没有接 external lexical engine / Elasticsearch。
- 当前 phrase path 不读取 benchmark gold answer、gold evidence text 或 gold labels。
- 当前仍未完成 evidence-aware reranker 的多特征排序契约。

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

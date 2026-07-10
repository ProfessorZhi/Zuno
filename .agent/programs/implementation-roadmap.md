# Program Roadmap

state: active
active_program: zuno-evidence-span-agentic-graphrag-hardening-v1
current_phase: PHASE04_lexical-phrase-evidence-retriever.md
latest_completed_program: `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`

## 总目标

本轮 program 只解决一个核心问题：

```text
Zuno 已经能在 EnterpriseRAG paired benchmark 上看到 agentic_graphrag 的 doc-level retrieval 增益；
下一步必须把这个增益稳定转成 evidence text availability、source-span citation 和 answer correctness。
```

第一性判断：

- 如果 gold document 没召回，修 retriever / query rewrite。
- 如果 gold document 召回但 gold evidence text 没进 context，修 chunking / span index / lexical path / rerank。
- 如果 evidence text 进了 context 但 citation 没绑定，修 citation builder / claim binder。
- 如果 citation 对但答案错，修 answer synthesis / claim grounding。

## 历史完成边界

Program 3 Mega：`zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`

状态：completed / archived。

归档位置：

- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`

完成边界：输入异步基础设施、Knowledge / Retrieval / GraphRAG、Memory & Context、Capability / Skill / Tool / MCP、Security / Governance、Model Gateway / Cost、Planning & Control Runtime、Eval / Trace / Benchmark、Product API / Frontend 最小同步、E2E、文档和归档已统一收口成本地 launchable product baseline。

完成结论：

```text
Launchable enterprise Agentic GraphRAG product baseline completed.
Production scale external deployments remain replaceable targets.
```

## Program 4：Evidence-Span Agentic GraphRAG Hardening

Program ID：`zuno-evidence-span-agentic-graphrag-hardening-v1`

状态：completed。

### PHASE01：Eval Truth Source And Gap Buckets

文件：`PHASE01_eval-truth-source-and-gap-buckets.md`

状态：completed。

目标：把 EnterpriseRAG paired eval 的失败从平均分拆成四类：`doc_miss`、`doc_hit_text_miss`、`text_hit_citation_miss`、`citation_hit_answer_wrong`。先证明瓶颈在哪里，再改 runtime。

验收：metrics / report / failure cases 中能明确区分 retrieval、evidence text、citation binding 和 answer synthesis 的责任边界。

### PHASE02：Source Span Provenance Contract

文件：`PHASE02_source-span-provenance-contract.md`

状态：completed。

目标：冻结 citation 所需 provenance 字段，包括 `document_id`、`source_object_id`、`document_version_id`、`page_number`、`section_path`、`block_id`、`chunk_id`、`char_start`、`char_end`、`normalized_text`、`raw_text`、`parent_chunk_id`、`neighbor_chunk_ids`、`source_uri`、`file_name`、`content_hash`、`parser_name`、`parser_version`。

验收：新增或扩展 IR / chunk / eval fixtures 时，source span 字段不丢失，并能从 retrieval result 回到 source block。

### PHASE03：Citation-Sized Chunk Index

文件：`PHASE03_citation-sized-chunk-index.md`

状态：active。

目标：建立 small citation chunks + parent context chunks。检索可以用 parent context，citation 必须能落到更小的 evidence span。

验收：EnterpriseRAG paired eval 中 `Evidence Text Available@5` 开始可测且不为伪造值。

### PHASE04：Lexical Phrase Evidence Retriever

文件：`PHASE04_lexical-phrase-evidence-retriever.md`

状态：active。

目标：把 BM25、phrase / normalized substring、vector、entity 和 graph neighbor 作为一等候选来源，再做 RRF / rerank。

验收：strict evidence text 的命中不只依赖 embedding；failure cases 能标出 lexical path 是否命中。

### PHASE05：Entity-Chunk Bidirectional Graph Index

文件：`PHASE05_entity-chunk-bidirectional-graph-index.md`

目标：让 graph 结果必须能回落到 source chunks：`entity -> relation -> supporting_chunk_ids`、`relation -> evidence_span_ids`、`community_summary -> source_chunk_ids`、`chunk -> entities / relations`。

验收：GraphRAG 不只返回 summary 或 graph context，而能输出可引用 evidence span。

### PHASE06：Evidence-Aware Reranker

文件：`PHASE06_evidence-aware-reranker.md`

目标：rerank 不只排序 relevance，还排序 answerability、exact evidence presence、citation span quality、source authority、ACL allowed、freshness。

验收：top-k 更像 evidence bundle，而不是相关背景材料；`gold_doc_recalled_but_low_rank` 和 `graph_context_non_gold` 下降。

### PHASE07：Claim-Level Citation Binder

文件：`PHASE07_claim-level-citation-binder.md`

目标：回答先拆 claim，再把每个 claim 绑定 candidate evidence span；没有 evidence 的 claim 要 rewrite、abstain 或触发 focused retrieval。

验收：`text_hit_citation_miss` 降低，`Citation Accuracy` 达到第一阶段硬化目标。

### PHASE08：Hard Negative Eval And Release Gate

文件：`PHASE08_hard-negative-eval-and-release-gate.md`

目标：补齐 hard negative eval，覆盖同文档相邻错误 chunk、同主题不同文档、表格 vs 正文、页眉页脚、OCR 噪声、多文档冲突和 graph summary must cite source。

验收：release report 能证明 agentic_graphrag 相比 standard_rag 的收益、成本和失败边界，并能归档关闭 program。

## 全局质量闸门

```text
Evidence Text Available@5 >= 0.60
Source Doc Citation >= 0.85
Citation Accuracy >= 0.30 first hardening target
Answer Correctness >= standard_rag baseline
```

## 禁止事项

- 不把 Target 或 Future 写成 Current。
- 不把 missing dataset、blocked_not_measured 或 runtime observed 写成 measured。
- 不把 doc-level recall 提升直接等同 citation 完成。
- 不把 Codex 多线程工程执行写成 Zuno 产品 runtime 多 Agent 架构。
- 不把 deep_graphrag 冒充完整 product Agentic Runtime。

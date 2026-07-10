# Agent 执行计划

`.agent/programs/` 当前处于 active 状态。

## 当前状态

- State: active
- Active program: `zuno-evidence-span-agentic-graphrag-hardening-v1`
- Current phase: `PHASE05_entity-chunk-bidirectional-graph-index.md`
- Latest completed program: `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`

最近完成并归档的 Program 3 Mega 已完成本地可验证的 launchable enterprise Agentic GraphRAG product baseline。归档入口：

- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`

## 当前文件

- `current.md`：当前 active program、当前 phase、质量目标和 Current / Target / Future 边界。
- `implementation-roadmap.md`：本轮 evidence-span hardening 的 PHASE01-PHASE08 路线。
- `closure-checklist.md`：本轮关闭条件、质量闸门和禁止提前关闭项。
- `PHASE01_eval-truth-source-and-gap-buckets.md`：completed phase。
- `PHASE02_source-span-provenance-contract.md`：completed phase。
- `PHASE03_citation-sized-chunk-index.md`：completed phase。
- `PHASE04_lexical-phrase-evidence-retriever.md`：completed phase。
- `PHASE05_entity-chunk-bidirectional-graph-index.md`：当前 active phase。
- `PHASE06_evidence-aware-reranker.md` 到 `PHASE08_hard-negative-eval-and-release-gate.md`：后续 pending phase。
- `queued-programs/README.md`：当前没有 queued program；旧 Program 4-6 已随 Program 3 Mega 归档为 merged inputs。

## 本轮 Program 口径

```text
目标：把 Agentic GraphRAG 从 doc-level retrieval 增益推进到 evidence-span-level retrieval / citation / answer quality 增益。
不做：把 external graph DB、external vector DB、OCR / VLM、长期 metrics store 写成 Current。
不做：把 deep_graphrag 冒充完整产品 Agentic Runtime。
```

本轮质量闸门：

```text
Evidence Text Available@5 >= 0.60
Source Doc Citation >= 0.85
Citation Accuracy >= 0.30 first hardening target
Answer Correctness >= standard_rag baseline
```

## 使用规则

- active 状态下，PHASE 文件必须平铺在 `.agent/programs/` 根目录，不放入子目录。
- 每个 phase 只能在真实代码、测试、trace/eval 或 verifier 证明后关闭。
- blocked、prepared、runtime observed 或缺失数据不能写成 measured。
- completed program 的 phase、closure summary 和 merged queued inputs 必须留在 `docs/history/programs/`。
- 多线程执行必须由当前主线程先确认真实 UI 目标模式和独立 worktree / branch；提示词目标模式不等于 Codex UI 目标模式。

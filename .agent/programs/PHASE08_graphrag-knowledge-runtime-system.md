# PHASE08 GraphRAG Knowledge Runtime System

Program: `zuno-eight-deliverables-full-realization-v1`
status: planned

## 为什么

Zuno 的知识系统目标不是单一向量检索，而是 RAG、GraphRAG、local/global/drift retrieval 和 fusion/rerank 的可解释组合。GraphRAG 必须从项目叙事进入可测试 runtime 边界。

## 范围

覆盖交付物：

- 6. 完善的 Zuno 目标架构。
- 7. 清晰干净的代码和目录。
- 8. 一致性与验证系统。

主要目标：

- LLM-first entity / relation extraction contract。
- Knowledge extractor configs。
- local / global / drift retrieval。
- fusion、rerank、citation、evidence coverage。

## 执行步骤

1. 审计 `src/backend/zuno/knowledge`、GraphRAG services 和 legacy query path。
2. 固定 extraction config、graph snapshot、retrieval result 和 citation contract。
3. 实现或收口 local/global/drift query path 与 fusion policy。
4. 将 GraphRAG result 接入 Context Pack 和 trace。
5. 增加 eval/focused tests，证明不同 query_method 的输出和证据边界。

## 验收

- GraphRAG 不再只是 docs 目标，有可测试 contract。
- local/global/drift 的边界和 fallback 可解释。
- fusion/rerank 不破坏 citation coverage。
- 旧兼容入口继续可用。

## PR 边界

建议拆成 extraction/config PR、retrieval/fusion PR、trace/eval PR。

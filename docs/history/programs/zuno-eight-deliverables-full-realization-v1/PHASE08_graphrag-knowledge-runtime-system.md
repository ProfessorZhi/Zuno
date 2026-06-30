# PHASE08 GraphRAG Knowledge Runtime System

Program: `zuno-eight-deliverables-full-realization-v1`
status: completed

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

## 完成证据

- `GraphRAGExtractorConfig` 已进入 GraphRAG contract，表达 LLM-first extractor config、rule fallback、model / prompt / schema / policy / eval refs。
- `KnowledgeQueryService.build_project_snapshot()` 会把现有 `knowledge_config` JSON 转成 `GraphRAGProjectSnapshot.extractor_config`，不新增 DB schema。
- `GraphRAGQueryService` / `RetrievalOrchestrator` trace metadata 已暴露 `query_method_contract`、`citation_contract` 和 `retrieval_fusion_contract`。
- 显式 `global` 当前走 `community_global`，不与 vector / BM25 chunk-level retrievers 扁平混榜；缺少 chunk/span grounding 时 citation contract 保持 `missing`。
- `GeneralAgent` 知识库工具返回文本会暴露 query method contract，旧 `zuno.services.*` import path 由 legacy guard 证明继续可用。
- PHASE08 focused tests 已覆盖 extractor config、snapshot propagation、query / citation / fusion trace contract、GeneralAgent 文本桥、API config preservation、facade surface 和 legacy import path。
- Contract Review eval comparison 已运行 `dev_offline,dev_local,demo` 三 profile，输出均为 `status=ok`；structured profiles 证明本地 GraphRAG Project extraction / retrieval path 能产生更多 graph path，不依赖外部 API。
- 仍在 Target：生产级 schema-constrained LLM extraction、完整 RRF/rerank 治理、多套 extractor orchestration、DB schema 迁移和前端 trace 面板。
- 未作为完成证据：`tools/evals/zuno/rag_eval` 的 contract-review stackless matrix 需要未跟踪的 `.local/evals/zuno/rag_eval/corpus/contract_review/manifest.json`，real-runtime multihop runner 在当前机器的本地模型 registry / embedding 初始化层超时；二者不写成 Current。

## PR 边界

本 PR 合并 extraction/config、retrieval/fusion、trace/eval 三个互相独立切片，由主线程统一审查和验证。

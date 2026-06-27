# Phase 07：GraphRAG LLM 实体抽取与知识检索融合

## 目标

围绕现有 `KnowledgeQueryService` 和 `GraphRAGQueryService` 落地目标检索融合路径，并把 GraphRAG 建图的实体抽取主路径从规则/正则提升为 LLM 抽取。

## 核心原则

GraphRAG 的实体是语义节点，不是普通关键词。LLM 抽取是默认主路径；规则、正则和词典只能作为确定格式辅助、预处理、fallback 或测试 baseline。

## 范围

- `graph_index_settings.entity_extraction_mode` 默认目标为 `llm`。
- 知识库配置支持选择 `model_refs.entity_extraction_llm_id`，用于 GraphRAG 实体和关系抽取。
- LLM 抽取输出 schema-constrained JSON，包括 entity、entity type、relation、source chunk/span、confidence 和 trace。
- 规则/正则只辅助日期、金额、条款号等确定格式，不作为 GraphRAG entity discovery 主路径。
- query method requested / resolved trace。
- Basic、Local、Global、DRIFT 路由边界。
- Native BM25、dense vector、graph local、community global 的候选融合。
- RRF、dedup、optional rerank、evidence check、citation coverage。
- `GraphRAGProjectSnapshot` 继续是内部查询配置，不变成 Agent memory。

## 不在范围内

- 重新引入 Domain Pack 作为主线。
- 新建第二套聊天 runtime。
- 大规模重新跑正式 eval，除非该 phase 明确要求。
- 在没有用户选择或默认模型配置时强制调用外部 LLM。

## 退出标准

- 知识库配置能表达“使用某个 LLM 抽取 GraphRAG 实体”。
- GraphRAG 建图 trace 能说明 entity extraction mode、LLM id、prompt version、schema version、fallback reason 和 evidence span。
- query method resolution 可追踪。
- GraphRAG 是被选择的 Knowledge Capability，不是第二套聊天运行时。
- evidence bundle、citation coverage、index/community/prompt versions 进入 trace。

## 验证

- 聚焦 GraphRAG entity extraction config / schema 测试。
- 聚焦 retrieval/fusion 测试。
- 需要时运行 stackless 或 eval smoke。
- 文档边界验证。

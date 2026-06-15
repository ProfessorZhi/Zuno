# Retrieval Orchestrator

## 目标

把当前分散在 `rag`、`graphrag` 和兼容逻辑里的知识检索流程，收束成一个统一的检索编排层。

第一阶段目标不是追求最强效果，而是先建立一个：

- 清楚
- 可扩展
- 可评测
- 可解释
- 可追踪

的检索控制面。

## 核心问题

当前仓库已经有：

- Milvus 向量检索
- Elasticsearch 关键词检索
- Neo4j GraphRAG 检索
- `rag / graphrag / hybrid / auto` 模式

真正缺的不是某一路检索，而是：

```text
系统如何决定何时调用哪一路，
如何融合，
如何重试，
如何解释结果质量和失败原因。
```

## 设计原则

### Single Control Plane

所有知识检索请求都必须经过统一 orchestrator。

### Retriever Only Retrieves

各路 retriever 只负责召回，不负责决策和最终上下文排序。

### Policy Outside Backends

`auto / rag / graphrag / hybrid` 的差异由 planner 决定，不写死在具体后端。

### Unified Trace

每次检索都必须留下结构化 trace，至少能回答：

- 原 query 是什么
- 是否做了 rewrite
- 调用了哪几路召回
- 每路回来了多少结果
- 哪些结果被融合、降权或丢弃
- 最终上下文是什么

## 目标结构

```text
Query
  -> QueryProcessor
  -> RetrievalPlanner
  -> Retriever Adapters
  -> RetrievalFusion
  -> Final Context + Trace
```

## 组件职责

### `RetrievalOrchestrator`

统一入口，负责一次检索请求从开始到结束的完整调度。

职责：

- 创建 retrieval session / trace
- 调用 query processor
- 调用 planner
- 调度各路 retriever
- 调用 fusion
- 产出最终结果与 trace metadata

### `QueryProcessor`

负责 query 标准化与扩写。

职责：

- normalize
- rewrite
- feature detection
- 关系型 / 关键词型 / 语义型问题初步判断

输出是结构化 `ProcessedQuery`，不是最终结果。

### `RetrievalPlanner`

负责根据：

- 用户请求模式
- query 特征
- knowledge 能力
- 当前可用后端

生成检索计划。

它决定：

- resolved mode
- enabled retrievers
- fallback 策略
- query rewrite 是否参与

### Retriever Adapters

第一版建议保留三路：

- vector retriever
- keyword retriever
- graph retriever

它们都输出统一结果模型。

### `RetrievalFusion`

负责融合多路召回结果，统一排序和去重。

职责：

- 文档合并
- 分数归一化
- 多路来源标记
- 重复 chunk 合并
- 最终 top-k 选择

## 模式语义

面试前，对用户层不直接暴露大量技术名，而是只保留两种检索模式：

### 普通模式

- `BM25 + Dense RAG`
- 适合默认问答、低成本场景

### 增强模式

- `Conditional Requery + BM25 + Dense RAG + Local GraphRAG + Fusion + Rerank + Citation Check + Grounding`
- 适合关系型、跨条款、强引用、高质量场景

这里要明确：

```text
当前增强模式里的 GraphRAG = Local GraphRAG
```

不是“社区摘要 + 全局图总结”整包全开。

用户只选普通 / 增强两档，底层由 planner 决定这次具体启用哪些能力。

## GraphRAG 分层语义

### Local GraphRAG

Local GraphRAG 负责：

```text
Query
  -> Query Analyze
  -> Entity Linking
  -> Vector + BM25
  -> Local Graph Path Retrieval
  -> Chunk Hydration
  -> Fusion
  -> Rerank
  -> Evidence Check
  -> Answer with Citation
```

它解决的问题是：

- 谁负责
- 什么条件触发风险
- 哪个条款支持结论
- 哪条关系路径把问题带回原文证据

### Community GraphRAG

Community GraphRAG 负责：

```text
Entity / Relation Graph
  -> Community Detection
  -> Community Reports
  -> Global Search
  -> Map-Reduce Summary
```

它解决的问题是：

- 这批知识整体有哪些主题
- 风险主要聚在哪些社区
- 某类问题在全库里呈现什么趋势

### DRIFT-like Hybrid

更后期的混合路线是：

```text
Community Report
  -> choose theme region
  -> Local Graph Search
  -> hydrate chunk evidence
  -> final answer
```

也就是：

```text
global overview + local deep dive
```

### 分层关系

必须在编排层写清楚：

```text
Local 和 Community 共用同一张实体关系图。
Local 不依赖 Community。
Community 建立在已经成形的实体关系图上。
```

因此现阶段 planner 的顺序应是：

1. 标准 RAG
2. Local GraphRAG
3. Community GraphRAG
4. DRIFT-like hybrid

### `rag`

- 主路径：vector
- 可选：keyword fallback

### `graphrag`

- 当前应解释为 `Local GraphRAG`
- 主路径：vector + graph
- vector 用于图谱入口 chunk

### `hybrid`

- 当前主路径：vector + keyword + Local GraphRAG
- 后续可扩展为 `Community overview + Local deep dive`

### `auto`

不是一种后端，而是一种 planner 决策模式。

## 与 Domain Pack 的关系

Retrieval Orchestrator 是通用控制面，但它必须能被 Domain Pack 影响：

- query strategy
- graph hop limit
- path preference
- rerank policy
- citation strictness

也就是说：

```text
orchestrator 是通用骨架，
Domain Pack 决定部分检索策略参数。
```

并且对增强模式，Domain Pack 应能影响：

- requery 触发条件
- graph hop / path preference
- 风险导向 relation preference
- citation strictness
- grounding strictness

## 第一阶段边界

第一阶段不要求：

- 学习排序
- 复杂在线 bandit
- 新增外部 Web / SQL 检索源
- 大规模多 query planner

第一阶段只要求：

- 有统一入口
- 有 planner
- 有统一结果模型
- 有 trace
- 有 fallback
- 能为 LangGraph 主流程提供稳定上下文

面试前在这份文档上额外要求：

- 普通 / 增强两档体验明确
- 增强模式下允许启用完整高质量能力包
- 不把底层技术选项直接暴露给用户

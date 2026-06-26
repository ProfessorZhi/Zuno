# Zuno Retrieval Orchestrator Design

## Goal

把当前分散在 `rag`、`graphrag` 和若干兼容逻辑里的检索流程，重构成一个更接近正式 RAG 系统的统一检索编排层。

第一版目标不是追求最强效果，而是先建立清楚、可扩展、可评测、可解释的系统骨架，使项目可以名正言顺地具备：

- query 预处理
- 检索规划
- 多路召回
- 融合排序
- rerank
- trace 回放

## Why This Change

当前仓库里已经存在：

- Milvus 向量检索
- Elasticsearch 关键词检索
- Neo4j GraphRAG 检索
- `rag / graphrag / hybrid / auto` 查询模式

但这些能力还没有形成统一的“检索控制面”。

主要问题不是“有没有某一路检索”，而是“系统如何决定何时调用哪一路、如何融合、如何解释失败原因”。

如果继续沿用当前模式，项目会更像：

- 一套传统 RAG 逻辑
- 一套 GraphRAG 逻辑
- 外层再补一些兼容分支

而不是一个完整的检索系统。

这次重构的第一性目标是：

- 让 Zuno 的知识检索层更完整，更像正式 RAG 系统
- 让 `RAG / GraphRAG / hybrid / auto` 成为统一编排策略的不同结果，而不是多套散落实现

## Scope

这份设计定义：

- 统一检索编排入口
- query 处理、检索规划、召回、融合、rerank、trace 的职责边界
- 多路召回的统一数据模型
- 第一版落地范围与非目标
- 与当前 `rag` / `graphrag` 代码的迁移关系

这份设计不定义：

- LLM answer generation prompt
- 前端最终交互样式
- 离线训练式学习排序
- 新增外部 Web/Search/SQL 召回源

## Design Principles

### Single Control Plane

所有知识检索请求都必须经过一个统一 orchestrator，不允许某一路检索在调用方侧直接拼接结果后绕过编排层。

### Retriever Only Retrieves

每一路 retriever 只负责召回，不负责决定查询策略，也不负责最终上下文排序。

### Policy Outside Backends

`auto / rag / graphrag / hybrid` 的差异由 planner 决定，不写死在具体后端里。

### Unified Trace

每次检索都必须留下结构化 trace，能回答：

- 原 query 是什么
- 改写成了什么
- 调用了哪几路召回
- 每路召回回来了多少
- 哪些结果被融合、降权、丢弃
- 最终上下文是什么

### Incremental Migration

第一版允许复用现有 Milvus、Elasticsearch、Neo4j 能力，不要求重写底层存储与索引逻辑。

## Architecture

### `RetrievalOrchestrator`

统一入口，负责一次检索请求从开始到结束的完整调度。

职责：

- 创建 retrieval session / trace id
- 调用 query processor
- 调用 retrieval planner
- 并行调度各路 retriever
- 调用融合与 rerank
- 产出最终上下文与 retrieval trace

它不直接关心 Milvus、Elasticsearch、Neo4j 的内部细节。

### `QueryProcessor`

负责 query 的标准化与扩写。

职责：

- query normalize
- query rewrite
- query feature detection
- relation-style / keyword-style / semantic-style 问题初步判断
- 为 planner 产出结构化 query 信息

输出是 `ProcessedQuery`，不是最终检索结果。

### `RetrievalPlanner`

负责把用户请求、知识库能力、query 特征转成一份明确的检索计划。

职责：

- 根据 mode 选择启用哪些 retriever
- 为每路分配 `top_k`
- 决定是否开启 keyword recall
- 决定是否开启 graph recall
- 决定是否需要 query rewrite retry
- 决定 fallback / refill 策略
- 决定是否调用 rerank

它是这次重构里最关键的控制面。

### `BaseRetriever`

统一召回器接口。

第一版至少包含：

- `VectorRetriever`
- `KeywordRetriever`
- `GraphRetriever`

未来可扩展：

- `WebRetriever`
- `SQLRetriever`
- `MemoryRetriever`

### `FusionAndRerank`

负责把多路召回结果变成最终上下文候选。

职责：

- 标准化各路分数
- 对相同 chunk 去重
- 聚合同 chunk 多路命中证据
- 应用融合策略
- 进行 rerank
- 截断最终上下文

### `RetrievalTraceBuilder`

负责把整次 retrieval session 的关键信息写成结构化 trace，供：

- SSE / 调试输出
- 离线评测
- LangSmith / Langfuse / 本地日志
- 失败回放

## Core Data Models

### `RetrievalRequest`

建议字段：

- `query`
- `knowledge_ids`
- `mode`
- `top_k`
- `score_threshold`
- `rerank_enabled`
- `rerank_top_k`
- `graph_hop_limit`
- `max_paths_per_entity`
- `needs_query_rewrite`
- `trace_enabled`

### `ProcessedQuery`

建议字段：

- `original_query`
- `normalized_query`
- `rewritten_queries`
- `intent_labels`
- `query_features`
- `route_hints`

### `RetrievalPlan`

建议字段：

- `requested_mode`
- `resolved_mode`
- `enabled_retrievers`
- `retriever_configs`
- `fusion_policy`
- `rerank_policy`
- `fallback_policy`
- `trace_policy`

### `RetrievedDocument`

统一的多路召回结果模型。

建议字段：

- `chunk_id`
- `knowledge_id`
- `file_id`
- `file_name`
- `content`
- `summary`
- `score`
- `normalized_score`
- `source_type`
- `source_backend`
- `retrieval_reason`
- `metadata`

这里的 `source_type` 用来区分：

- `vector`
- `keyword`
- `graph`

`source_backend` 用来区分具体实现：

- `milvus`
- `elasticsearch`
- `neo4j`

### `FusionResult`

建议字段：

- `documents`
- `dropped_documents`
- `fusion_metadata`
- `rerank_metadata`

### `RetrievalTrace`

建议字段：

- `trace_id`
- `request`
- `processed_query`
- `plan`
- `retriever_runs`
- `fusion_summary`
- `rerank_summary`
- `final_context`
- `failure_reason`

## Query Lifecycle

一次完整检索请求的数据流如下：

```text
RetrievalRequest
-> RetrievalOrchestrator
-> QueryProcessor
-> RetrievalPlanner
-> VectorRetriever / KeywordRetriever / GraphRetriever (parallel)
-> FusionAndRerank
-> RetrievalTraceBuilder
-> final context
```

### Step 1: Request Intake

orchestrator 接收请求，创建：

- `trace_id`
- `request_started_at`
- 初始 trace record

### Step 2: Query Processing

`QueryProcessor` 负责：

- 去除噪声空白
- 保留原 query
- 产出 rewrite variants
- 识别是否是偏关系型问题
- 识别是否更适合 keyword precision

第一版不追求复杂分类器，只做轻量规则 + 现有 query rewrite 能力复用。

### Step 3: Retrieval Planning

`RetrievalPlanner` 根据：

- 用户指定 mode
- knowledge base 的索引能力
- query features
- 系统默认策略

生成 `RetrievalPlan`。

第一版建议规则：

- `rag` -> 启用 `VectorRetriever`，可选 `KeywordRetriever`
- `graphrag` -> 启用 `VectorRetriever` + `GraphRetriever`
- `hybrid` -> 启用 `VectorRetriever` + `KeywordRetriever` + `GraphRetriever`
- `auto` -> planner 根据 query 特征和知识库能力解析成以上之一

### Step 4: Multi-Retriever Execution

各 retriever 并行执行。

统一约束：

- retriever 只返回自身命中
- retriever 不做最终跨路排序
- retriever 可以返回局部分数与局部解释

#### `VectorRetriever`

职责：

- 走 Milvus 向量召回
- 兼容文本 embedding 与现有图文检索入口

#### `KeywordRetriever`

职责：

- 走 Elasticsearch 关键词全文检索
- 适合精确术语、英文专有名词、配置项、参数名

#### `GraphRetriever`

职责：

- 使用 query 或 RAG entry chunks 提取 graph seeds
- 在 Neo4j 做 1-hop / 2-hop 关系扩展
- 返回图谱命中的路径证据，并尽可能回链到 chunk

### Step 5: Fusion

融合层处理：

- score normalize
- exact chunk dedupe
- same chunk 多路证据聚合
- query-aware 排序

第一版不引入训练式排序，建议先做规则化融合。

推荐的第一版融合策略：

- 相同 `chunk_id` 合并为一条
- 保留 `matched_by=["vector", "keyword"]` 这类来源证据
- 多路命中的 chunk 获得额外加分
- graph 命中优先提升“关系型问题”的相关 chunk

### Step 6: Rerank

融合后再做统一 rerank，而不是让各路召回器分别 rerank。

这样做的原因：

- 便于统一比较不同来源候选
- 便于保留跨路排序证据
- 便于 trace 中解释为什么最终排序发生变化

### Step 7: Fallback / Retry

如果结果不足，planner 允许按策略补检。

第一版允许：

- query rewrite retry
- widen top_k
- `rag -> hybrid`
- `graphrag -> hybrid`

第一版不做过多动态策略学习。

### Step 8: Trace Finalization

产出最终 `RetrievalTrace`，记录：

- 计划与实际执行路径
- 每路召回数
- 融合前后文档变化
- 被丢弃原因
- 最终上下文

## Mode Semantics After Refactor

重构后应统一收敛成“planner 语义”，不再让 mode 只是历史兼容 if-else 名字。

### `rag`

- 标准语义检索主路径
- 以向量召回为主
- 可选关键词补充，但不默认暴露为用户理解负担

### `graphrag`

- 关系问题优先
- 仍允许 RAG 作为图谱入口来源
- 不是纯图谱检索空跑

### `hybrid`

- 多路召回全开
- 由 orchestrator 统一融合

### `auto`

- planner 根据 query features 和 knowledge capability 自动解析
- 是策略模式，不是单独的一套实现

## Migration Strategy

### Reuse

第一版直接复用：

- `services/rag` 中现有 Milvus / rerank 能力
- `services/rag/es_client.py`
- `services/graphrag` 中现有 Neo4j / graph retrieve 能力

### Refactor

需要拆分和迁移的重点：

- 把 mode 判断从 `rag.handler`、`graphrag.orchestrator` 里逐步上提到统一 planner
- 把多路结果格式统一成 `RetrievedDocument`
- 把融合排序逻辑从零散 helper 收进单独模块
- 把 trace 输出从 ad-hoc metadata 统一成结构化对象

### Compatibility

第一版应尽量保证：

- 现有 API 请求参数仍可用
- 现有 workspace 请求入口不需要大改调用方式
- 前端已有 mode 选项可继续工作

但内部不再允许调用方直接拼接 RAG / GraphRAG 结果。

## Implementation Scope For V1

第一版必须完成：

- 新建统一 orchestrator 主线
- 新建 retriever 接口与三路实现适配器
- 新建 planner
- 新建 fusion / rerank 层
- 新建 retrieval trace 数据结构
- 让现有 workspace 知识检索入口统一走新主线
- 为 `rag / graphrag / hybrid / auto` 补测试

第一版不做：

- 学习式路由
- 学习式融合
- 在线反馈驱动权重调参
- 新增新的外部召回源
- 复杂 UI 配置重做

## Testing Strategy

### Unit Tests

需要覆盖：

- planner 对不同 mode 和 query feature 的决策
- retriever 结果标准化
- fusion 去重与多路加权
- fallback / retry 计划
- trace 输出字段完整性

### Integration Tests

至少覆盖：

- `rag` 请求只走向量主路径
- `graphrag` 请求会使用 graph path
- `hybrid` 请求会合并多路结果
- `auto` 请求会根据 query 解析 mode
- query rewrite retry 会反映到 trace

### Regression Tests

当前已有 `graphrag` 与 `rag_eval` 相关测试应保留，并逐步迁移到新 orchestrator 语义。

## Acceptance Criteria

- 所有知识检索主入口都经过统一 orchestrator
- 三路召回使用统一接口
- 融合与 rerank 脱离具体 retriever
- `auto / rag / graphrag / hybrid` 由 planner 解释
- trace 能完整解释一次检索过程
- 保持现有 API 基本兼容

## Risks

- 当前仓库已存在 `rag` 与 `graphrag` 的交叉逻辑，迁移时容易出现双重编排
- 如果兼容层保留过厚，最终可能只是“包了一层”，而不是完成真正收敛
- 如果 trace 只记录结果不记录决策过程，后续评测价值会大幅下降
- 如果 fusion 层过早做复杂策略，会拖慢第一版落地

## Recommended First Slice

实现顺序建议是：

1. 先抽统一数据模型
2. 再抽 planner
3. 再接入三路 retriever 适配器
4. 再抽 fusion / rerank
5. 最后把 workspace 主路径切到新 orchestrator

这样可以先把“系统骨架”做出来，再替换老逻辑，而不是一次性大爆改。

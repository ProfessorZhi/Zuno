# Domain Pack + LangGraph + GraphRAG Architecture

## 目标

这份文档描述 Zuno 这一轮核心架构目标：

```text
让领域 schema、图谱抽取、混合检索、回答生成、评估和成本控制
作为可插拔能力接入统一 LangGraph Runtime。
```

## 核心原则

1. 在现有 Zuno 资产上做收束，不推倒重写。
2. Domain Pack 负责领域变化部分。
3. LangGraph 负责统一编排。
4. GraphRAG 是 Agent 可调用的图增强检索层，不是某一个业务场景的写死插件。
5. 开发流程必须支持低成本离线模式。
6. 面试前要把 Local GraphRAG 做成完整主线，而不是一次性 demo。

## 三层结构

```text
Runtime Layer
  - LangGraph workflow
  - state / checkpoint / trace / permissions

Retrieval Layer
  - vector retrieval
  - graph retrieval
  - retrieval planner / orchestrator / fusion

Domain Layer
  - domain_pack metadata
  - schema
  - extraction prompt
  - retrieval policy
  - answer template
  - report template
  - eval dataset
```

## 统一接线点

推荐接线方式：

1. `knowledge` 绑定可选 `domain_pack_id`
2. `agent` 声明默认 `domain_pack_id`
3. 对话层保留未来动态切换能力

原因：

- schema 首先依赖知识材料
- agent 可以有默认领域
- 多知识库场景需要按 knowledge 维度切 pack

## Domain Pack 运行责任

Domain Pack 必须参与以下运行时决策：

- 图谱抽取 schema
- relation 白名单
- retrieval policy
- answer template
- report template
- eval dataset
- graph update policy

## Domain QA Workflow

```text
START
  -> load_agent_config
  -> resolve_domain_pack
  -> route_intent
  -> rewrite_query
  -> vector_retrieve
  -> entity_link
  -> graph_retrieve
  -> merge_context
  -> maybe_call_tool
  -> generate_answer
  -> citation_check
  -> END
```

这里的要求不是“项目里引用了 LangGraph”，而是：

- `rewrite_query / retrieve / graph_retrieve / citation_check` 是正式节点
- GraphRAG 进入主流程，不是临时补丁
- citation_check 是正式收口节点，不是答案后的随手检查

## GraphRAG 分层模型

一句话口径：

```text
Local GraphRAG 是“沿实体关系找证据”，
Community GraphRAG 是“把实体关系聚成主题社区，再做全局总结”。
```

它们不是两个互斥方案，而是同一张知识图谱上的两层能力：

```text
原始文档
  -> chunk
  -> 抽实体 / 关系 / 证据
  -> 构建知识图谱
        |
        |-- Local GraphRAG：从问题实体出发，沿图谱找路径和原文证据
        |
        |-- Community GraphRAG：对整张图做社区检测，生成社区摘要，用于全局总结
```

这里必须明确：

```text
Local 和 Community 共用同一张实体关系图。
Local 可以独立存在。
Community 建立在已经成形的实体关系图之上。
```

换句话说，GraphRAG 不是“合同审查模式”。
它是 Agent 平台里的图检索能力层，具体场景只通过 Domain Pack 影响 schema、relation preference 和 evidence policy。

## Local GraphRAG 主线

当前主线必须写成：

```text
问题
  -> 实体链接
  -> 图路径检索
  -> chunk 回链
  -> evidence bundle
  -> citation verified answer
```

Local GraphRAG 解决的是：

- 谁负责
- 什么条件触发责任
- 哪个条款支持结论
- A 和 B 有什么关系
- 关系路径最终回到了哪些原文 chunk

所以当前 GraphRAG 主线关心的是：

- 实体
- 关系
- 路径
- 证据 chunk
- 引用

## Community GraphRAG 后续层

Community GraphRAG 不是当前默认检索主线。
它是 Local GraphRAG 之后的更高层索引能力：

```text
实体关系图
  -> 社区检测
  -> community report
  -> global search
  -> map-reduce summary
```

它适合回答的是：

- 这批知识整体有哪些高频主题
- 哪类风险最集中
- 全局上有哪些趋势
- 某个知识库整体覆盖了哪些主题区域

所以它关心的是：

- 社区
- 主题
- 全局摘要
- 趋势
- 分布

## DRIFT-like Hybrid 后续层

更后期的混合路线可以写成：

```text
Community report
  -> 找到相关主题区域
  -> 进入实体关系图
  -> Local search
  -> 回链 chunk
```

也就是：

```text
global overview + local deep dive
```

这类能力应被描述成 `DRIFT-like` 或 `hybrid graph search`，而不是当前默认模式。

## GraphRAG 目标形态

从：

```text
regex entity -> generic relation -> neighbor query
```

升级到：

```text
domain schema
  -> structured extraction
  -> incremental graph update
  -> entity resolution
  -> typed graph writing
  -> Local GraphRAG retrieval
  -> evidence bundle
  -> citation verified answer
```

## 面试前必须成立的 GraphRAG 能力

面试前，Local GraphRAG 至少要形成下面这条完整链路：

- 合同审查领域 schema
- 结构化实体 / 关系抽取
- 实体归一化
- evidence back-link
- Local GraphRAG 路径检索
- 向量检索 + 图路径证据融合
- 基于 `document_hash / chunk_hash` 的增量更新
- `index_version / status=active` 查询过滤
- 本地评测可证明价值

如果缺少动态更新和版本过滤，这条主线不能算完整。

## 当前与后续能力顺序

正式顺序应写成：

```text
Level 1：Local GraphRAG
  实体关系路径 + chunk 证据回链
  当前主线

Level 2：Community GraphRAG
  社区检测 + 社区摘要 + Global Search
  后续增强

Level 3：DRIFT-like Search
  community overview + local deep dive
  更后期能力
```

## 用户可见的检索模式

面试前，对用户层只保留两种模式：

### 普通模式

- `BM25 + Dense RAG`

### 增强模式

- `Conditional Requery + BM25 + Dense RAG + Local GraphRAG + Fusion + Rerank + Citation Check + Grounding`

增强模式不是“完整微软 GraphRAG”的同义词。
它在当前阶段应被定义为：

```text
ReQuery + Vector + BM25 + Local GraphRAG + Fusion + Rerank + Evidence Check
```

后续如果加入 Community GraphRAG，对外也应另写成：

```text
全局模式 = Community Report + Map-Reduce Global Search
```

不要把当前增强模式和后续社区模式混成一档。

## 目录目标

```text
src/backend/agentchat/
  core/graphs/
  core/runtime/
  services/domain_pack/
  services/graphrag/
  services/llm/
  services/embedding/
  domain_packs/
```

## 开发配置目标

```text
dev_offline
  - fake embedding
  - mock graph extraction
  - mock answer

dev_local
  - local embedding
  - mock extraction
  - real retrieval path

demo
  - real embedding
  - real extraction
  - traced evaluation
```

## 不在本阶段解决的问题

- 多 Agent 生产化
- 大规模 UI 改版
- 先于能力落地的包名重构

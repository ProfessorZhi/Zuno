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
4. GraphRAG 负责领域知识路径。
5. 开发流程必须支持低成本离线模式。
6. 面试前要把 GraphRAG 做成完整主线，而不是一次性 demo。

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
  -> vector + graph hybrid retrieval
  -> evidence bundle
  -> citation verified answer
```

## 面试前必须成立的 GraphRAG 能力

面试前，GraphRAG 至少要形成下面这条完整链路：

- 合同审查领域 schema
- 结构化实体 / 关系抽取
- 实体归一化
- evidence back-link
- 向量检索 + 图谱检索混合
- 基于 `document_hash / chunk_hash` 的增量更新
- `index_version / status=active` 查询过滤
- 本地评测可证明价值

如果缺少动态更新和版本过滤，这条主线不能算完整。

## 用户可见的检索模式

面试前，对用户层只保留两种模式：

### 普通模式

- `BM25 + Dense RAG`

### 增强模式

- `Conditional Requery + BM25 + Dense RAG + GraphRAG + Rerank + Citation Check + Grounding`

增强模式不是写死流程，而是允许 orchestrator 在高质量预算下启用完整能力包。

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

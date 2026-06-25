# Platform Evolution And Future Direction

## 目标

这份文档回答两个问题：

1. Zuno 当前架构的合理定位是什么
2. 在不破坏当前主线的前提下，后面应该沿哪些方向演进

它不是某个单点模块的 spec，而是整个项目的中长期架构方向说明。

## 当前定位

Zuno 当前更合理的定位不是：

- 单纯的智能问答平台
- 一开始就完全对标 Claude Code / Codex 的专业编码 Agent
- 已经完成拆分的微服务平台

更准确的定位是：

```text
本地优先的 Agent 工作台
  支持用户通过模型、Prompt、知识库、GraphRAG Project、MCP、Skills 和 Tools
  搭建具备领域问答、工具调用和任务执行能力的 Agent
```

当前阶段最重要的主线能力是：

- LangGraph runtime
- RAG / GraphRAG / BM25 检索
- GraphRAG Project 领域知识建模
- 证据、引用、评测、成本控制
- 清楚的目录结构与分层边界

## 当前架构主线

当前最应该继续做强的不是“到处扩功能”，而是下面这条主线：

```text
Frontend
  -> Backend API
  -> LangGraph runtime
  -> Retrieval Orchestrator
  -> GraphRAG Project / query policy
  -> RAG / GraphRAG / BM25
  -> Evaluation / Trace / Citation / Cost control
```

这条主线成立后：

- 合同审查能成为高质量示范场景
- 其他领域问答可以复用同一套骨架
- 多 Agent、云原生、异语言后端扩展才有稳定挂载点

## 分阶段目标

这份文档不只回答“未来想做什么”，还要回答“当前该做到什么程度才算架构成立”。

### 当前阶段

当前阶段的目标不是追求功能数量，而是先把主线骨架立住：

- Zuno 明确定位为本地优先 Agent 工作台
- LangGraph 成为运行时主线
- Retrieval Orchestrator 成为知识检索控制面
- RAG / GraphRAG / BM25 主线成立
- GraphRAG Project 成为领域知识与 query policy 的目标容器
- 本地评测、trace、citation、成本控制进入架构主线
- 文件夹结构、文档入口、后端分层开始清晰

### 下一步阶段

下一步不是再平行加新系统，而是继续补治理层和边界：

- profile / planner / RetrievalPlan / trace contract 更明确
- GraphRAG Project、query policy 与 retrieval planner 的领域边界更清楚
- GraphRAG 动态更新与图谱版本治理明确落地
- 用户层检索模式收成普通 / 增强两档
- 文档系统、目录系统、公开说明进一步收口
- 后端分层继续从“有意图”走向“真正稳定”

### 面试前目标

面试前，Zuno 至少要达到下面这个架构完成度：

- 运行时不是简单 LangChain agent，而是明确依赖 LangGraph workflow
- RAG / GraphRAG 主线完整，且能通过本地评测证明价值
- GraphRAG 具备基于 `document_hash / chunk_hash` 的增量更新能力
- 检索模式对外只保留普通模式 / 增强模式两档
- 合同审查领域建模形成真实示范，而不是空壳概念
- 架构可扩展、可修改，不把关键能力写死
- 项目目录和文件夹结构清楚，不乱放文件
- 文档、目录、README、GitHub 展示面清楚专业

一句话说，面试前要做到的是：

```text
这不是一个“能跑的 demo”，
而是一套主线清晰、边界明确、可继续演进的 Agent 工作台架构。
```

### 面试后继续优化

面试后再继续推进更长周期的工作：

- 更完整的多 Agent runtime
- 更强的企业级检索治理
- 更严格的 grounding / citation contract
- 更完整的索引生命周期与治理
- 微服务 / 云原生演进
- 异语言后端接入
- 更强的编程 Agent / 代码工作台能力

## 三条长期演进方向

### 1. 企业级检索治理

这是最靠近当前主线、也是最该优先补强的方向。

目标不是“再多接几路检索”，而是把已有能力升级成：

- 可解释
- 可审计
- 可降级
- 可评测
- 可控成本
- 可治理索引生命周期

核心边界已经由这些文档承担：

- `retrieval-orchestrator.md`
- `enterprise-retrieval-governance.md`
- `rag-evaluation-and-observability.md`

当前应坚持的原则：

- `profile` 是策略边界，不是固定 DAG
- `planner` 按单次请求生成 plan
- `GraphRAG` 受 GraphRAG Project / query policy 控制
- citation 走 evidence-first 路线
- scope、budget、fallback、index version 是硬约束

### 2. 多 Agent 演进

多 Agent 是未来方向，但不是当前第一优先级。

当前最合理的形态仍然是：

```text
单主 Agent + LangGraph workflow
```

后面可以逐步演进到：

```text
Supervisor Agent
  -> Retrieval specialist
  -> Graph specialist
  -> Citation specialist
  -> Report specialist
```

多 Agent 的价值不在于“名字更多”，而在于：

- 职责隔离
- 上下文隔离
- 权限隔离
- 工具隔离
- 失败隔离
- 并行空间

因此未来推进时，应坚持：

- 共享知识底座，不重复建 RAG
- 子 Agent 权限只能缩小，不能扩大
- handoff 必须是显式状态，不是隐式 prompt 文本

### 3. 平台工程化演进

Zuno 未来需要保留往下面两类方向演进的可能：

- 微服务 / 云原生
- 接入其他语言的业务后端，例如 Java

但这不意味着现在就要把单体拆碎。

当前更正确的做法是：

- 先把单仓结构和分层边界理顺
- 让控制层、服务层、DAO 层、基础设施层职责清楚
- 保证未来可以把部分服务抽离出去

这类边界由 [Layered Backend And Service Evolution](layered-backend-and-service-evolution.md) 负责定义。

## 后端分层原则

后端默认采用四层视角：

1. 控制层
2. 服务层
3. DAO 层
4. 基础设施层

它的意义不是追求“教科书分层”，而是为了让下面几件事成立：

- 控制层保持薄
- 业务语义留在服务层
- 数据访问不要污染 workflow
- Redis、队列、对象存储、向量库、图数据库等 provider 逻辑保持隔离

这能同时服务当前单体开发和未来服务拆分。

## 面向未来的边界要求

如果未来要继续演进，这些边界必须尽量稳定：

- retrieval contract
- evidence / citation contract
- GraphRAG Project / query policy contract
- runtime state contract
- service / DAO contract
- publish-safe repository boundary

也就是说，未来可以替换实现，但不要轻易破坏 contract。

## 不同阶段的重点

### 近阶段

重点是把当前主线做扎实：

- RAG / GraphRAG / BM25 检索
- GraphRAG Project
- LangGraph runtime
- 低成本评测
- 检索治理
- 公开可解释的项目文档

这一阶段对应“面试前必须成立”的主能力。

### 中阶段

重点是把当前能力做成更完整的平台骨架：

- supervisor + specialist 的最小多 Agent 路径
- 更严格的 citation / grounding
- 更完整的索引生命周期治理
- 更稳定的公共 API 与服务边界

这一阶段对应“面试后但仍然沿当前主线自然深化”的工作。

### 远阶段

重点是扩大平台外延：

- 更完整的多 Agent 能力
- 更强的代码工作台 / 编程 Agent 能力
- 微服务 / 云原生部署演进
- 异语言业务服务接入

这一阶段对应“平台外延扩大”而不是“当前简历展示必须一次做完”的工作。

## 当前不该做错的事

为了保住这条演进路线，当前应避免：

- 为了“看起来现代”过早拆微服务
- 为了“支持多 Agent”平行造第二套 runtime
- 为了“支持更多领域”把核心逻辑写死在合同审查里
- 为了“显得更强”默认全开 GraphRAG / requery / rerank
- 为了“先把名字改完”而让 `zuno -> zuno` 重命名压过能力主线

## 一句话总结

Zuno 当前最合理的方向不是横向摊大，而是：

```text
先把它做成一个本地优先、领域能力清晰、检索治理扎实的 Agent 工作台，
再在这个基础上逐步演进多 Agent、平台工程化和更强的任务执行能力。
```

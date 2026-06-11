# LangGraph Runtime

## 目标

让 LangGraph 从“项目里已经在用的一个库”升级为 Zuno 的统一运行时编排层。

这份文档关注的不是某个单独 Agent，而是：

```text
什么逻辑应该进 graph，
什么逻辑应该留在 service，
状态如何流动，
trace 和成本如何挂进去。
```

面试前的要求不是“依赖里装了 LangGraph”，而是：

- 主问答流程显式 graph 化
- GraphRAG 正式进入 graph 节点流
- state / trace / fallback / citation 进入统一运行时

## 为什么需要单独定义 Runtime

当前仓库已经有 LangGraph 相关实现，但还没有形成统一的运行时边界。

如果不定义清楚，后面很容易出现：

- 一部分逻辑写在 agent 里
- 一部分逻辑写在 service 里
- 一部分逻辑写成 graph
- 最终没人能说清楚“系统到底怎么跑”

所以这份文档的目标是把运行时边界固定下来。

## Runtime 设计原则

### Graph Owns Flow

流程编排属于 graph，不属于零散 service 调用链。

### Service Owns Capability

能力实现属于 service，不属于 graph 节点本体。

### State Is Explicit

节点之间传递的信息必须进入显式 state，而不是靠隐式上下文拼接。

### Trace Is First-Class

每个关键节点都应能被观察、记录和回放。

### Retry Is Scoped

失败重试必须有边界，不能变成无限黑盒重试。

## 推荐分层

```text
Agent Config Layer
  - agent defaults
  - domain defaults

Runtime Layer
  - StateGraph
  - state schema
  - node transitions
  - checkpoint / trace / cost

Capability Layer
  - retrieval
  - graph extraction
  - tool execution
  - answer generation
```

## Domain QA 主流程

推荐把当前主问答流程统一成：

```text
START
  -> load_agent_config
  -> resolve_domain_pack
  -> route_intent
  -> rewrite_query
  -> retrieve_context
  -> maybe_call_tool
  -> generate_answer
  -> citation_check
  -> END
```

其中：

- `retrieve_context` 内部可以继续调用 orchestrator
- `maybe_call_tool` 不是每次都要执行
- `citation_check` 是主线正式节点，不是后处理补丁

如果面试前要强调“深度融合 LangGraph”，至少要做到：

- `rewrite_query`
- `retrieve_context`
- `generate_answer`
- `citation_check`

这些步骤都在显式 graph 中，而不是藏在单个 agent 或 middleware 黑盒里。

## State 设计原则

第一阶段建议状态至少覆盖：

- 用户输入
- agent id / dialog id
- knowledge ids
- domain pack id
- rewritten queries
- retrieved contexts
- graph paths
- tool results
- draft answer
- citations
- trace metadata
- cost metadata

## 节点职责边界

### graph 节点应该做什么

- 决定流程下一步
- 调用 service
- 写回 state
- 记录节点级 metadata

### graph 节点不应该做什么

- 内部直接实现复杂业务逻辑
- 内部直接操作底层数据库细节
- 把多路检索逻辑手写散在节点里

## 与 Retrieval Orchestrator 的关系

LangGraph runtime 不替代 retrieval orchestrator。

关系是：

```text
LangGraph 负责问答流程编排
RetrievalOrchestrator 负责检索控制面
```

也就是说：

- graph 决定“现在进入检索阶段”
- orchestrator 决定“这次检索具体怎么跑”

普通模式和增强模式的对外体验可以保持简单，但 graph 内部仍然要保留清楚的检索前后节点和状态演进。

## 与 Domain Pack 的关系

LangGraph runtime 必须能感知 Domain Pack，但不持有领域细节本身。

graph 负责：

- resolve 当前 pack
- 把 pack 信息传给 retrieval / answer 相关节点

pack 负责：

- schema
- policy
- template
- eval expectations

## Checkpoint 与恢复

第一阶段不要求把所有节点都做成人类中断点，但必须为后续能力预留：

- node-level trace
- state snapshot
- failure resume

至少要能回答：

- 卡在哪个节点
- 当时 state 里有什么
- 是否可以安全重跑

## 第一阶段非目标

第一阶段不要求：

- 多 Agent supervisor runtime
- 图内并行子图调度
- 复杂人类审批流
- 图级长期记忆系统

第一阶段只要求建立稳定单主 Agent runtime。

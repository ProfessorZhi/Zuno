# Data Ownership & Recovery：事实在哪里、如何一致？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 哪个边界拥有哪类数据，部分失败时如何恢复而不重复业务事实或副作用？
owner: Data Ownership and Recovery Owner
replaces: old module/database/consistency appendices（Superseded）

## Part A — Architecture Narrative

### 谁拥有权威事实

数据架构首先回答“谁有权说某个事实是真的”，而不是先选择数据库。Domain Owner 拥有 Matter、Evidence、Finding、HumanDecision 和 WorkProduct 等业务事实；Runtime Owner 拥有一次执行的控制状态；Knowledge Owner 拥有可重建投影；Tool Owner 拥有外部动作 Receipt；Security 和 Eval 各自拥有授权与评测事实。

它要解决的问题是跨服务部分失败时出现两个互相矛盾的成功记录：一个边界已经提交，另一个边界却仍认为动作未发生。

### Target Scenario：一条部分失败链

这是 Target Scenario，不是历史事实：

Domain Transaction 已提交一个 FindingVersion；随后 Outbox 发布失败，Worker 重试并再次收到 Job；Tool 可能在第一次请求时已经执行，但 Runtime Checkpoint 仍指向执行前。恢复不能用 Queue ACK 或 Checkpoint 覆盖 Domain Truth，而要读取 DomainVersion、EffectReceipt 和 Provider Operation ID，判断业务提交和外部副作用是否已发生，再 Resume、Retry、Reconcile 或进入 Human Review。

### 存储分类和边界

System of Record 保存可审计的 Canonical Business State；Projection 保存可重建的词法、Dense、Graph 和 Citation Index；Runtime Store 保存 Plan、Step 和 Checkpoint；Cache/Memory 保存可过期 Context；Object Store 保存原始文档 Artifact；Queue 保存投递和重试状态。Projection、Cache、Queue 和 Checkpoint 都不能冒充业务真相。

### 责任和非责任

Data Owner 定义逻辑 Ownership、版本和重建规则；各专题 Owner 决定自己持有的事实；Deployment 负责备份和恢复能力；Security 负责访问约束。本文不强制 Database-per-service、Event Sourcing、2PC 或 Saga，也不把某个 PostgreSQL Schema 当作跨文档共享事实。

### 失败、取舍与反转

分布式数据边界增加 outbox/inbox、幂等、对账和 Schema Compatibility 成本，但能防止重复 Effect 和状态误判。V1 可以使用 Shared PostgreSQL Cluster 加逻辑表/Schema Ownership，只有独立可用性、扩缩容、安全或生命周期证据成立时才拆物理库。若一个事务型模块和 Worker 能提供相同恢复语义，应减少分布式数据边界。

### Current / Target / Gap

Current 由 Migration、代码、测试和运行证据证明；Target 是 Logical Ownership first、Projection 可重建、Runtime/Domain 分离和最小对账机制；Hypothesis 是该结构能减少重复业务事实和副作用；Gap 是 Crash Replay、备份恢复、跨服务一致性、Schema Compatibility 和真实操作证据。

## Part B — Detailed Architecture Specification

### Storage Classification

| 类别 | 保存内容 | Owner | 是否可重建 |
|---|---|---|---|

Platform Domain owns Canonical Business State; Agent Runtime owns Graph Control State; Knowledge owns projections and retrieval indexes; unknown historical storage choices remain UNKNOWN until repository or artifact evidence proves them。
| System of Record | Matter、DocumentVersion、accepted Fact/Evidence/Finding、HumanDecision、WorkProduct | Domain | 否，按保留规则 |
| Projection | Chunk、Embedding、Lexical/Dense/Graph/Citation Index | Knowledge | 是 |
| Runtime Control | AgentRun、Plan、Step、Branch、Checkpoint、Interrupt、Budget | Runtime | 是，受恢复 Contract |
| Context/Cache | Working、Session、Matter Context、Memory | Memory Policy | 是/可删除 |
| Artifact | 原始文件、版本化解析产物 | Domain/Knowledge | 按 Artifact Policy |
| Delivery | Job、Attempt、DLQ、Backpressure、Outbox/Inbox | Service/Tool | 可重放/对账 |

### Transaction、Outbox 与 Inbox

本地事务先提交其 Owner 的事实；需要异步发布时使用 transactional outbox 或等价可靠交接。Consumer 以 Inbox/JobId/Idempotency Key 去重；消息发布失败不能回滚已经提交的业务事实，也不能直接生成第二个 Effect。

### Recovery Contract

恢复必须比较 DomainGeneration、RuntimeGeneration、Checkpoint、Receipt、Provider Operation ID 和当前 Policy Epoch。Domain 已提交而 Checkpoint 落后时禁止重复 Mutation；Checkpoint 超前而 Domain 未提交时回到最后合法 Generation；Unknown Effect 进入 reconciliation 或 manual_review，不视为失败已知。

### Ownership、权限与审计

跨 Owner 读取使用 API、Event、Reference、Snapshot 或 Receipt，禁止私有表 JOIN。每条写入绑定 Tenant、Matter、Principal、Scope、Version、Idempotency Key 和 Trace。保留旧版本、失败和对账结果，删除和 legal hold 规则不能破坏必要审计。

### Verification and implementation gap

测试覆盖重复消息、Consumer Crash、Outbox 未发布、Provider timeout、Checkpoint 丢失、Domain/Runtime 分歧、版本冲突、备份恢复和权限撤销。当前 Repository 中出现某中间件只证明代码/配置表面；物理拓扑、恢复成功率和数据丢失边界仍需 Runtime Evidence。

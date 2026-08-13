# Service Architecture：逻辑能力如何形成服务？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 哪些逻辑能力值得形成独立部署和故障边界？
owner: Service Boundary Owner
replaces: old 11-module physical interpretation and docs/project/modules/11-infrastructure.md（Superseded）

## Part A — Architecture Narrative

### 先看哪种工作会互相拖垮

服务边界不是把旧的逻辑模块换成网络地址。一次案件分析同时包含短事务请求、等待模型的长任务、OCR/Embedding/Graph 的重计算、需要强隔离的 Sandbox，以及不应抢占在线资源的离线评测。它们的资源曲线和失败方式不同，才构成拆分的候选理由；几千个用户本身不够。

### 一个跨边界的目标场景

以下是 Target Scenario，不是历史事实。Edge/API 接收 Matter 或 Run；Platform/Domain 记录事务型业务状态；Knowledge Worker 解析材料并建立检索投影；Agent Runtime 负责长任务；Tool/Sandbox 在自己的网络和 Secret 边界内执行动作；Eval Worker 离线比较结果。每个边界只发布自己的 Receipt、Reference、Snapshot 或 Proposal，真正的 Domain Commit 仍回到唯一 Owner。

### 为什么有些能力不该成为服务

直觉上可以把 Legal Capability、Model Gateway、Memory 或 Graph 都拆成服务，但网络跳转并不会自动产生边界。只有独立扩缩容、失败隔离、安全/资源隔离、独立发布、不同可用性、数据 Ownership 或独立运维生命周期中至少一项得到证据，才值得承担服务化成本。纯函数、模型适配和同一资源池内的批处理更适合 library、worker 或 provider adapter。

### 真正麻烦的是部分失败

考虑 Domain Transaction 已提交 Finding，但 Outbox 发布失败；Worker 重试后又收到同一 Job，或者 Knowledge 索引已经写入而 ACK 丢失。服务不能用“消息重试成功”覆盖业务事实，必须依赖幂等键、版本和对账。服务化带来序列化、延迟、Schema 兼容、追踪和本地开发成本；如果模块化单体加独立 Worker 能给出同样的隔离与恢复语义，边界就应该合并。

Python Microservice + independently scalable workers 是 Target；仓库当前只能证明部分进程和 Compose 表面。服务数量、SLO、容量、故障注入和生产运行证据仍是 Gap，五个候选角色不是已实现的 Current 清单。

若这些工作负载在实际测量中没有互相影响，服务边界就不值得保留；这项设计从一开始就接受合并回 Worker 的结果。

服务 Owner 还必须能解释自己的状态、重试和健康信号，否则它只是一个被网络包装的函数。

这条准入标准会把看似“企业级”的拆分挡在正式部署之前。

## Part B — Detailed Architecture Specification

### Service Admission Contract

每个服务候选必须记录 ServiceId、Canonical Owner、owned state、API/Queue Contract、resource profile、failure domain、security boundary、scaling trigger、deployment lifecycle、observability、retry/recovery、alternative 和 reversal evidence。没有这些字段只能保留为 Logical Capability 或 Worker。

Why not 11 services? 11 logical modules are not a physical decomposition。每个候选都必须证明为什么不是 library、worker 或 external provider；也要明确它是否应当留在 library/worker/provider 层，而不是升级成 Service。当前 Target role identifiers 是 `edge-api`、`platform-domain-service`、`agent-runtime-service`、`knowledge-service` 和 `tool-sandbox-service`，但它们是可审计的候选边界，不是 Current 数量承诺。

### Target deployment roles

| Role | Owns | Does not own | First independent reason |
|---|---|---|---|
| `edge-api` | auth handoff、routing、correlation、SSE | Domain、Runtime、Tool effect | external protocol and low-latency |
| `platform-domain-service` | transaction business state and review references | OCR、Agent control、Sandbox | consistency and ownership |
| `agent-runtime-service` | Run、Plan、Step、Checkpoint、Budget | Canonical Fact and normal CRUD | long-running control |
| `knowledge-service` | ingestion、index、retrieval、citation projection | Domain admission and permission truth | CPU/GPU/IO heterogeneity |
| `tool-sandbox-service` | ToolAttempt、EffectReceipt、reconciliation | Agent Plan、Domain Fact | security/resource isolation |
| Eval Worker | Dataset、EvaluationRun、RawResult、ReleaseDecision | Product business state | offline batch lifecycle |

### Communication and queue

HTTP/API 默认用于 CRUD、Query 和小命令；Queue 用于 Agent Run、Ingestion、Embedding、Graph Build、Sandbox 和 Eval；MCP/API 用于外部互操作；gRPC 只有在 latency/serialization benchmark 支持时采用。Job 必须有 JobId、Idempotency Key、Attempt、Lease、Timeout、Cancellation、Retry、DLQ、Backpressure 和 Reconciliation。

### Data and security boundary

服务通过 API、Event、Reference、Snapshot 或 Receipt 读取其他 Owner 的状态，禁止跨服务 JOIN 私有表。每个请求绑定 Tenant、Matter、Scope、Policy Epoch 和 Trace；不可逆 Effect 必须通过 Tool/Security。Shared PostgreSQL Cluster 可以作为物理基础设施，Database-per-service 不是默认要求。

### Testing and reversal

服务拆分前测试模块化替代、Worker 替代和 Provider 替代；拆分后测试部分失败、重复消息、Schema Compatibility、Retry Storm、网络延迟、部署回滚和跨服务 Trace。没有独立收益的服务必须合并；服务数量仍是 Target/Hypothesis，不是 Current。

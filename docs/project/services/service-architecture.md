# Service Architecture：逻辑能力如何形成服务？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 哪些逻辑能力值得形成独立部署和故障边界？
owner: Service Boundary Owner
replaces: old 11-module physical interpretation and docs/project/modules/11-infrastructure.md（Superseded）

## Part A — Architecture Narrative

### 服务边界从工作负载开始

Microservice 是 Target Constraint，但服务数量不是预先决定的。法律任务同时包含短事务 API、LLM-bound 长运行、OCR/Embedding/Graph 的 CPU/GPU/IO 工作、Sandbox 安全隔离和 Eval 批处理。不同资源、故障、权限和生命周期才是服务边界的理由，用户数量本身不是理由。

它要解决的问题是异构工作负载互相抢占资源、失败互相扩散，以及高风险工具需要独立安全边界；如果这些问题不存在，服务化的网络成本就没有理由。

### Target Scenario：复杂案件跨边界运行

这是 Target Scenario，不是历史事实：

Edge/API 接收 Matter 或 Run 请求；Platform/Domain 提交事务型业务状态；Knowledge Worker 解析和检索；Agent Runtime Coordinator 执行长任务；Tool/Sandbox 执行高风险动作；Eval Worker 在离线环境比较结果。每个边界只发布自己的 Receipt、Reference、Snapshot 或 Proposal，最终 Domain Commit 仍由 Domain Owner 完成。

### 候选服务与逻辑能力

候选网络服务角色是 Edge/API、Platform/Domain、Agent Runtime、Knowledge 和 Tool/Sandbox。Eval/Observability 初期更适合作为批处理 Worker 与 Trace Sink。Legal Capability、Model Gateway、Memory、Graph 和 Multi-Agent Profile 默认是逻辑能力、Provider 或 Worker，不自动成为服务。

### Why service 与 Why not service

只有 Independent Scaling、Failure Isolation、Security/Resource Isolation、Independent Deployment、Distinct Availability、Data Ownership 或 Operational Lifecycle 之一有实证，才值得拆服务。若能力只是纯函数、模型调用适配、同一资源池中的批处理或小型策略，它更适合 Python Library、Worker 或 Provider Adapter。每个服务必须拥有清晰状态，不能只是把一次函数调用包成网络跳转。

### 失败、取舍与反转

服务化会增加序列化、网络延迟、Schema 版本、部分失败、重试风暴、分布式追踪、部署协调和本地开发成本。典型失败是 Domain Commit 成功但消息发布失败，或 Knowledge Worker 重试导致重复 Index/Effect。若模块化单体加独立 Worker 已能提供相同的隔离、扩缩容、安全和恢复语义，应合并服务；若独立服务没有真实资源或故障差异，应删除。

### Current / Target / Gap

Current 以仓库进程、Compose、代码和测试证据为准；Target 是 Python Microservice + independently scalable workers；Hypothesis 是异构 workload 和 Security Boundary 足以证明候选服务；Gap 是服务数、SLO、容量、故障注入、部署、团队 Ownership 和生产运行证据。

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

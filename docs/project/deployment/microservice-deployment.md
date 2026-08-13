# Microservice Deployment：服务怎样运行和扩缩容？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Python services、workers、基础设施和部署 Profile 如何运行、扩缩容、升级和隔离？
owner: Deployment / SRE Owner
replaces: docs/project/modules/11-infrastructure.md（Superseded）

## Part A — Architecture Narrative

### 部署先处理资源竞争

这里要解决的问题不是把服务数量做大，而是隔离不同工作负载的资源和失败影响。

用户数量不是部署边界。短 API、等待模型的长 Agent Run、OCR/Embedding/Graph 批处理、Sandbox 隔离和 Eval 批量任务会以完全不同的方式消耗 CPU、GPU、网络和队列。部署层的工作，是让一种任务的拥塞不会把另一种任务拖垮，同时让每个运行单元的失败、升级和回滚都能被看见。

### 一个滚动升级中的目标场景

以下是 Target Scenario，不是历史事实。Agent Worker 正在等待模型响应，Knowledge Worker 同时需要 GPU 构建索引；此时发布新版本，旧 Worker 仍可能持有一个长 Run 的 Checkpoint。Deployment 必须先排空可取消的队列、保留兼容的 Checkpoint 读取能力，再逐步替换 Worker。若 Sandbox Job 违反网络策略，应只隔离该 Job，不能让在线事务和 Eval 队列一起停摆。

### 逻辑能力如何落成物理单元

Edge/API、Platform/Domain、Agent Runtime、Knowledge 和 Tool/Sandbox 是服务候选；OCR、Embedding、Graph Build、Sandbox 和 Eval 更像可独立扩缩容的 Worker Profile。一个 Knowledge Logical Domain 可以同时有 Ingestion Worker 和 Retrieval API，这不改变 Knowledge 对投影的 Ownership。Developer、Staging 和 Production 是不同证据等级，不是仓库里出现三个配置文件就都完成了。

### 失败路径比启动命令更重要

重复消费可能造成双重 Effect，旧 Schema 可能无法读取新 Checkpoint，滚动升级可能把长 Run 留在“看似成功、实际无人继续”的状态。队列 drain、兼容窗口、幂等和恢复检查必须在部署设计里有位置。Kubernetes、Kafka、gRPC、Service Mesh 和 Database-per-service 都有运营成本；如果 Docker/Compose 加独立 Worker 已能满足资源和安全隔离，就不应为了规模想象引入它们。

Target 是 Python-only Service/Worker Profiles 和三种部署 Profile；Docker、Compose、进程和测试只能证明 Current 的局部表面。容量、SLO、HA、回滚、备份、on-call、配置漂移和真实部署证据仍是 Gap，Production Ready 没有被本轮文字更新证明。

部署的核心问题因此不是“能否启动更多容器”，而是长任务、短请求和高风险动作在失败与升级时能否各自恢复。

运行单元的健康状态需要和业务状态分开报告，容器存活不能被解释成 Run 已经完成。

这也是 Deployment 文档不拥有 Domain Fact 的原因。

## Part B — Detailed Architecture Specification

### Deployment Profiles

| Profile | Contract | 证据边界 |
|---|---|---|
| Developer | Compose、同镜像候选服务和最小 Worker、可选依赖 | 仅本地开发和合同验证 |
| Staging | 多服务、多 Worker、真实 Queue/Object/Index Provider、故障和观测测试 | 预发布验证，不等于生产 |
| Production | HA、滚动升级、独立扩缩容、网络隔离、备份恢复、值班责任 | 未经运行证据不得标记 Ready |

### Unit、health and rollout

每个 Deployment Unit 声明 Service/Schema Version、Resource Profile、Queue、Timeout、Cancellation、Health、Readiness、Drain、Trace、Secret/Network Policy 和 Rollback Path。升级使用 Compatibility Window；旧 Worker 与新消息格式必须可共存到迁移完成，无法兼容时停止接收、排空、回滚或人工对账。

### Scaling and communication

HTTP/API 用于 CRUD、Query 和小命令；durable Queue 用于 Agent、Ingestion、Embedding、Graph、Sandbox 和 Eval；MCP/API 用于外部 Host；gRPC 只有在延迟和序列化测试支持时采用。扩缩容依据 Queue Lag、CPU/GPU/IO、并发 Run、Sandbox 数、Error Rate 和预算，而不是注册用户数。

### Failure、backup and recovery

Job/Effect 使用 Idempotency Key、Attempt、Retry、DLQ、Backpressure 和 Reconciliation。未知外部结果先对账；升级中断以 Checkpoint、DomainVersion 和 Receipt 恢复。备份恢复必须验证 RPO/RTO、Domain State、Object Artifact、Projection 重建和 Secret/Config 轮换；声明有 Backup 不等于恢复成功。

### Compatibility and evidence

服务间不跨私表 JOIN，通过 API、Reference、Snapshot、Event 或 Receipt 交互。服务数量、Kubernetes、Kafka、物理库和 Service Mesh 的决定都需要 workload、failure、security、deployment 或 lifecycle Evidence。

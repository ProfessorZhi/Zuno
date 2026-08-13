# Microservice Deployment：服务怎样运行和扩缩容？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Python services、workers、基础设施和部署 Profile 如何运行、扩缩容、升级和隔离？
owner: Deployment / SRE Owner
replaces: docs/project/modules/11-infrastructure.md（Superseded）

## Part A — Architecture Narrative

### 部署首先解决工作负载异构

用户数量不能单独证明微服务。一次法律任务同时包含短 API 请求、LLM-bound 长运行、OCR/Embedding/Graph 的 CPU/GPU/IO 批处理、Sandbox 的强安全隔离和 Eval 的离线批处理。它们的资源曲线、超时、取消、backpressure、failure domain 和升级生命周期不同，这才是独立 Worker 或 Service 的候选理由。

### Target Scenario：资源竞争与隔离

这是 Target Scenario，不是历史事实：

Agent Worker 正在等待模型响应时，Knowledge Worker 需要 GPU/CPU 构建索引；如果两者共享请求线程，短查询会被拖慢。另一个 Sandbox Job 因网络策略违规被隔离；Eval Job 需要批量运行但不能抢占在线事务。Deployment 通过 resource profile、queue、独立健康检查和失败域隔离这些工作负载，仍让 Domain State 由唯一 Owner 保存。

### 运行形态如何从逻辑能力推导

Edge/API、Platform/Domain、Agent Runtime、Knowledge 和 Tool/Sandbox 是候选网络服务角色；OCR、Embedding、Graph Build、Sandbox 和 Eval 更可能是 Worker Profile。一个 Knowledge Logical Domain 可以有 Ingestion Worker 和 Retrieval API，多个物理单元不意味着多个业务 Owner。Developer、Staging 和 Production 是不同证据等级，而不是三种都已完成的事实。

### 责任与非责任

Deployment 负责运行单元、资源、网络、健康、升级、回滚、备份和隔离；不定义 Fact、Plan、Tool Permission、Citation 或评测指标。Kubernetes、Kafka、gRPC、service mesh 和 Database-per-service 不是默认答案，必须由 HA、autoscaling、rolling update、operator cost 或真实 workload 证据推动。

### 主要失败、取舍与反转

长任务占满短请求资源、重复消费触发双重 Effect、旧 Schema 与 Checkpoint 不兼容、滚动升级中断任务，都是部署层需要处理的失败。微服务增加网络延迟、序列化、追踪、配置和本地开发成本；若模块化单体加独立 Worker 能达到相同隔离和扩容，服务拆分应合并。若规模、SLO 或安全证据支持独立边界，再逐步拆分。

### Current / Target / Gap

Current 由 Docker、Compose、进程、测试和运行证据证明；Target 是 Python-only Service/Worker Profiles 与三种部署 Profile；Hypothesis 是 workload/failure/resource/security isolation 能带来收益；Gap 是容量、SLO、HA、回滚、备份、on-call、配置和真实部署证据。

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

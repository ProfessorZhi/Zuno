# Microservice Deployment：服务怎样运行和扩缩容？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Python services、workers、基础设施和部署 Profile 如何运行、扩容、升级和隔离？
owner: Deployment / SRE
replaces: `docs/project/modules/11-infrastructure.md`（Superseded）

## Part A — Architecture Narrative

部署设计要解决的是 workload heterogeneity，而不是用用户数量证明微服务。一次法律任务的短
API 请求、LLM-bound 长运行、OCR/Embedding/Graph 的 CPU/GPU/IO 批处理、Sandbox 的安全隔离和
Eval 的离线成本曲线不同；它们需要不同的资源池、超时、backpressure、failure domain 和扩缩容
策略。

因此 Target 允许几个 network-facing Python service role 加独立 workers，但不把逻辑领域、服务、
进程、容器和团队强行一一对应。Developer 可以用 Compose 验证合同，Staging 关注真实队列、故障
注入和观测，Production 才需要 HA、滚动升级、备份和隔离证据。Kubernetes、Kafka、gRPC 和物理
Database split 都必须由实际部署规模、SLO、升级或资源证据推动。

典型失败是长任务占满短请求资源、重复消费造成双重 Effect，或升级时旧 Schema 与 checkpoint
不兼容。部署必须通过版本兼容窗口、幂等、drain、rollback 和 reconciliation 收口。若一个
模块化服务加 worker 已经满足相同的隔离和扩缩容要求，就不增加平台复杂度。
部署文档不负责定义 Domain Fact、Agent Plan 或 Tool Permission；它只规定运行单元、资源、网络、
升级和恢复边界。

## Part B — Detailed Architecture Specification

### Deployment and rollout contract

每个 deployment unit 声明 service/schema version、resource profile、queue/backpressure、timeout、
cancellation、health/readiness、trace、secret/network policy 和 rollback path。HTTP、queue、MCP/API
的选择必须有 workload 依据；升级采用 compatibility window、drain、idempotent retry、rollback 和
reconciliation。Developer/Compose、Staging 和 Production 是不同证据等级，声明配置存在不能替代
HA、fault-injection、backup/restore、capacity 或 on-call 证据。
Job/Effect 使用幂等键，重复消费只能产生同一 receipt；unknown outcome 先对账，compatibility
失败才允许 rollback 或人工介入。

## Profiles

| Profile | Target |
|---|---|
| Developer | Docker Compose；可用同镜像启动候选五类 service role 和最小 workers；重依赖按 profile 启用 |
| Staging | 多 service、多 worker、真实 queue/object/index provider；做 contract/fault/observability tests |
| Production | HA、滚动升级、独立 scale、network/security isolation、backup/restore；运行时选择 managed container/VM/Kubernetes |

Microservice Target 不自动等于 Kubernetes、Kafka、service mesh、Database-per-service、Event Sourcing 或 Saga。平台选择由 workload、HA、rolling update、autoscaling、operator cost 和 team on-call evidence 决定。

## Scaling reasons

用户数量不单独证明拆分。真正的 workload heterogeneity：

- Platform Domain：短事务、低延迟、强一致；
- Agent Runtime：LLM-bound、长运行、checkpoint、并发/预算；
- Knowledge：CPU/GPU/IO heavy、批处理、索引发布；
- Tool/Sandbox：安全隔离、secret/network、不可逆 effect；
- Eval：离线 batch、可暂停、独立成本。

每类都需要 resource pool、queue/backpressure、timeout/cancellation、SLO、failure domain 和 trace。

## Communication and rollout

HTTP for CRUD/query/small commands; durable queue for long-running work; MCP/API for external interoperability; gRPC only with benchmark evidence. Schema versioning、idempotency、compatibility window、drain、rollback and reconciliation precede independent rollout.

## Current / Target / Gap

- Current：Compose backend + worker + frontend and infrastructure dependencies; Docker uses Python 3.12; no production microservice deployment evidence。
- Target：可独立扩缩容的 network-facing service roles + parse/index/graph/agent/sandbox/eval workers；
  具体数量和物理拆分仍由 workload/failure/security/lifecycle evidence 决定。
- Gap：capacity assumptions、SLO、deployment traces、HA/rollback、service discovery/config/secret distribution、on-call ownership。

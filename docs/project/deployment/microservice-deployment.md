# Microservice Deployment：服务怎样运行和扩缩容？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Python services、workers、基础设施和部署 Profile 如何运行、扩容、升级和隔离？
owner: Deployment / SRE
replaces: `docs/project/modules/11-infrastructure.md`（Superseded）

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

## Round-002 Target refinement（D011）

部署单元按 workload/failure/security/lifecycle 证据划分：Platform/Domain 的短事务、Agent 的
长任务、Knowledge 的 CPU/GPU/IO worker、Tool/Sandbox 的隔离边界和 Eval 的 batch worker 可以
独立扩缩容，但不强制一逻辑领域对应一服务。HTTP 用于小命令与查询，durable queue 用于长任务，
MCP/API 用于外部互操作；gRPC、Kafka、Kubernetes 和物理 Database-per-service 仍是候选而非默认。

本节只收敛 Target deployment rule。实际 service count、SLO、HA、rollback、容量和 on-call 仍是
开放证据缺口。

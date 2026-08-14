# ADR-0012：证据门控的物理服务拆分

- 状态：`accepted-target`
- 日期：2026-08-14
- 决策来源：`docs/history/red-blue/manual-round-01-overall-architecture.md`，Manual Red/Blue Round 01 Main Judgment
- 取代：ADR-0010；旧 ADR 不再属于 active current tree，完整内容由 Git history 保留
- 适用：Physical Service、Worker、Deployment、Cross-host Contract、Operational Ownership

## Context

Round 01 暴露出当前架构叙事的治理张力：ADR-0008 已把“模块化 Backend + 独立 Worker 优先”作为默认物理起点，但 ADR-0010 又把 Microservice Architecture 描述成 accepted-target，并列出一组预设 Network Service Candidate。两种表述会让“证据驱动拆分”退化成“最终必然微服务，只是暂时还没拆”。

当前没有足够的负载、故障、安全、可用性、部署生命周期或独立数据 Ownership 证据，证明 Zuno 必须预先承诺固定 Network Service 数量。服务边界属于 Target Deployment Refinement，不是由逻辑责任层或旧模块目录直接推导的事实。

## Decision

Zuno 的默认物理起点是：

```text
Python Modular Backend
+
Independent Workers where justified
```

Independent Network Service / Microservice 不是预先承诺的终局 Target，而是：

```text
EVIDENCE-GATED DEPLOYMENT REFINEMENT
```

只有当某个具体边界出现可重复证据，证明它需要下列至少一类独立能力时，才允许拆成 Network Service：

- Independent Scaling；
- Failure Isolation；
- Security / Secret Isolation；
- Distinct Availability Requirement；
- Independent Deployment Lifecycle；
- Stable Cross-host API；
- Distinct Data / Operational Ownership。

“任务比较慢”“以后用户会很多”“微服务更先进”都不是充分证据。每个候选边界必须回答：

```text
Why Service?
Why not Library?
Why not Worker?
```

Service Count、Database-per-service、Kafka、Kubernetes、Service Mesh、2PC 和 Saga Framework 不由本 ADR 预冻结。逻辑责任可以先在同一 Backend 内保持清晰；Worker 可以承担长任务、CPU/GPU/I/O 重负载或批处理，而不自动升级为独立 Network Service。

## Ownership and Contract

- Architecture Owner 负责维护“逻辑责任不等于物理服务”的总体原则；
- Service / Deployment Owner 负责提交独立拆分所需的 Scaling、Failure、Security、Availability、Lifecycle、Cross-host Contract 或 Data / Operational Ownership 证据；
- Domain、Runtime、Knowledge、Tool 和 Eval Owner 只拥有自己的逻辑状态与 Contract，不因目录或进程存在而自动拥有独立服务；
- 任何真正的跨 Host 拆分都必须拥有稳定 Contract、超时、重试、幂等、观测和故障恢复语义。

## Consequences

正面：先保持模块化 Backend + Worker，降低网络跳数、Schema 演进、Partial Failure、Retry Storm、Tracing、Secret Distribution 和本地开发成本；只有真实边界证明必要时才承担拆分成本。

负面：在证据出现前不会得到一个看似完整的服务清单；需要为每次拆分保存可复现的 workload、故障、安全或运维证据，且部署演进速度受 Evidence Gate 约束。

## Reversal / Refinement

如果 Worker、进程内模块或现有 Host 已经满足资源隔离、故障恢复和安全边界，则应继续保持合并。若后续出现稳定的独立扩缩容、Failure Blast Radius、Secret / Sandbox 隔离、Availability、Deployment Lifecycle 或跨主机 Ownership 证据，只拆分被证据支持的具体边界，不自动恢复 ADR-0010 的五服务清单。

## Current / Target / Gap

- Current：当前仓库能证明有限的 FastAPI Backend、Compose 和 Worker 表面，不能证明生产服务拓扑。
- Target：Python Modular Backend + Independent Workers where justified；Physical Service Split = `EVIDENCE-GATED`。
- Gap：真实 workload profile、故障隔离、安全边界、Availability、部署生命周期、跨 Host Contract 和独立运营 Ownership 证据尚未完成。

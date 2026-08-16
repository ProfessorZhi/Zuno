# ADR-0013：Round 02 Responsibility Taxonomy

- 状态：`accepted-target`
- 日期：2026-08-15
- 决策来源：Round 02 Main Judgment，记录见 [`docs/history/red-blue/manual-round-02-overall-architecture-freeze-review.md`](../history/red-blue/manual-round-02-overall-architecture-freeze-review.md)
- 取代：ADR-0003 中关于 Infrastructure 作为逻辑模块的 taxonomy 部分，以及与本责任分类直接冲突的旧分类
- 适用：总体责任域、模块入口和后续模块分解

## Context

Round 02 发现旧的 10-module candidate 把不同性质的东西放在同一层：Product Surface、Memory、Capability/Tool 和 Infrastructure 分别包含了接口、可替换 Provider、外部 Effect 和物理原语。它既容易把逻辑责任误读成服务清单，也会让一个候选目录看起来像已经冻结的产品边界。

Main Judgment 要求先统一总体责任分类，再进行 Main Architecture Freeze Review。分类必须支持 Generic Host + Legal Backend 的最小形态，允许 Simple QA 不进入 Native Runtime，同时保持 Platform 和 Optional Provider 可替换。

> 状态说明：以上描述的是本 ADR 作出时的决策背景。Round 02 后续已经完成 Overall Architecture Freeze；当前总体状态和模块设计状态以 `docs/architecture/architecture.md` 与 `docs/modules/README.md` 为准。本 ADR 不重复维护第二套阶段状态。

## Decision

Zuno 的 Canonical Target 使用九个 Logical Responsibility Modules：

1. Application & Integration
2. Legal Domain & Work Product
3. Knowledge & Evidence
4. Agent Runtime & Control
5. Capability & Skill
6. Tool Runtime & Effects
7. Model Gateway
8. Security & Governance
9. Observability & Evaluation

它们是责任域，不是九个 Process、Container、Database、Network Service、Microservice 或 Team。

另外建立一个 **Platform / Infrastructure Responsibility Layer**，提供 PostgreSQL、Object Store、Queue/Worker、Runtime Checkpointer Adapter、CAS、Lease、Fencing、Clock、Index Adapter、Backup/Restore、Network 和 Secret Delivery 等 physical primitives。Platform Layer 不拥有 Domain Success、Knowledge Success、Runtime Success、Capability Success 或 Tool Effect Success。

Memory / Context 不再是一级逻辑模块，而是 **Optional Context Provider Boundary**。Working/Session Context 可以由 Host 或 Runtime 管理；Long-term Memory 只有在 Ablation / Evaluation 证明收益后才启用，并可由 OpenViking、Generic Host 或其他 Provider 提供。

旧 taxonomy 只在 Git History 和 Red / Blue Archive 中保留。ADR-0003 的 CrossModuleEnvelope、Security Epoch、Audit durability、Receipt boundaries、Model Gateway contracts 和 Infrastructure primitives 等其他 accepted contracts 继续有效；本 ADR 只 supersede 与责任分类直接冲突的部分。

## Boundary Clarifications

### Application & Integration

拥有 External Task Intake、Agent Definition/Version surface、Invocation Decision Composition、Generic Host/Court Integration、Response Publication、WorkProduct Delivery、Invalidation Delivery 和 Consumer Acknowledgement Observation。它不要求自行拥有 UI、Login、Session 或 Conversation，也不重新计算其他责任域的事实。

### Legal Domain 与 Knowledge

Legal Domain & Work Product 拥有 Canonical Legal Domain、Formal Admission、AdmissionReceipt、WorkProduct 历史引用绑定和 Domain invalidation truth。Knowledge & Evidence 拥有 KnowledgeGeneration、task-level ReadinessDecision、EvidenceCandidate、CitationLineage 和可重建检索派生。

因此 `EvidenceCandidate != Evidence`、`CitationLineage != WorkProductCitationBinding`，Knowledge generation stale 也不自动等于 WorkProduct stale。

### Capability 与 Tool Runtime

Capability & Skill 负责专业能力 Contract 和 Proposal，例如事件抽取、冲突检测、事实—法条对应和法律适用性。Tool Runtime & Effects 负责 PreparedAction、Approval Binding、ToolAttempt、Idempotency、EffectReceipt 和 Reconciliation。两者可以在物理上共用进程，但其成功、失败、恢复、安全和 Owner 语义分开。

### Agent Runtime & Control

负责 Controller、Plan、PlanVersion、Step、Budget、Parallel Dispatch、Join、Retry、Replan、Reconcile、Interrupt、Resume 和 Checkpoint-based Control Recovery。Multi-Agent / Specialist 是可选执行模式，不是模块存在的理由。Native Runtime 仍是 Conditional / Measurement-gated。

### Security、Model 与 Observability

Security & Governance 是 Authorization、Approval、Model Egress、Tool Permission、Secret / Credential policy、Effective Lifecycle Policy 和 Audit Requirement 的 Policy Owner；执行结果仍由各目标边界负责。

Model Gateway 拥有模型角色到 Provider / Model 的调用、路由、Attempt、Quota 和 Usage / Cost 语义，不拥有业务接受。

Observability & Evaluation 拥有 Telemetry Projection、Eval 和 Measurement Evidence，不拥有 Domain / Security / Effect truth，也不替代 Mandatory Audit durability。

## Consequences

正面：总体架构有稳定的九个责任域，Platform、Provider 和业务状态不再被误读为同一种模块；模块分解可以继续深入，物理部署仍由 ADR-0012 的 Evidence Gate 决定。

负面：现有代码目录不必立即一一对应新责任域；后续实现需要用 typed ports 和 Evidence 解释边界，不能通过目录或进程名称自动宣称 Owner 已经迁移完成。

## Current / Target / Gap

- **Current**：仓库包含与九个责任域相关的代码、Contract 和测试证据，但不能证明九个责任域都已作为完整生产模块实现。Current 以 `docs/evidence/` 与最新代码 / 测试为准。
- **Target**：本 ADR 的九模块、Platform / Infrastructure Responsibility Layer 和 Optional Context Provider taxonomy；Round 02 Overall Architecture 已完成 Freeze。
- **Design status**：九模块 `Design Baseline V1` 已建立，九篇第一轮 `Deep Design V1` 已完成；字段级 Module Detail Freeze 仍未完成。
- **Gap**：字段级 Contract、最终状态枚举、数据库 / Migration、实现迁移、真实测量、生产安全 / 恢复 / HA 和外部资格仍需要后续证据。
- **Implementation Authorization**：本 ADR 本身不授权大规模运行时代码实现。
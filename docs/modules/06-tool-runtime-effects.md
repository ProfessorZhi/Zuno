# 06 Tool Runtime & Effects（工具运行与外部效果）

<!-- status: design-baseline-v1; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么“调用失败”有时反而最危险

如果一次纯计算模型调用超时，通常可以重试；但如果 Zuno 已经向外部法院系统发送“提交结果”的请求，连接超时并不能说明动作失败。请求可能根本没到，也可能已经成功但响应丢失，还可能执行了一部分但外部状态暂时无法查询。

如果系统把这种未知状态当成普通失败再执行一次，就可能产生重复提交、重复通知、重复扣减或其他现实副作用。工具运行与外部效果模块专门保护这条现实边界：**我们不仅要知道“代码调用了什么”，还要知道“现实世界最终发生了什么，以及当前到底能不能确认”。**

### 不是所有 Tool 都有同样风险

只读查询、可安全重复的幂等写入、可补偿写入和不可逆副作用，不应该共享同一种 Retry 策略。一个查询接口超时通常可以重新请求；一个“提交正式结果”接口超时则必须先判断外部系统是否已经执行。

因此 Tool Definition 至少要让运行控制知道它是不是只读、是否有现实副作用、是否支持外部幂等键、是否可以查询执行结果、是否需要审批和强制审计。这里不冻结最终字段名，但副作用风险必须成为 Tool Contract 的一部分，不能只藏在 Prompt 或开发者经验里。

### 一个外部动作怎样安全执行

在真正执行前，系统先把候选动作整理成稳定的 PreparedAction（准备动作）：绑定工具定义版本、非敏感参数摘要、action identity / hash、幂等身份、run / step 因果和当前安全要求。现有跨模块 Registry 对 Tool Runtime 的具体类型可称 `PreparedToolAction`；它是总体架构 `PreparedAction` 在工具执行边界的具体化，不是第二套竞争 Contract。

安全与治理决定当前是否授权、是否需要审批以及必须持久化哪些审计事实。高风险动作只有在所需授权、审批和强制审计已经满足后，才进入真正执行。

真正调用后，`ToolAttempt` 记录一次执行尝试，`EffectReceipt`（效果回执）保存 Zuno 对现实结果的可靠认识。如果结果未知，就进入 Reconcile（对账恢复），通过外部幂等键、状态查询、业务流水号或人工确认判断现实世界究竟发生了什么。

### transport success 为什么不等于 effect success

HTTP 200、队列 ACK、SDK 返回 success 都只说明某层传输或协议成功。它们不能自动证明外部业务系统已经接受并完成动作，更不能证明某个法律结论因此成为正式事实。

工具运行拥有“Zuno 怎样准备、尝试、确认和对账这个动作”的执行语义；外部系统仍然拥有自己内部业务状态的最终事实。需要把外部结果进一步写成 Zuno 的正式法律业务状态时，还必须经过 02 的正式准入。

### 它为什么不等于专业能力

专业能力回答“应该怎样分析、可能应该做什么”；工具运行回答“这个动作是否被允许、怎样执行、有没有重复、现实结果是什么”。一个专业能力即使提出“应该提交这份结果”，也不能直接越过授权、审批和 Effect 控制。

两者可以物理上共用同一个 Python Worker，但成功语义完全不同。Capability 的“成功”可能只是得到了可信候选；Tool Effect 的“成功”意味着现实动作结果已经被可靠确认。

### Secret 为什么不能变成普通参数

工具调用经常需要凭证。CredentialVersionRef / Secret Lease 可以被 Tool Runtime 在受控边界短暂使用，但 Secret Material 不应该进入 PreparedAction 的普通可持久化参数、Prompt、Trace 或日志。

恢复时需要的是“当时使用了哪一版凭证引用、哪个动作 hash 和哪个工具版本”，不是把明文 Secret 永久保存下来。

### 结果未知时系统怎样恢复

如果能确认外部动作根本没有执行，可以在重新授权和预算允许后重试；如果能确认已经执行，则补齐本地 EffectReceipt；如果无法确认，就保持 unknown / reconciling，继续外部查询或转人工。

不能因为本地 checkpoint 显示“tool node failed”就决定重试，也不能因为本地没有 EffectReceipt 就假设外部没有执行。恢复必须先查 durable Attempt / Receipt，再结合外部事实决定下一步。

### 为什么不默认自建完整工具平台

MCP、HTTP API、CLI、已有 Sandbox 或法院现有系统已经能承担很多执行原语。Zuno 真正需要自己保护的是工具定义版本、安全、幂等、Effect Receipt、对账和关键审计，而不是为了“平台完整”先建设一套通用工具市场、复杂 Sandbox 和独立 Tool 微服务。

物理服务拆分仍受 ADR-0012 的证据门控。安全隔离、独立扩缩容或故障半径出现真实证据时再拆，不从逻辑模块名称直接推导服务数量。

### 当前、目标与缺口

Current Runtime Baseline 已记录 Tool Gateway 在 unknown external effect 时进入 `RECONCILE` 并禁止盲目重试，也存在工具与副作用相关的 Contract 基础。完整 PreparedAction / PreparedToolAction、EffectReceipt、ReconciliationReceipt 的生产持久化、真实外部幂等、duplicate effect 故障注入、approval invalidation 和 mandatory audit-before-effect 闭环仍未完整证明。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

现实副作用结果未知时禁止 Blind Retry；transport receipt 不等于 effect success；执行前消费当前授权 / 必要审批 / 审计要求；Secret 不进入普通持久化 payload；Tool Runtime 不拥有专业正确性或正式领域准入。

### B2 Responsibility / Ownership

**Owns**：PreparedAction / PreparedToolAction、ToolAttempt、EffectReceipt、ReconciliationReceipt / EffectReconciliation、tool definition binding、action hash、effect idempotency / reconciliation semantics、执行结果确认状态。

**Does not own**：Authorization / Approval policy、Capability 专业语义、Canonical Domain admission、外部系统内部最终事实、用户界面发布。

### B3 Upstream / Downstream

上游主要接收 04 / 05 的 action proposal、08 的 AuthorizationDecision / ApprovalDecision / Audit Requirement、Platform 的 secret delivery / network primitives。下游向 04 返回 Effect / Reconciliation result，向 02 提供可用于正式准入的外部事实引用，向 09 输出脱敏 execution telemetry。

### B4 Authoritative Facts / Core Objects

核心对象族：Tool Definition / Version reference、PreparedAction / PreparedToolAction、ToolAttempt、EffectReceipt、ReconciliationReceipt、action identity / hash、idempotency identity、external correlation / business reference。Effect class / retry safety 必须能被 Tool Contract 表达，但具体字段后续冻结。

### B5 Cross-boundary Contracts

沿用 `PreparedAction` / `PreparedToolAction`、`ToolAttempt`、`EffectReceipt`、`ReconciliationReceipt`、AuthorizationDecision、ApprovalDecision、AuditPersistenceReceipt。PreparedToolAction 是 Tool Runtime 的具体类型映射，不建立第二套总体动作语义。

### B6 Normal Flow

action proposal → canonicalize / validate → classify effect / retry safety → bind tool version + action hash + idempotency identity → current authorization → approval when required → mandatory audit persistence when required → acquire secret lease if needed → execute ToolAttempt → interpret external response → persist EffectReceipt → if outcome unknown, Reconcile → optional downstream Domain Admission。

### B7 State / Lifecycle

详细 enum 未冻结，但至少要区分 prepared、authorized / denied、awaiting approval、ready to execute、attempted、confirmed not executed、confirmed effect result、outcome unknown、reconciling、reconciled、manual review / terminal failure。一次动作可以有多个 Attempt，但必须归属于同一稳定 action / idempotency identity。

### B8 Failure Taxonomy

主要失败包括：invalid args、schema / tool-definition mismatch、authorization denied / revoked、approval missing / expired、secret lease failure、known-not-executed transport failure、rate limit、duplicate request risk、outcome unknown、external inconsistent status、audit persistence failure、tool provider drift。

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

只读或 confirmed-not-executed 的瞬时失败可在策略允许时 Retry。Tool schema / semantic drift 使原计划失效时由 04 Replan。outcome unknown 必须 Reconcile。每次恢复先查询持久化 Attempt / Receipt 和外部 correlation，再决定是否重试；不得仅依赖 checkpoint。

同一 idempotency identity + 同一 action hash 应返回既有结果或继续同一 reconciliation；同 key 不同 action hash 必须拒绝。

### B10 Security / Approval / Audit

执行时重新授权；高风险动作绑定 action hash 和 ApprovalDecision，动作内容变化后旧审批不能自动复用。强制审计事实必须在对应 Effect 前满足持久化要求。Secret 通过受控引用 / lease 使用，不进入 Prompt / ordinary Trace / ordinary DB columns。

### B11 Persistence / Transaction Boundaries

PreparedAction、Attempt、EffectReceipt 和必要 ReconciliationReceipt 需要耐久保存到能够支持崩溃恢复的边界。不能把对远端系统的网络调用包在本地数据库事务里等待“原子成功”；通过 idempotency、receipts 和 reconciliation 处理跨系统 partial failure。

### B12 Observability / Evaluation

至少观测 tool version、effect class、attempt count、latency、known failure vs unknown outcome、reconcile duration、duplicate suppression、approval wait、audit gate failure 和 external error class。Telemetry 只关联 receipt / action refs，不替代 durable effect facts。

### B13 Current / Target / Gap / Evidence

Current 见 [`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md)。Target 是完整 effect control chain。Gap 包括真实外部系统故障、duplicate effect、unknown outcome、approval invalidation、secret lease failure、audit persistence failure、reconcile E2E 和不同 effect class 的 retry test。

### B14 Code / Database / Migration Constraints

不默认自建复杂 Sandbox 或工具平台；优先复用 MCP / API / CLI / 现有执行环境，加薄 Adapter 保护安全、幂等、Receipt 和对账语义。物理服务拆分继续受 ADR-0012 证据门控。后续数据库设计先围绕 action identity、attempt、receipt 和 reconciliation 恢复需求，不为每个 Tool 单独创造状态表体系。

# 06 Tool Runtime & Effects（工具运行与外部效果）

<!-- status: design-skeleton; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么“调用失败”有时是最危险的状态

如果一次纯计算或明确只读的调用失败，并且可以确认没有改变外部世界，通常可以安全重试；但如果 Zuno 已经向法院系统发送“提交结果”的请求，连接超时并不能说明动作失败。请求可能根本没到，也可能已经成功但响应丢失。

如果系统把这种未知状态当作普通失败再执行一次，就可能产生重复提交、重复通知或其他现实副作用。工具运行与外部效果专门保护这条现实边界。

### 一个外部动作怎样安全执行

在真正执行前，系统先把候选动作整理成稳定的已准备动作：绑定工具定义版本、非敏感参数摘要、幂等身份、run/step 因果和当前安全要求。工程 Contract 在当前跨模块 Registry 中使用 `PreparedToolAction`；总体架构中的 `PreparedAction` 表示同一类“执行前已经稳定化的动作事实”，后续详细设计要保持这一命名映射清晰。

安全与治理决定当前是否授权以及是否需要审批；高风险动作还要先满足强制审计持久化要求。真正调用后，ToolAttempt 记录一次尝试，EffectReceipt（效果回执）保存 Zuno 对结果的可靠认识。

如果结果未知，就进入 Reconciliation（对账恢复）：优先用幂等键、外部查询或已有回执确认现实世界究竟发生了什么；自动化无法确认时转人工，而不是继续猜。

### 只读工具和有副作用工具为什么不能套同一重试规则

查询法院公开接口、读取内部系统信息和“提交正式结果”都可以在技术上表现为一次 HTTP 调用，但风险不同。只读且可确定无副作用的调用可以按普通暂时故障重试；会改变外部状态的调用必须建立更严格的幂等、回执和未知结果处理。

因此工具协议本身并不能决定 Retry 是否安全，必须结合该操作的效果语义。

### 谁拥有最终真相

工具运行拥有“Zuno 怎样准备、尝试、确认和对账这个动作”的语义；外部系统仍然拥有它自己现实世界中的最终事实。Zuno 收到 HTTP 200、队列 ACK 或 transport receipt，都不能自动升级成法律领域事实。

### 它为什么不等于专业能力

一个法律能力可以提出“应该提交这份结果”或“应该查询这个系统”，但是否有权限、如何保证幂等、请求是否真的执行、超时后怎么恢复，都属于工具运行。把两者分开，可以防止专业判断直接绕过安全门禁变成现实动作。

### 出问题以后怎么办

参数无效时拒绝；工具定义或 Schema 漂移使原计划失效时触发重规划；纯传输瞬时失败且确认未产生副作用时可以重试；现实结果未知时必须对账；没有安全的自动恢复路径时转人工。

### 当前、目标与缺口

Current Runtime Baseline 已记录 Tool Gateway 在 unknown external effect 时进入 `RECONCILE` 并禁止盲目重试。完整 PreparedToolAction / EffectReceipt / ReconciliationReceipt 的生产持久化、外部幂等能力、重复副作用故障注入和强制审计前置闭环仍未完整证明。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Owns**：PreparedToolAction（总体架构泛称 PreparedAction）、ToolAttempt、EffectReceipt、ReconciliationReceipt / EffectReconciliation、tool definition binding、effect idempotency / reconciliation semantics。

**Does not own**：Authorization / Approval policy、专业 Capability 正确性、Canonical Domain admission、外部系统内部事实。

### B2 Execution Chain

```text
Action Proposal
→ Tool Runtime prepare / canonicalize
→ current authorization + approval when required
→ mandatory audit persistence when required
→ execute ToolAttempt
→ EffectReceipt
→ unknown ? Reconcile : finish
→ optional downstream Domain Admission
```

### B3 Cross-boundary Contracts

沿用 `PreparedToolAction` / `ToolAttempt` / `EffectReceipt` / `ReconciliationReceipt`、AuthorizationDecision、ApprovalDecision、AuditPersistenceReceipt。不得把 transport receipt 当 effect success。

### B4 Failure Semantics

- schema / tool-definition mismatch：reject 或 Replan。
- transient transport failure with known-not-executed：Retry allowed。
- outcome unknown：Reconcile required，Blind Retry forbidden。
- duplicate side effect risk：依赖 stable idempotency identity / external lookup。
- audit / authorization missing：fail closed 或人工。

### B5 Recovery / Idempotency

每个副作用动作绑定 action identity、action hash、run/step causation 和 idempotency identity。重启后先查询持久化 Attempt / Receipt，再决定重试或对账；不得仅依赖 checkpoint 猜测。

### B6 Security / Persistence / Observability

执行时重新授权；Secret 只通过受控引用/lease 使用，不进入普通日志。PreparedToolAction、Attempt、Receipt 和必要 Reconciliation 需要耐久保存。Telemetry 只引用它们，不替代它们。

### B7 Current / Target / Gap

Current 见 [`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md)。Target 是完整 effect control chain。Gap：真实外部系统故障、duplicate effect、unknown outcome、approval invalidation、audit persistence failure 和 reconcile E2E。

### B8 Code / Database / Migration Constraints

不默认自建复杂 Sandbox 或工具平台；优先复用 MCP/API/CLI/现有执行环境，加薄 Adapter 保护安全、幂等、Receipt 和对账语义。物理服务拆分继续受 ADR-0012 证据门控。

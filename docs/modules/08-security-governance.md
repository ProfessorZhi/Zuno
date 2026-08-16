# 08 Security & Governance（安全与治理）

<!-- status: design-baseline-v1; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么任务开始时允许，不代表十分钟后仍然允许

复杂任务可能运行很久、暂停等待人工、重试模型、重新规划，期间用户权限、数据范围、策略版本、凭证和法律保全状态都可能变化。如果系统只在任务开始时做一次授权，后面的材料读取、模型外发和工具执行就可能继续使用已经失效的权限。

安全与治理负责回答“**现在**谁可以对什么做什么、需要谁批准、数据应该怎样保留和删除”。它是贯穿任务的持续控制面，不是登录页后的一个布尔值。

### 决策权和执行事实必须分开

安全模块拥有“是否允许”的政策决定，但不应该把所有执行结果也收进自己。Security 可以决定某个用户当前能否读取材料、某个模型能否接收这类数据、某个工具动作是否需要审批；真正的材料读取是否成功由对应 Store / Knowledge 边界执行，外部工具是否产生 Effect 由 06 确认，领域结果是否正式提交由 02 决定。

这种分离避免一个 `security_success=true` 被误解成“数据库写入成功、工具执行成功、业务结果也成功”。Security 负责政策和门禁，各执行边界负责证明自己是否真的执行。

### 授权、审批和人工业务判断不是同一件事

`AuthorizationDecision`（授权决定）回答当前访问或动作是否允许；`ApprovalDecision`（审批决定）回答高风险动作是否已经获得所需批准；`HumanDecision`（人工业务决定）属于法律领域，表示专业人员对某个法律结果的确认、修改或拒绝。

三者可以在一个业务流程里连续出现，但不能因为“都有人参与”就混成一个状态。人工业务判断不能替代系统授权，高风险动作的审批也不能自动把模型候选升级为正式法律事实。

### 长任务怎样持续受控

新的受保护材料读取、检索、模型外发、Secret 使用、工具调用和正式提交都要绑定当前策略 / Security Epoch（安全策略版本）。Resume、Retry 和 Replan 不能自动沿用过期授权。

权限变化后，已经完成的合法历史动作仍然是历史事实，但后续新的受保护访问必须使用当前决定重新判断。至于已载入内存的数据能否继续纯计算，则由更细的数据分类和策略决定，不能一刀切地假设“撤权后什么都能继续”或“什么都必须销毁”。

### 审批为什么必须绑定动作内容

如果某个高风险动作需要人工审批，审批的对象不能只是“这个 Step 可以执行”。它应该绑定足够稳定的 action identity / hash、工具版本和关键非敏感参数摘要，使系统能够判断恢复或重规划后动作是否已经变化。

动作内容改变后，旧 ApprovalDecision 不能自动复用；否则用户批准的是 A，系统最后可能执行 B。审批过期、策略版本变化或 action hash 变化都应该重新进入门禁。

### Secret 为什么只能通过引用使用

模型和工具可能需要 API Key、Credential 或内部访问令牌。安全与治理拥有 Secret / Credential 的使用策略，平台层可以提供 Secret Delivery、Lease 和轮换原语，但业务模块不应该持久保存明文 Secret。

模型和工具只拿到在当前用途和时间范围内允许的引用 / lease。日志、Prompt、Trace、普通审计 payload 和普通数据库列都不应因为“方便恢复”而保存 Secret Material。

### 删除为什么不只是删一行

Retention（保留）、Deletion（删除）、Legal Hold（法律保全）和 Compliance Exception（合规例外）的最终政策由安全与治理决定，各数据 Store 负责执行自己的部分。

删除某段长期记忆意味着未来不能继续召回，但如果法律保全仍有效，底层字节可能暂时依法保留；这些被保留的字节也不能重新获得召回资格。反过来，如果物理 purge 仍 pending / failed，就不能对外声称“已经彻底删除”。因此“允许保留”“允许召回”“物理清除完成”是不同事实。

### 审计为什么不能完全交给可观测性

高风险动作需要能够重建：做了什么、为什么允许、谁批准、现实世界发生了什么。Security 定义什么情况下必须审计、必须保存哪些最小事实；实际持久化边界证明这些事实是否已经耐久落盘。

如果强制审计在 Effect 前写入失败，系统应按政策阻止动作。事后即使有一条完整 LangSmith Trace，也不能假装当时已经满足同等级强制审计要求。Trace 适合诊断和关联，不拥有“审计已满足”的权威事实。

### Prompt Injection 为什么是跨模块问题

提示注入不是只靠一个“安全模型”解决。知识模块要避免越权检索，模型网关要遵守外发策略，Capability 不能把不可信文本当系统指令，工具运行必须在真实执行前重新授权和审批，运行时不能让模型绕过预算或门禁。

安全与治理提供统一政策和决策引用，各模块在自己的受保护边界执行。这样即使模型被诱导产生恶意 Tool Call Proposal，Proposal 仍然只是候选，不会直接成为现实副作用。

### 当前、目标与缺口

Wave 1 Registry 已确认 Security Epoch、Authorization、SecretRef / CredentialVersionRef、Audit Requirement、Lifecycle 等 Target Contract；当前 Runtime baseline 也要求无效 Security / Budget owner reference 时 fail closed。但外部安全资格、真实 cross-tenant / no-egress、secret leakage、prompt injection + tool、revoked permission、approval invalidation、legal hold / deletion enforcement 和生产审计恢复测试仍未完成。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

Continuous Authorization（持续授权）是默认原则；Resume / Retry / Replan 不复用失效授权；Security 决定政策但不冒充各 Store / Tool / Domain 的执行事实；Secret NEVER enters ordinary Prompt / Trace；mandatory audit failure 在需要时 fail closed；Lifecycle policy 与 store enforcement 分离。

### B2 Responsibility / Ownership

**Owns**：Identity / Principal policy、AuthorizationDecision、Effective Security Epoch、ApprovalDecision、model egress policy、tool permission、secret / credential policy、Retention / Deletion / Legal Hold / Compliance Exception policy、Audit Requirement。

**Does not own**：Legal Finding / HumanDecision、Runtime Plan、Knowledge Readiness、Tool Effect outcome、Domain Admission、Audit storage success itself、各 Store 的 purge completion fact。

### B3 Upstream / Downstream

上游接收 identity / principal、tenant / matter / resource / action、data classification、risk、credential use purpose、lifecycle context 和当前策略。下游向 01 / 03 / 04 / 05 / 06 / 07 / 02 提供授权、审批、Security Epoch、credential refs、lifecycle decision 和 audit requirement；各模块返回自己的 enforcement / receipt / outcome 引用供审计和评测。

### B4 Authoritative Facts / Core Objects

核心事实族：Principal / Identity ref、AuthorizationDecision、Security Epoch / policy hash、ApprovalDecision、CredentialVersionRef / SecretRef / Lease ref、EffectiveLifecycleDecision、Audit Requirement、policy reason / expiry。执行 receipt 属于对应执行模块或 Store。

### B5 Cross-boundary Contracts

跨边界至少稳定传递 principal、tenant / scope、action / resource、policy epoch、decision outcome、reason code、expiry / refresh requirement、approval binding、credential ref 和 lifecycle decision。ApprovalDecision 应绑定 action identity / hash；Action 改变后不得静默复用旧批准。

### B6 Normal Flow

request enters protected boundary → resolve principal / scope → load current policy epoch → evaluate authorization / egress / tool / secret policy → if high-risk, evaluate approval requirement → if mandatory audit required, require durable persistence proof → return typed decision refs → target module enforces → enforcement result / receipt becomes separate fact。

### B7 State / Lifecycle

至少区分 policy / epoch active / superseded、authorization valid / denied / expired / revoked、approval pending / granted / denied / expired / invalidated、secret lease active / expired / revoked、lifecycle retain / no-recall / purge-pending / purge-complete / legal-hold 等语义。具体 enum 和 policy engine 后续冻结。

### B8 Failure Taxonomy

主要失败包括 missing / stale security context、revoked permission、policy evaluation unavailable、approval missing / expired / action changed、secret lease unavailable、credential stale、model egress denied、mandatory audit persistence failed、cross-tenant access、lifecycle conflict、purge pending / failed、policy epoch drift。

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

授权计算可以在同一输入 / policy epoch 下幂等重算，但不能缓存为永久通行证。策略变化后需要新 Decision。Approval 在 action hash 未变化且仍在有效期内才可复用。Security 不负责 06 的 effect reconcile；如果权限在重试 / 对账过程中变化，后续外部访问仍需重新授权。

### B10 Security / Approval / Audit

本节本身即本模块主责：所有受保护边界 fail closed / review 的条件必须明确；Secret Material 永不普通导出；Prompt Injection + Tool 路径必须依赖多层门禁而不是模型自律；高风险 effect 在执行前消费 current authorization、required approval 和 mandatory audit persistence proof。

### B11 Persistence / Transaction Boundaries

Security policy / epoch、Authorization / Approval、Lifecycle Decision 和必要 Audit Requirement 要达到可审计与恢复所需的耐久程度。Platform 可以提供 CAS、Lease、Fencing、Secret Delivery 和 storage，但不能自行改变 policy。每个 Store 保存自己的 lifecycle enforcement state / receipt；不做跨所有 Store 的全局 2PC。

### B12 Observability / Evaluation

Telemetry 记录脱敏 decision ref、policy epoch、reason code、latency、deny / revoke / expiry、approval wait、secret lease failure 和 lifecycle enforcement lag，不导出 Secret。安全验证至少覆盖 cross-tenant、no-egress、revocation、stale credential、secret leakage、prompt injection + tool、duplicate effect、legal hold / deletion 和 audit recovery。

### B13 Current / Target / Gap / Evidence

Target 见 ADR-0014 与 [`wave1-cross-module-contract-registry.md`](../governance/wave1-cross-module-contract-registry.md)。Current 只有有限 Contract / fail-closed 基线，Security Qualified 尚未建立。Gap 包括真实 policy engine behavior、cross-tenant / no-egress、revocation、approval invalidation、secret delivery、lifecycle enforcement 和 production audit reconstruction。

### B14 Code / Database / Migration Constraints

安全策略与执行原语分离。详细数据库字段、Policy Engine 和独立 Security Service 都不在本基线中预冻结；默认优先模块化实现和 typed decision ports。任何实现都不得让 Platform、Runtime、Tool 或 Application 通过本地默认值放宽 Security policy，也不得为了恢复便利把明文 Secret 持久化。

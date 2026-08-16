# 08 Security & Governance（安全与治理）

<!-- status: design-skeleton; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么任务开始时允许，不代表十分钟后仍然允许

复杂任务可能运行很久、暂停等待人工、重试模型、重新规划，期间用户权限、数据范围、策略版本或凭证都可能变化。如果系统只在任务开始时做一次授权，后面的材料读取、模型外发和工具执行就可能继续使用已经失效的权限。

安全与治理负责回答“**现在**谁可以对什么做什么、需要谁批准、数据应怎样保留”。它是持续控制面，不是登录页后的一个布尔值。

### 授权、审批和人工法律判断不是同一件事

AuthorizationDecision（授权决定）回答当前访问或动作是否允许；ApprovalDecision（审批决定）回答高风险动作是否需要并已经获得批准；HumanDecision（人工业务决定）则属于法律领域，表示专业人员对某个法律结果的确认、修改或拒绝。

三者可以在一个业务流程里连续出现，但不能因为“人工点了同意”就混成一个状态。安全审批允许一个动作发生，不等于法律领域接受这个动作产生的业务结论。

### 长任务怎样持续受控

新的受保护材料读取、检索、模型外发、秘密读取、工具调用和正式提交都要绑定当前策略/安全版本。Resume、Retry 和 Replan 不能自动沿用过期授权。

模型只拿到允许范围内的数据，工具只拿到已授权的凭证版本或短期 Secret Lease（秘密租约）；Secret Material 不进入普通 Prompt、Trace 或日志。

### 安全决定和实际执行为什么还要分开

安全与治理拥有“是否允许、需要什么审批和审计”的政策事实，但它不亲自拥有每个存储或外部动作的执行成功事实。

例如，高风险工具调用需要强制审计时，Security 定义审计要求；平台持久化边界证明必要事实是否已经耐久保存；工具运行决定是否真正执行并保存效果回执；可观测性可以接收审计事件和诊断引用。任何一层都不能用自己的 success 替代其他层的 success。

### 删除为什么不只是删一行

Retention、Deletion、Legal Hold 和 Compliance Exception 的最终政策由安全与治理决定，各数据存储负责执行自己的部分并返回执行状态。删除某个长期记忆意味着未来不能继续召回，但如果法律保全要求仍有效，底层字节可能暂时需要保留；保留也不能重新恢复召回资格。

因此“允许保留”“允许召回”“已经完成物理清除”是不同事实。Purge 仍在等待或失败时，系统不能宣称数据已经 fully deleted。

### 审计为什么不能完全交给可观测性

高风险动作需要能够重建：做了什么、为什么允许、谁批准、现实世界发生了什么。需要在动作前耐久保存的审计事实如果写入失败，不能事后用一条完整 LangSmith Trace 假装已经满足同等级审计要求。

可观测性负责诊断和评测，Security 定义审计要求，持久化边界证明是否落盘，工具或领域模块则分别拥有自己的效果和业务事实。

### 当前、目标与缺口

Wave 1 Registry 已确认 Security Epoch、Authorization、SecretRef / CredentialVersionRef、Audit Requirement、Lifecycle 等 Target Contract；当前 Runtime baseline 也要求无效 Security / Budget owner reference 时 fail closed。但外部安全资格、真实 cross-tenant/no-egress、secret leakage、prompt injection + tool、revoked permission 和生产审计恢复测试仍未完成。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Owns**：Identity / Principal policy、AuthorizationDecision、Effective Security Epoch、ApprovalDecision、model egress policy、tool permission、secret/credential policy、Retention / Deletion / Legal Hold / Compliance Exception policy、Audit Requirement。

**Does not own**：Legal Finding / HumanDecision、Runtime Plan、Tool Effect outcome、Knowledge readiness、Audit storage success itself。

### B2 Inputs / Outputs

输入：principal、tenant/scope、action/resource、data classification、current policy epoch、risk、credential/use purpose、lifecycle context。

输出：AuthorizationDecision、ApprovalDecision、SecurityEpoch ref/hash、CredentialVersionRef / SecretRef、EffectiveLifecycleDecision、Audit Requirement。

### B3 Continuous Authorization

每一次新的受保护边界重新检查当前决定；Resume / Retry / Replan 不复用失效授权。Policy Epoch / hash 用于检测长任务中的策略漂移。

### B4 Decision / Enforcement Split

- Security owns effective authorization / approval / lifecycle / audit requirement decisions.
- Each data store is its own lifecycle enforcement owner and returns status/receipt.
- Infrastructure persistence may prove mandatory audit durability, but does not decide the security policy.
- Tool Runtime owns effect execution/reconciliation；Legal Domain owns HumanDecision/Formal Admission；Observability may own accepted AuditEvent/telemetry projection.

### B5 Lifecycle / Legal Hold

Security 是有效生命周期政策 Owner，各 store 是 enforcement owner。删除不得绕过 Legal Hold；future recall eligibility 与 physical retention 分开；purge pending / failed 时不能声称 fully deleted。

### B6 Failure / Recovery

- missing / stale security context：fail closed 或 review。
- revoked permission：阻止后续受保护访问。
- approval missing / expired：pause / deny。
- secret lease unavailable：不降级为明文凭证。
- mandatory audit persistence failed：按政策阻止高风险 effect。

### B7 Observability / Audit

Telemetry 记录脱敏 decision reference、policy epoch 和原因码；Secret NEVER EXPORT。关键重建依赖 durable Authorization / Approval / Audit Persistence / Effect / Admission facts，不依赖 Trace 完整性。

### B8 Current / Target / Gap

Target 见 ADR-0014 与 [`wave1-cross-module-contract-registry.md`](../governance/wave1-cross-module-contract-registry.md)。Current 仅有有限 contract / fail-closed 基线，Security Qualified 尚未建立。Gap：cross-tenant、no-egress、revocation、secret leakage、prompt injection + tool、legal hold / deletion enforcement、production audit recovery。

### B9 Code / Database / Migration Constraints

安全策略与执行原语分离：Platform 可提供 secret delivery、CAS、fencing、storage，但不能自行放宽 policy。详细数据库字段和策略引擎选择需后续设计，不默认引入独立 Policy Service。

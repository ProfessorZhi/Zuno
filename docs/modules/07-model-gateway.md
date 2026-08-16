# 07 Model Gateway（模型网关）

<!-- status: design-skeleton; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么模型调用不能散落在每个模块里

Zuno 会同时需要复杂推理、快速执行、抽取、重写、综合和评测等不同类型的模型能力。如果每个业务模块自己选择 Provider、处理凭证、配额、重试和成本，系统很快会出现不同的安全规则、预算口径和失败语义。

模型网关把“如何安全、可控、可替换地调用模型”集中起来，但不把模型输出升级为业务事实。

### 模型角色解决的不是“哪个模型最强”

规划和关键质量判断通常需要更强推理能力；查询改写、抽取、分类和格式转换通常更适合快速模型。Zuno 因此先定义角色的能力要求，再由模型网关把角色映射到经过资格检查的具体 Provider / Model。

这样更换供应商时，上层不需要把“GPT 某型号”“Claude 某型号”写进业务流程，也能避免 Planner 生成执行器根本无法完成的巨大步骤。

### 一次模型调用怎样被约束

上层提交模型角色、操作类型、预算、截止时间和任务输入引用。安全与治理先决定当前数据是否允许发给目标 Provider，以及凭证、地域和数据分类限制；模型网关再做路由、配额预留、真实调用、取消和使用量结算。

快速执行模型失败后，可以先在原计划仍成立时调整参数重试，再升级到更强执行模型；仍失败时由 Critic 参与判断应该继续重试、触发重规划还是放弃。替代链不能绕过最低质量、安全和预算要求。

### 哪些事情尽量不要交给模型

模型最适合产生语义判断和候选内容，不应该因为“什么都能生成”就接管确定性控制。检索执行、工具真实调用、Schema Validation（模式校验）、Citation Check（引用校验）、测试、安全门禁和审批门禁，只要能用确定性代码可靠完成，就优先不用模型决定。

这能让关键边界可重复测试，也减少模型输出直接控制权限、数据库和现实副作用的机会。

### 为什么模型不能直接更新最终状态

模型只产生 Proposal（候选）。它不能直接修改正式领域状态、批准权限、执行未审批副作用、激活 PlanVersion、绕过 Budget 或提交长期 Memory。模型网关也不替上层判断“这次任务是否正式成功”；它只证明模型调用本身发生了什么。

### 当前、目标与缺口

Wave 1 Contract Registry 已确认 ModelRoutingDecision、ModelCallAttempt、Quota / Usage / Cancellation 等 Target Contract；当前仓库存在模型网关实现和测试基础，但本骨架不把它提升为完整生产 Current。正式 Provider 凭证、四 Profile runtime、预算/安全资格和真实模型故障测量仍是缺口。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Owns**：model role mapping、provider/model routing、ModelRoutingDecision、ModelCallAttempt、quota semantics、Usage / Cost Receipt、cancellation / provider failover within approved policy。

**Does not own**：business/result eligibility、Authorization policy、Runtime Plan、Canonical Domain State、Tool effects、deterministic citation/security/approval gates。

### B2 Model Roles

Target roles：TASK_ANALYZER、PLANNER、PLAN_REPAIR、EXECUTOR_FAST、EXECUTOR_REASONING、QUERY_REWRITER、EXTRACTOR、CRITIC、SYNTHESIZER、FINAL_CRITIC。具体 provider/model mapping 属于配置和资格管理，不在文档中硬编码厂商。

强模型主要承担复杂规划、Plan Repair、关键 Reflection 和 Final Reflection；快速模型主要承担 Query Rewrite、抽取、分类、格式转换和普通 ReAct。

### B3 Inputs / Outputs

输入：role、operation、deadline、budget/quota、security decision / credential ref、prompt/input refs、required quality profile。

输出：routing decision、call attempt/result、usage/cost receipt、cancellation/reconciliation state、provider/model reference。

### B4 Failure / Fallback

`EXECUTOR_FAST → 调整参数重试 → EXECUTOR_REASONING → Critic: Retry / Replan / Abstain` 是默认升级方向。Provider failover 只有在安全、质量、预算和任务语义都允许时才发生。

Model transport failure ≠ task failure；model response success ≠ result eligibility；usage receipt ≠ business success。

### B5 Deterministic Boundary

Retrieval execution、Tool execution、Schema Validation、Citation Check、Tests、Security Gate、Approval Gate 在存在可靠确定性实现时优先使用非模型能力。模型可以提供辅助信号，但不能成为绕过这些门禁的权威路径。

### B6 Security / Persistence / Observability

Security 决定 provider/model allowlist、数据分类、模型外发和 credential scope。秘密不进入 Prompt/Trace。RoutingDecision、Attempt、Usage / Cost 和必要 Cancellation Receipt 要可审计；Observability 消费脱敏引用。

### B7 Current / Target / Gap

Target Contract 见 [`wave1-cross-module-contract-registry.md`](../governance/wave1-cross-module-contract-registry.md)。Current 需要进一步按代码、Provider 和真实运行重新审计。Gap：正式凭证、provider qualification、usage settlement、fallback eval、budget fault test。

### B8 Code / Database / Migration Constraints

模型 SDK 和 Provider adapter 是可替换实现；不得让上层模块直接绕过 Gateway 持有长期凭证或各自实现不同的安全/配额规则。表结构和独立服务拆分在详细设计与测量后决定。

# 07 Model Gateway（模型网关）

<!-- status: design-skeleton; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么模型调用不能散落在每个模块里

Zuno 会同时需要强推理模型、快速模型、抽取模型、重写模型和批量评测模型。如果每个业务模块自己选择 Provider、处理凭证、配额、重试和成本，系统很快会出现不同的安全规则、预算口径和失败语义。

模型网关把“如何安全、可控地调用模型”集中起来，但不把模型输出升级为业务事实。

### 不同任务为什么需要不同模型角色

复杂规划、Plan Repair、关键 Reflection 和 Final Reflection 更适合强推理模型；Query Rewrite、提取、分类、格式转换和普通 ReAct 更适合成本较低的快速模型。目标角色包括 TASK_ANALYZER、PLANNER、PLAN_REPAIR、EXECUTOR_FAST、EXECUTOR_REASONING、QUERY_REWRITER、EXTRACTOR、CRITIC、SYNTHESIZER、FINAL_CRITIC。

角色描述的是能力要求，不和某个厂商模型永久绑定。Planner 还必须知道执行器能力边界，不能生成执行器无法完成的巨大 Step。

### 一次模型调用怎样被约束

上层提交模型角色、操作类型、预算和任务上下文。安全与治理先决定当前数据是否允许发给目标 Provider、凭证版本和地域/分类要求；模型网关再选择具体模型、预留配额、执行调用并记录尝试和使用量。

弱模型失败后可以先调整参数重试，再升级到更强执行模型；仍失败时由 Critic 判断应该重试、重规划还是放弃。降级链不能绕过最低质量和安全要求。

### 为什么模型不能直接更新最终状态

模型只产生 Proposal。它不能直接修改 Canonical Domain State、批准权限、执行未审批副作用、激活 PlanVersion、绕过 Budget 或提交长期 Memory。这样模型供应商可以替换，业务权威仍然稳定。

### 当前、目标与缺口

Wave 1 Contract Registry 已确认 ModelRoutingDecision、ModelCallAttempt、Quota / Usage / Cancellation 等 Target Contract；当前仓库也存在模型网关实现和测试基础，但本骨架不把它提升为完整生产 Current。正式 Provider 凭证、四 Profile runtime、预算/安全资格和真实模型故障测量仍是缺口。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Owns**：model role mapping、provider/model routing、ModelRoutingDecision、ModelCallAttempt、quota semantics、Usage / Cost Receipt、cancellation / provider failover within approved policy。

**Does not own**：business eligibility、Authorization policy、Runtime Plan、Canonical Domain State、Tool effects。

### B2 Model Roles

Target roles：TASK_ANALYZER、PLANNER、PLAN_REPAIR、EXECUTOR_FAST、EXECUTOR_REASONING、QUERY_REWRITER、EXTRACTOR、CRITIC、SYNTHESIZER、FINAL_CRITIC。具体 provider/model mapping 属于配置和资格管理，不在文档中硬编码厂商。

### B3 Inputs / Outputs

输入：role、operation、deadline、budget/quota、security decision / credential ref、prompt/input refs、required quality profile。

输出：routing decision、call attempt/result、usage/cost receipt、cancellation/reconciliation state、provider/model reference。

### B4 Failure / Fallback

`EXECUTOR_FAST → 调整参数重试 → EXECUTOR_REASONING → Critic: Retry / Replan / Abstain` 是默认升级方向。Provider failover 只有在安全、质量、预算和任务语义都允许时才发生。

### B5 Security / Persistence / Observability

Security 决定 provider/model allowlist、数据分类、模型外发和 credential scope。秘密不进入 Prompt/Trace。RoutingDecision、Attempt、Usage / Cost 和必要 Cancellation Receipt 要可审计；Observability 消费脱敏引用。

### B6 Current / Target / Gap

Target Contract 见 [`wave1-cross-module-contract-registry.md`](../governance/wave1-cross-module-contract-registry.md)。Current 需要进一步按代码、Provider 和真实运行重新审计。Gap：正式凭证、provider qualification、usage settlement、fallback eval、budget fault test。

### B7 Code / Database / Migration Constraints

模型 SDK 和 Provider adapter 是可替换实现；不得让上层模块直接绕过 Gateway 持有长期凭证或各自实现不同的安全/配额规则。表结构和独立服务拆分在详细设计与测量后决定。

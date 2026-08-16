# 07 Model Gateway（模型网关）

<!-- status: design-baseline-v1; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么模型调用不能散落在每个模块里

Zuno 会同时需要强推理模型、快速模型、抽取模型、重写模型和评测模型。如果每个业务模块自己选择 Provider、处理凭证、配额、重试、降级和成本，系统很快会出现不同的安全规则、预算口径和失败语义。

模型网关把“怎样安全、可控、可替换地调用模型”集中起来，但不把模型输出升级为业务事实。业务模块表达的是“我需要一个什么角色、什么质量要求、什么预算和数据边界的模型能力”，而不是直接写死厂商和模型名。

### 模型角色为什么比模型名字稳定

复杂规划、Plan Repair、关键 Reflection 和 Final Reflection 更适合强推理模型；Query Rewrite、提取、分类、格式转换和普通 ReAct 更适合成本较低的快速模型。目标角色包括 TASK_ANALYZER、PLANNER、PLAN_REPAIR、EXECUTOR_FAST、EXECUTOR_REASONING、QUERY_REWRITER、EXTRACTOR、CRITIC、SYNTHESIZER 和 FINAL_CRITIC。

这些角色描述的是能力要求，不和某个厂商模型永久绑定。模型供应商、版本和价格会变化，但 Planner 对“需要规划模型还是抽取模型”的判断应该保持稳定。

### 模型不应该承担能由确定性代码完成的事情

Retrieval Execution（检索执行）、Tool Execution（工具执行）、Schema Validation（结构校验）、Citation Check（引用检查）、测试、安全门禁和审批门禁，只要可以可靠地用确定性代码完成，就不应该默认交给大模型决定。

模型擅长的是分析、生成、重写、分类和复杂判断，不应该变成系统所有 if-else 的替代品。把确定性门禁交回代码，不仅更便宜，也让失败更容易复现和审计。

### 一次模型调用怎样被约束

调用方提交模型角色、任务操作、输入引用、最低质量要求、deadline、预算和当前安全决定。安全与治理先决定当前数据能否发给某类 Provider、允许使用哪一版 Credential、是否存在地域或数据分类限制；模型网关再选择具体 Provider / Model、预留配额、执行调用并记录尝试、取消和使用量。

网关负责 Provider-specific formatting、SDK 适配和路由，但不应该拥有法律专业 Prompt 的业务语义。专业 Prompt 可以属于 Capability 或 Runtime 的任务定义；Gateway 只负责把已经批准的请求可靠地送给具体 Provider。

### 弱模型失败以后怎样升级

默认升级方向保持：

```text
EXECUTOR_FAST
→ 调整参数重试
→ EXECUTOR_REASONING
→ Critic 判断 Retry / Replan / Abstain
```

升级不是“失败就自动换最贵模型”。每一步都要满足当前安全、预算、质量和任务语义；如果替代 Provider 不符合数据外发政策，或强模型也不能满足最低证据要求，就应该停止、降级为草稿或交人工。

### 为什么模型不能直接更新最终状态

模型只产生 Proposal（候选建议）。它不能直接修改 Canonical Domain State、批准权限、执行未审批副作用、激活 PlanVersion、绕过 Budget 或提交长期 Memory。

这样模型供应商可以替换，业务权威仍然稳定。即便某个模型“自称完成”，真正的步骤验收、正式准入和外部 Effect 都必须由各自责任域决定。

### 模型调用失败和现实副作用失败有什么不同

大多数模型调用属于计算型依赖。超时、503、限流通常意味着“这一轮没有拿到结果”，可以在预算和安全条件允许时重试或换 Provider；它们通常不会像外部提交接口那样产生不可确认的现实副作用。

但模型调用仍可能产生费用、配额消耗和取消竞态，所以 CallAttempt、Usage / Cost、Cancellation 等需要可审计。不能因为生成内容丢了，就假装 Provider 没收费或没占用配额。

### 为什么值得独立成一个责任域

如果模型选择散落在每个 Capability 和 Agent 节点里，就无法统一安全外发、预算、Provider 资格和成本核算，也很难替换供应商。独立模型网关让上层依赖“模型角色和最低要求”，而不是依赖具体 SDK。

### 当前、目标与缺口

Wave 1 Contract Registry 已确认 ModelRoutingDecision、ModelCallAttempt、Quota / Usage / Cancellation 等 Target Contract；当前仓库也存在模型网关实现和测试基础，但本设计不把它提升为完整生产 Current。正式 Provider 凭证、四 Profile runtime、provider qualification、预算 / 安全资格、真实模型故障和 fallback 质量测量仍是缺口。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

模型角色与具体 Provider 解耦；Provider failover 不绕过安全、质量和预算；模型输出只产生候选；上层模块不得绕过 Gateway 持有长期 Provider 凭证；能由确定性代码完成的执行和门禁不默认交给模型。

### B2 Responsibility / Ownership

**Owns**：model role mapping、provider / model routing、ModelRoutingDecision、ModelCallAttempt、quota semantics、Usage / Cost Receipt、cancellation、approved provider failover、provider/model reference 和调用层兼容语义。

**Does not own**：business eligibility、Authorization policy、Runtime Plan、Canonical Domain State、Tool Effect、Capability professional semantics、final answer publication。

### B3 Upstream / Downstream

上游主要接收 04 / 05 / 03 / 09 的 model role request、prompt / input refs、budget / deadline / quality profile，以及 08 的 egress / credential decision。下游向调用者返回 model result / failure、routing decision、usage / cost、cancellation status，并向 09 输出脱敏 model telemetry。

### B4 Authoritative Facts / Core Objects

核心对象族包括 ModelRole、Provider / Model Qualification Reference、ModelRoutingDecision、ModelCallAttempt、Quota reservation / consumption、Usage / Cost Receipt、Cancellation / timeout state、Provider capability / version ref。业务 Prompt 本体和领域结果不属于 Gateway 权威状态。

### B5 Cross-boundary Contracts

调用至少携带 role、operation、deadline、budget / quota、required quality profile、security decision / credential ref 和 input / prompt refs。输出至少能区分 routing decision、attempt/result、usage/cost、cancellation / timeout 和 provider/model reference。

### B6 Normal Flow

role request → validate current security / egress decision → check provider qualification → reserve quota / budget → select provider/model → prepare provider-specific request → execute ModelCallAttempt → validate transport / schema → record usage / cost → return typed result → caller performs business acceptance。若失败，按批准 fallback chain 选择 retry / stronger model / abstain。

### B7 State / Lifecycle

至少区分 provider/model qualified / restricted / disabled、routing selected、quota reserved、attempt in-flight、completed、failed、cancel requested / cancelled / cancellation unknown、usage settled / pending。具体 enum 后续冻结。

### B8 Failure Taxonomy

主要失败包括 provider unavailable、rate limit、timeout、invalid response schema、quality floor not met、security egress denied、credential unavailable、quota / budget exhausted、fallback provider not equivalent、cancellation ambiguity、usage settlement mismatch。

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

同一模型调用在 Runtime 层可重试，但必须保留 attempt identity、预算累计和 usage truth，不能让重试“重置成本”。Provider temporary failure 可按策略重试或 failover；若角色能力不足或任务假设变化，由 04 决定 Replan。模型调用通常不使用 06 的现实 Effect Reconcile，但 cancellation / billing ambiguity 需要自己的 attempt / usage 对账。

### B10 Security / Approval / Audit

08 决定 provider/model allowlist、数据分类、地域 / 模型外发、credential scope 和 secret policy。Gateway 只消费这些决定并执行。Secret Material 不进入 Prompt / Trace；Prompt / response 的可观测内容按数据分类和 redaction policy 处理。

### B11 Persistence / Transaction Boundaries

RoutingDecision、Attempt、Usage / Cost 和必要 Cancellation state 需要达到预算、审计和恢复要求的持久化程度，但不要求与 Runtime Checkpoint 或领域事务做 2PC。高吞吐明细可以物理外置，权威 usage / billing 仍需可对账。

### B12 Observability / Evaluation

至少观测 provider/model、role、latency、TTFT / completion latency（如果可得）、token / cost、retry / failover、quota rejection、schema failure、quality eval reference 和 cancellation outcome。09 负责跨模型实验和质量证明，Gateway 不因为 SDK 调用成功就宣称模型适合某类法律任务。

### B13 Current / Target / Gap / Evidence

Target Contract 见 [`wave1-cross-module-contract-registry.md`](../governance/wave1-cross-module-contract-registry.md)。Current 需要进一步按代码、Provider 和真实运行审计。Gap 包括正式凭证、provider qualification、usage settlement、fallback eval、budget / quota fault test、cancellation race 和不同角色的稳定质量门。

### B14 Code / Database / Migration Constraints

模型 SDK 和 Provider adapter 是可替换实现；上层模块只依赖 Gateway Contract。不得把厂商模型名写进领域对象或 Capability identity。表结构、缓存、batching 和独立服务拆分在详细设计与测量后决定；需要高吞吐时可以 Worker 化，但不因模块名默认变成 Model Service。

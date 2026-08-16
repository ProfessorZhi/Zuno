# 05 Capability & Skill（专业能力与技能）

<!-- status: design-baseline-v1; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么“能调用一个函数”还不等于专业能力

Zuno 的法律能力可能来自论文算法、规则系统、大模型、微调模型、开源组件、外部 API 或 MCP。真正需要稳定的不是某个 Python 函数或某个模型名字，而是“上层怎样知道这个能力能做什么、接受什么输入、返回什么、在哪些条件下可信，以及版本变化后还能不能继续使用”。

专业能力与技能模块把这种专业语义从具体 Provider 中抽出来，使研究成果可以逐步变成可组合、可测试、可替换的工程能力。

### Capability 和 Skill 在这里怎样理解

Capability（专业能力）是对外稳定的专业语义，例如事件抽取、事件对齐、冲突检测、事实—法条对应、类案检索、法律适用性或证据推理。它回答“这项能力承诺完成什么专业任务”。

Skill（技能）更接近一种可复用实现或组合包装：它可能由 Prompt、规则、模型、工具、检索或若干步骤组成，用来实现一个或多个 Capability。Skill 可以替换、拆分或重写，但不因为存在某个 Skill 文件就自动拥有正式业务权威。后续详细设计如果发现 Skill 没有独立生命周期价值，也可以继续把它保持为实现层概念，而不扩大领域模型。

### 从研究成果到可用能力需要经过什么

一个论文算法或实验脚本不能因为“Demo 效果不错”就直接进入产品。目标工程化链路是：

```text
Research Artifact（研究成果）
→ Domain Capability（专业能力定义）
→ Versioned Provider（版本化实现）
→ Conformance / Evaluation（契约与质量验证）
→ Eligibility（当前可用资格）
→ Runtime / Host 调用
```

研究成果首先要被说明“解决什么问题、输入是什么、输出是什么、适用范围是什么”；Provider 再证明自己满足这份 Contract；最后由评测证据决定它是否可以用于某类任务。这样能力不会因为更换模型或服务就重新定义业务含义。

### 输出为什么只能是候选

专业能力可以说“这里可能存在冲突”“这条材料可能支持某个主张”“这些法条可能适用”，但它不能直接宣布一个 Finding 已经成为正式法律事实。它输出的是候选、观察、引用或建议，后续还要经过证据、权限、质量判断和必要的人审。

这条边界让能力模块可以大胆使用模型和研究算法，同时不让不确定性直接污染 Canonical Domain State（正式领域状态）。

### Planner 为什么必须知道能力边界

如果 Planner 只看到一个名字叫“法律分析”的万能能力，它很容易生成一个无法验收的巨大 Step。能力定义应该让 Planner 至少知道：适用任务、输入前置条件、输出类型、是否需要某类证据、是否有副作用、成本 / 时延级别和当前资格。

Planner 不需要理解 Provider 内部实现，但必须知道“这项能力现在能不能做这一步”。Provider 变化导致能力语义变化时，也必须显式暴露，不能让 Planner 继续按旧假设运行。

### 它和模型网关为什么不能合并

模型网关回答“怎样安全、统一地调用一个模型角色”；专业能力回答“怎样完成一个法律专业任务”。一个事件抽取能力可以用大模型实现，也可以用规则或微调模型实现；如果把能力语义直接绑到模型路由，换模型就等于改业务 Contract。

因此模型网关是 Provider 调用基础设施，Capability 是业务可组合语义。Capability 可以调用 Model Gateway，但不由某个模型供应商定义。

### 它和工具运行为什么必须分开

专业能力回答“应该怎样分析”；工具运行回答“是否以及怎样对外执行动作”。一个法律适用性算法即使内部调用外部服务，也不因此拥有现实副作用语义；一个向法院系统提交结果的动作，也不能因为使用了 Tool 就获得法律专业正确性。

两者可以物理上共用 Python Worker，但成功、失败、恢复和安全含义必须分开。能力失败通常意味着“分析没有得到可信候选”，工具失败可能意味着“现实世界结果未知”，恢复方式完全不同。

### 能力变化时为什么有时重试、有时重规划

Provider 暂时超时、限流或短暂不可用，只要 Capability Contract 没变，通常可以在预算和安全条件允许时重试或切换已验证的等价 Provider。

如果输入 Schema、输出语义、适用范围或最低证据要求已经变化，原计划依赖的能力假设就失效。这时不是继续猜参数，而是通知运行控制重新解析能力并可能 Replan。没有等价替代时，应该停止、降级为草稿或交人工，而不是静默换一个语义不同的 Provider。

### 为什么值得独立成一个责任域

如果所有专业能力都散落在 Agent Prompt、Tool wrapper 和业务服务里，Planner 无法知道 Executor 真正能做什么，测试也无法区分是能力退化、模型退化还是运行控制错误。研究成果也会长期停留在“某个 Prompt / notebook 能跑”的状态。

独立能力边界为研究成果提供工程化出口，也让同一个专业能力可以拥有多个 Provider、统一质量门和稳定上层 Contract。

### 当前、目标与缺口

仓库已经存在能力、工具、模型 Provider 和跨模块 Contract 相关实现，但当前证据没有证明九模块下的 Capability Registry、Provider Conformance、Eligibility 和 Planner Awareness 已经作为完整 Current 模块运行。本文件冻结目标方向，不把目录、类名或 Prompt 的存在写成完成证据。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

Capability Contract 与 Provider 实现分离；Provider 更换不能静默改变专业语义；能力输出只能是 Proposal / Candidate / Observation / Reference；Planner 不生成超出当前 Capability / Executor 边界的巨大 Step；Capability 不直接执行未经审批的现实副作用。

### B2 Responsibility / Ownership

**Owns**：Capability identity / version、专业语义 Contract、Skill / provider binding、provider conformance、capability eligibility、专业 Proposal / Candidate / Observation / Reference、capability deprecation / compatibility 语义。

**Does not own**：Canonical Domain admission、Tool Effect execution、Authorization / Approval、Model routing、Runtime Plan ownership、最终发布资格。

### B3 Upstream / Downstream

上游主要消费 03 的版本化证据引用、08 的当前 Scope / 安全决定、04 的 Step requirement，以及必要的 07 模型结果或 06 只读工具结果。下游向 04 返回 capability metadata / eligibility / typed output，向 02 提供专业候选和 evidence refs，向 09 输出 conformance / quality signal。

### B4 Authoritative Facts / Core Objects

核心对象族包括 Capability Definition、Capability Version、Provider Binding / Provider Version、Conformance Result、Eligibility、Skill package / composition reference、typed Proposal / Candidate / Observation / Reference。具体 Registry 存储形态尚未冻结。

### B5 Cross-boundary Contracts

每个 Capability 至少需要稳定 identity、version、input / output schema、semantic purpose、preconditions、evidence requirement、uncertainty / failure signal、provider compatibility 和 observable quality evidence。Runtime 消费 Capability 资格而不是 Provider 目录；Model Gateway / Tool Runtime 只作为实现依赖。

### B6 Normal Flow

research artifact → define capability semantics → register version → bind provider implementation → conformance test → legal / task eval → mark eligible for defined scope → Runtime / Host invokes capability → typed candidate output → downstream acceptance / admission。Provider 新版本必须重新通过与变化风险匹配的 conformance / eval。

### B7 State / Lifecycle

至少区分 draft definition、registered version、provider bound、conformance passed / failed、eligible / restricted / deprecated，以及 output-level success / insufficient evidence / unsupported / failure。详细 enum 后续冻结，但版本和资格必须可追溯。

### B8 Failure Taxonomy

主要失败包括 transient provider error、schema drift、semantic drift、unsupported input、insufficient evidence、quality regression、provider unavailable、capability version incompatible、planner request 超出能力边界、内部工具 / 模型依赖失败。

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

Provider 临时错误且语义未变时可重试；同一确定性 capability invocation 应通过稳定 invocation identity 避免重复昂贵计算。Schema / semantic drift、前置条件变化或能力被撤销时通知 04 重新规划。Capability 不拥有现实 Effect Reconcile；若内部需要有副作用工具，必须通过 06 执行并消费其 receipt。

### B10 Security / Approval / Audit

能力调用消费当前数据 Scope、模型外发和工具权限。Capability definition 可以声明需要的安全 / 数据条件，但授权真相仍由 08 决定。Provider 不直接拿长期秘密，秘密访问通过受控 Secret / Credential 引用。

### B11 Persistence / Transaction Boundaries

Capability registry 是否落 PostgreSQL 取决于是否需要跨进程一致版本和生命周期；第一原则是先稳定 identity / version / conformance / eligibility 语义。Provider 运行结果和大型中间产物不默认进入领域数据库，正式业务状态仍由 02 准入。

### B12 Observability / Evaluation

至少记录 capability version、provider reference、input / output schema hash、latency、cost、quality signal、failure class、evidence sufficiency 和 downstream acceptance。评测应能区分“Provider 调用成功”与“专业结果有用”，并支持同一 Capability 的 Provider A/B。

### B13 Current / Target / Gap / Evidence

Target 已由 ADR-0008 / ADR-0013 确认能力与 Tool Runtime 分离。Current 模块级 registry / conformance 证据尚未完成专项审计。Gap 包括 Capability Registry、version compatibility、provider conformance test、法律 Eval、Planner capability awareness、deprecation / rollback 和 research-to-capability E2E。

### B14 Code / Database / Migration Constraints

不要为每个研究算法新建微服务，也不要把 Provider SDK 暴露给所有上层模块。先冻结 capability identity、version、contract、eligibility 和 provider compatibility，再决定 registry 数据库和 API。Skill 如果只是实现包装，不得因为目录存在被升级为独立 Canonical 业务对象。

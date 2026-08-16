# 05 Capability & Skill（专业能力与技能）

<!-- status: design-skeleton; implementation: not-authorized -->

## Part A — Human Narrative

### 为什么“会调用一个函数”还不等于专业能力

Zuno 的法律能力可能来自研究算法、规则系统、LLM、微调模型、开源组件、外部 API 或 MCP。真正需要稳定的不是某个实现，而是“上层怎样知道这个能力能做什么、接受什么输入、返回什么、在哪些条件下可信”。

专业能力与技能把这种专业语义从具体 Provider（提供方）中抽出来，使研究成果可以逐步变成可组合、可测试、可替换的工程能力。

### 从研究成果到可调用能力

一个论文算法或实验脚本不能因为“效果不错”就直接进入产品。它需要经历一条明确的工程化链路：研究产物先被整理成领域能力，能力有稳定版本，再绑定一个或多个实现 Provider，经过契约一致性和评测后，才获得被 Agent 或宿主调用的资格。

```text
Research Artifact
→ Domain Capability
→ Versioned Provider
→ Conformance / Evaluation
→ Eligible for Use
```

事件抽取、事件对齐、冲突检测、事实—法条对应、类案检索、法律适用性和证据推理都可以沿这条路径进入系统。能力目录不是“插件市场”，核心是说明能力语义和资格，而不是收集尽可能多的工具。

### 输出为什么只能是候选

专业能力可以说“这里可能存在冲突”“这条材料可能支持某个主张”“这些法条可能适用”，但它不能直接宣布一个 Finding 已经成为正式法律事实。它输出的是候选、观察、引用或建议，后续还要经过证据、权限、质量和必要人审。

这条边界允许能力大胆使用模型和研究算法，同时不让不确定性直接污染正式领域状态。

### 它和工具运行为什么必须分开

专业能力回答“应该怎样分析”；工具运行回答“是否以及怎样对外执行动作”。一个法律适用性能力即使内部调用远程模型，也不因此获得现实副作用的权威；一个向法院系统提交结果的动作，也不能因为使用了 Tool 就获得法律专业正确性。

两者可以物理上共用同一个 Python Worker，但成功、失败、恢复和安全含义必须分开。

### Planner 为什么需要知道能力边界

如果 Planner 只看到一个含糊的“法律分析工具”，它很容易生成一个巨大步骤，要求执行器一次完成材料抽取、冲突识别、法条适用和最终结论。能力边界应该让 Planner 知道输入要求、输出类型、成本/质量特征和不能做什么，从而生成可执行、可评测的 Step。

Provider 临时超时通常可以重试；但如果能力版本的输入、输出或语义已经变化，原计划依赖的假设可能不再成立，这时应该让运行控制重新规划，而不是不断用旧参数重试。

### 为什么值得独立成一个责任域

如果所有专业能力都散落在 Agent Prompt、Tool wrapper 和业务服务里，Planner 无法知道 Executor 真正能做什么，测试也无法区分是能力退化还是运行控制错误。独立能力边界让研究成果有明确工程出口，也使底层实现可替换而不改变上层业务语义。

### 当前、目标与缺口

仓库已经存在一批能力、工具和 Provider 相关实现与 Cross-module Contract，但当前证据没有证明“九模块下的 Capability Registry / Conformance / Eval”已经作为完整 Current 模块运行。本文件因此只冻结目标方向，不把目录或 class 存在写成完成证据。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Owns**：Capability identity / version、专业语义 Contract、provider conformance、capability eligibility、专业 Proposal / Candidate / Observation / Reference。

**Does not own**：Canonical Domain admission、Tool Effect execution、Authorization、Model routing、Runtime Plan ownership。

### B2 Target Capability Families

第一阶段可覆盖事件抽取、事件对齐、冲突检测、事实—法条对应、类案检索、法律适用性、证据推理等。列表是能力族方向，不自动要求每项都实现。

### B3 Inputs / Outputs

输入：版本化材料/证据引用、明确 task requirement、当前权限/能力资格引用、必要模型或工具调用结果。

输出：typed proposal / candidate / observation / reference、capability version、provider evidence、failure / uncertainty signal。

### B4 Provider / Eligibility Boundary

Provider 可以是本地算法、LLM、fine-tuned model、OSS、API、MCP 或其他服务。Capability Contract 归本模块；网络、进程和存储只是实现。

能力可用性不能只看“endpoint 健康”。Provider version、schema、semantic conformance 和必要 eval 共同决定当前 eligibility；drift 必须显式暴露，不能静默改变能力语义。

### B5 Failure / Recovery

- transient provider error：在能力语义未变时可重试。
- schema / semantic drift：通知 Runtime 重新解析并可能 Replan。
- insufficient evidence：返回不确定/不可接受，不编造完整结果。
- provider unavailable：按已批准替代链降级；没有等价替代则停止或人工。

### B6 Security / Observability

能力调用消费当前数据 Scope 和模型/工具安全决定。记录 capability version、provider reference、input/output schema hash、quality signal 和 trace reference，但不把敏感正文或秘密材料无约束导出。

### B7 Current / Target / Gap

Target 已由 ADR-0008 / ADR-0013 确认能力与 Tool Runtime 分离。Current 模块级 conformance 证据尚未完成专项审计。Gap：Capability registry、version compatibility、provider conformance test、法律 eval 与 Planner capability awareness。

### B8 Code / Database / Migration Constraints

先冻结 capability identity、version、contract 和 eligibility，再决定 registry 是否需要数据库。不要为每个研究算法新建微服务，也不要让 Planner 生成超出 Executor / Capability 能力边界的巨大 Step。

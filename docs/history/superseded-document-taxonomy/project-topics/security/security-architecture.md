# Security Architecture：谁可以做什么？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 身份、权限、Secret、Sandbox、网络和副作用如何形成可验证边界？
owner: Security Decision Owner
replaces: docs/project/modules/09-security.md（Superseded）

## Part A — Architecture Narrative

### 安全要保护的对象

法律场景的安全目标不是堆叠最多的安全功能，而是让每次读取、模型调用和外部动作都能说明谁在什么 Tenant、Matter 和 Scope 下，以哪一版权限，访问了什么对象，产生了什么结果。安全边界必须同时保护材料机密性、租户隔离、工具副作用和审计可追溯性。

### Threat Scenario：恶意文档诱导外部动作

这是 Target Scenario，不是历史事实：

Matter 文档中包含 Prompt Injection，诱导 Agent 把案件内容发送到外部 API。Agent 可以提出 PreparedAction，但不可信内容不能改写 Grant、SecurityEpoch、Secret Scope 或 Approval。执行前 Security Owner 重新授权，必要时由 Human Approval 放行，Sandbox 执行并生成 EffectReceipt。若撤权、参数、ToolVersion 或 Secret 变化，旧授权失效。

安全的 Happy Path 是：识别主体与 Matter → downscope → 校验 PreparedAction → 当前 Epoch 授权 → 必要时人工批准 → Sandbox 执行 → Receipt 与 Audit；任何一步失败都不能静默执行。

### 责任边界

Security Owner 负责 Principal、Tenant、Grant、Policy、SecurityEpoch、Approval、Secret Scope 和 Audit Authority；Platform/Domain 保存业务权限引用；Runtime 负责执行时携带上下文；Tool/Sandbox 负责强制网络、文件、Secret 和 Effect 边界。Security 不拥有 Finding 或 Agent Plan，也不允许 Agent、Provider 或文档内容自行提升权限。

### 为什么需要执行时授权

只在 Plan 创建时授权无法处理长任务中的角色变更、撤权、Secret rotation、Tool version 和参数变化。执行时授权和 Receipt 增加延迟、审计和策略复杂度，但能把“计划想做什么”和“当前允许做什么”分开。若外部 Host 能提供同等的 Epoch、Approval、No-egress、Secret Trace 和副作用对账证据，Zuno 不应重复建设安全执行层。

### 失败、取舍与反转

Prompt Injection、跨租户查询、过期凭据、Sandbox escape、Tool timeout 和 duplicate effect 都必须 fail closed 或进入未知结果对账。权限在长 Run 中被撤回时，Queue 里的 PreparedAction 仍然只是候选；执行 Worker 必须用当前 SecurityEpoch 重新授权，不能因为旧 Approval 还在消息里就继续执行。开源不天然安全，闭源也不天然不安全；Zuno 的候选差异是 Security Verifiability 和 Deployment Sovereignty。若真实测试不能证明安全边界，不能把安全目标写成 Current 或 Production 事实。

### Current / Target / Gap

Current 只由实现、配置、测试、Trace 或 Attestation 证明；Target 是逐服务执行策略、Sandbox 隔离、最小权限和可审计 Effect；Hypothesis 是自托管可验证性降低审计不确定性；Gap 是 no-egress、Secret、跨租户、撤权、Sandbox 和制品证明。

## Part B — Detailed Architecture Specification

### Authorization and Effect Contract

PreparedAction 必须绑定 action hash、Subject、Tenant、Matter、Scope、ToolVersion、Arguments、EffectScope、SecurityEpoch、Approval 和 Expiry。执行前重新计算授权，执行后写 ToolAttempt、EffectReceipt、ProviderOperationId 和 Audit Record。Read-only、reversible、irreversible Effect 使用不同 Approval、Retry 和 Reconciliation 策略。

### Effect State and unknown outcome

Effect 状态包括 proposed、validated、authorized、approval_required、ready、executing、succeeded、failed_known、outcome_unknown、reconciling 和 manual_review。Timeout 不能直接等于 failed；不可逆动作的 outcome_unknown 必须先依据 ProviderOperationId 对账，禁止盲目 Retry。

每次 Execute 使用稳定 Idempotency Key；重复请求必须返回同一 EffectReceipt 或明确的 reconciliation 状态，不能依靠模型记忆去重。

### Revocation race and execution gate

PreparedAction 的准备时间不等于执行授权。Worker 取出队列消息后重新读取 Grant、SecurityEpoch、Approval、ToolVersion、Arguments 和 Secret Lease；任何一个版本变化都使旧动作进入 rejected、expired 或 manual_review。取消请求与 Provider 已收到请求并不互相覆盖，系统必须保留 cancel_requested、executing、outcome_unknown 和 reconciling 的顺序。

### Secrets、Sandbox 与 Network

Secret 只以 scoped lease 提供，不写入 Prompt、Trace 或普通日志；Network Allowlist、No-egress Profile、Filesystem Scope 和资源限制由 Sandbox 强制。工具参数来自不可信内容时必须经过 Schema、Policy 和 Approval，Prompt Injection 不能改变 Policy Decision。

### Audit、revocation 与 observability

每次 authorization、model invocation、tool execution、Domain Decision 和 Human Decision 记录 Principal、Tenant、Matter、Scope、PolicyEpoch、Trace、版本、结果和失败类型。撤权、Secret revoke、ToolVersion、Arguments 或 SecurityEpoch 变化使旧 Approval 失效。安全证据必须包括 SBOM、签名制品、Egress Audit、Secret Leakage、Cross-tenant、Prompt Injection、Sandbox Escape 和 Duplicate Effect Test。

### Testing and qualification gap

Target Contract 需要单元、集成、故障注入和部署级测试；Repository 中的安全模块或配置不等于实测安全。生产或合规结论必须等真实运行、Attestation、HA、备份和外部资格证据。

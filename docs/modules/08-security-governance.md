# 08 Security & Governance（安全与治理）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块保护的不是“用户是否登录”，而是“下一步现在还能不能做”

复杂法律任务可能持续几十分钟，中间等待人工、检索多批材料、调用多个模型、重规划并执行外部动作。期间用户权限、事项归属、数据密级、模型外发政策、审批状态和凭证版本都可能变化。

如果安全只在请求入口做一次 `allowed=true`，后台 Worker 会把这次结果当成永久通行证。08 因此拥有持续安全判断：当前主体在当前时刻，针对当前资源和用途，是否还能执行下一次受保护动作。

### 最简单的“登录 + RBAC”为什么覆盖不了长任务

登录和基础角色控制非常重要，但它们只能确认一个会话和粗粒度权限。任务开始后，资源版本、Matter scope、purpose、政策和审批都可能变化。

例如用户开始时能读附件 A，十分钟后管理员撤销权限。已经合法完成的历史读取仍然发生过，但下一次从索引恢复正文、向模型外发或执行依赖 A 的 Tool 时，都必须重新检查当前条件。

### Continuous Authorization（持续授权）到底意味着什么

`Continuous Authorization（持续授权）` 不是不停轮询一个布尔值，而是在新的受保护边界到来时重新消费当前安全事实。材料读取、模型外发、Secret 使用、现实 Tool Effect 和 Formal Admission 都是典型门点。

这样权限变化控制未来动作，不试图改写过去。系统也不需要为每个 token 做远端鉴权，只需要在真正产生新的安全风险时有明确检查点。

### 为什么三种“人点同意”必须拆开

有没有权限执行某动作，是 Authorization；一个具体高风险动作是否得到规定人员批准，是 Approval；专业人员是否接受、修改或拒绝法律业务结论，是 HumanDecision。

所以保持 `AuthorizationDecision、ApprovalDecision、HumanDecision 三者 Owner 与语义不同`。同一个 UI 可以呈现三种按钮，但架构不能因为交互相似就让它们拥有相同后果。

### Approval 为什么必须绑定具体动作而不是 Step 编号

如果只记录“Step 17 已批准”，Replan 后 Step 17 的目标、参数、ToolVersion 或 EffectClass 可能已经改变。继续复用旧批准就会变成“人批准 A，系统执行 B”。

Approval 应绑定稳定 action identity / hash、目标、关键参数摘要、版本和 SecurityEpoch。会影响现实或安全语义的内容变化后，旧 Approval 失效并重新申请。

### 模型外发为什么由安全策略决定，不由 Model Gateway 决定

07 能判断 Provider 技术可用、模型质量合格和当前预算允许，却不能自己决定一份法律材料是否可以发往某个 Provider / region。

数据分类、事项范围、用途、地域和合同政策由 08 形成 egress decision。07 只能在允许集合里路由；fallback 不能成为绕过数据政策的理由。

### Secret 为什么只传引用和短期 Lease

API Key、数据库凭证和外部法院系统令牌如果为了恢复方便写进 Prompt、Checkpoint 或普通日志，会把一次受控使用变成长期泄露面。

Target 让执行模块消费 SecretRef / CredentialVersionRef / LeaseRef 一类受控引用。恢复保存“当时使用了哪个受控凭证版本和用途”，不保存秘密明文。

### Mandatory Audit 为什么和普通 Trace 不是一回事

某些高风险现实动作要求在执行前就证明谁发起、基于什么授权、谁批准、准备执行什么。普通 Trace 可能被采样、网络失败或晚到，不能承担这种前置合规证明。

如果策略要求 `MANDATORY_BEFORE_EFFECT`，必须先获得耐久 `AuditPersistenceReceipt`，06 才能继续发送。事后补一个 OTel / LangSmith span 不能倒推当时已经满足强制审计。

### Prompt Injection 为什么不能靠“更聪明的模型”解决

材料正文可能包含恶意指令，模型也可能生成越权 Action Proposal。安全不能依赖模型“自己知道不能做”。

03 控制可读材料，07 控制模型外发，04 不允许模型绕过 Plan / Budget，08 决定授权与审批，06 在真实副作用前再次验证动作。多层确定性门禁使模型输出保持 Proposal，而不是权限来源。

### 数据生命周期为什么不能只有 deleted=true

法律数据可能同时受到用户删除请求、Retention、Legal Hold、索引召回限制和物理清除流程影响。“不能再被检索”与“底层所有字节已经物理删除”不是同一个事实。

所以保持 `Retention != Recall Eligibility != Physical Purge Completion`。08 决定当前生命周期政策，各 Store 执行自己的义务并产生 enforcement fact；任何单个 Store 都不能替整个系统宣布全局删除完成。

### 为什么跨 Store 删除不应该追求一个巨大 2PC

领域库、索引、对象存储、缓存、Checkpointer 和外部 Provider 不在同一事务系统里。强行做全局原子删除不仅成本高，也无法让外部系统真正参与本地 2PC。

更合理的方式是政策先确定，各 Store 按自己的事务边界执行并记录结果，治理层根据这些事实收敛。局部失败保持可见并重试，而不是用一个 `deleted=true` 掩盖未完成部分。

### 安全服务不可用时为什么高风险路径默认 fail closed

授权引擎不可用、SecurityEpoch 无法确认、Approval 不可验证、Secret Lease 获取失败或强制审计不能落盘时，高风险动作缺少必要前提。

因此受保护材料、模型外发、Secret、Tool Effect 和 Formal Admission 默认 fail closed 或进入人工复核。低风险诊断是否允许降级必须由显式策略定义，不能由每个模块临时选择 fail open。

### 撤权发生在不同时间点为什么结果不同

如果撤权发生在模型或 Tool 发送前，后续动作应被阻断；如果请求已经发出，撤权不能把已经外发的数据“收回来”，也不能把已经发生的现实 Effect 改写成未发生。

晚到结果在继续使用、发布或正式准入前仍要重新检查当前条件。持续授权控制未来使用，不修改过去已经真实发生的历史。

### SecurityEpoch 为什么是新鲜度边界

策略决定需要知道自己基于哪一版安全规则。SecurityEpoch 让消费者识别旧 allow 是否仍适用于新的受保护动作。

它不要求全系统共享一个巨大配置事务，只要求安全决定稳定绑定政策版本，并让新的门点能判断语义相关的政策是否已经变化。

### Decision Cache 为什么不能变成永久 Capability Token

高频访问为了性能可以缓存 AuthorizationDecision，但 cache 只能降低评估成本，不能延长权限寿命。只按 user id 缓存 allow，很容易在 Matter、resource version 或策略变化后继续误放行后台任务。

cache key 和 expiry 必须覆盖真正影响安全语义的条件，并受 SecurityEpoch 约束。新的受保护动作仍然要判断缓存决定是否仍适用。

### 多租户隔离为什么必须跟着资源引用走

只在 HTTP session 保存 tenant 不够，因为后台 Worker、异步恢复和 Cache 经常脱离原请求上下文。材料、Domain object、PreparedAction、Model request 和 Delivery 都要能证明属于哪个受保护 Scope。

可以跨模块传播 opaque scope ref，避免把敏感 tenant / matter 名称塞进普通 Trace。隔离是业务和安全事实，不是日志标签。

### 什么时候 08 应该更简单

低风险内部工具如果没有多租户、敏感外发、现实副作用和复杂数据生命周期，安全层可以主要复用成熟身份系统、RBAC 和 Secret Manager，不需要自造完整 Policy Platform。

Zuno 只应保留法律业务真正需要的持续授权、动作审批、外发政策和生命周期语义。Policy Engine、Secret infrastructure 和身份目录能买就买，08 负责的是权威边界，不是重复实现基础设施。

### Policy Decision 和 Policy Enforcement 为什么必须分开

08 可以计算“当前允许/拒绝/需要审批”的安全决定，但真正读取文件的是 03，调用 Provider 的是 07，执行 Effect 的是 06，提交 Domain 的是 02。只有 Decision 没有 Enforcement，安全仍然只是纸面规则。

因此每个受保护边界既要知道去哪里取得权威 Decision，也要在自己的真实执行点 fail closed。08 不需要亲自代理所有 I/O，但要让消费者无法用“我已经拿到数据了”绕过当前政策。

这种分离也避免建立一个所有业务流量都必须穿过的巨大 Security Proxy；策略 Authority 集中，执行门分布在真正产生风险的位置。

### Security Freshness 为什么不等于把 TTL 设得极短

把授权缓存 TTL 设成一秒看似“持续”，却会制造大量远端 Policy 请求，同时仍不能精确表达策略何时变化。更有意义的是让 Decision 绑定 SecurityEpoch / resource version / purpose，并在新的受保护边界判断这些前提是否仍成立。

TTL 可以作为性能和最坏撤权延迟的一部分，但不是唯一正确性机制。关键政策变化可以推进 epoch，使旧 allow 立即失去复用资格；不相关配置变化则不必让所有缓存同时失效。

新鲜度设计最终应该能回答撤权传播上限，而不是只展示一个很小的缓存数字。

### 可信身份为什么不能来自调用方自己提交的字段

前端或 Host 可以携带 tenant、role、matter 等字段，但这些值只是输入声明，不是权限事实。如果后台 Worker 直接相信请求里的 `role=admin` 或 tenant id，攻击者就可以通过修改参数提升权限，异步恢复也会失去可信身份来源。

可信 principal、tenant membership 和 role 必须来自经过验证的身份上下文、受控目录或可信 Host assertion。01 可以负责认证协议和上下文绑定，08 决定这个主体当前能做什么；Prompt、材料正文、模型输出和 Tool 参数都不能把自己升级成权限来源。

这个边界也解释了为什么多租户 Scope 要随着资源引用传播：离开原 HTTP 请求以后，系统仍然要知道当前动作依赖哪个可信身份和事项范围，而不是从普通业务字段重新猜。

### Approval 为什么自己也有生命周期

一次批准不是永久通行证。动作参数、目标资源、ToolVersion、SecurityEpoch、有效期或审批策略发生语义相关变化后，旧 Approval 可能已经不再适用；被撤销或过期的批准也不能因为某个 Runtime Checkpoint 仍写着 granted 就继续使用。

因此 Approval 需要区分 pending、granted、denied、expired、revoked、invalidated 等足以支持当前门禁的状态，并始终绑定它实际批准的动作。这里的重点不是制造复杂审批工作流，而是确保“曾经有人点过同意”不会被误解成未来任意版本动作的权限证明。

### Audit 数据本身为什么也需要最小化和生命周期

审计必须足够解释谁在什么条件下做了什么，但不意味着把完整 Prompt、材料正文和 Secret 全量复制进审计库。过度记录会创造新的高敏感数据仓库。

Audit record 应优先保存身份引用、动作 hash、资源版本、Decision / Approval refs 和必要非敏感摘要，需要查看正文时回到受控 Owner store。审计自身同样受 Retention、Legal Hold 和访问控制约束。

这样耐久性和数据最小化可以同时成立，而不是“为了审计所以什么都永久保存”。

### 安全平台哪些应该 Buy，哪些必须由 Zuno 定义

身份 Provider、Secret Manager、KMS、Policy Engine 和标准审计存储都可以优先复用成熟产品。Zuno 不需要重新实现密码学、OIDC 或 Vault。

但“什么动作属于高风险法律 Effect”“什么材料允许发给哪个模型”“Approval 应绑定什么 action identity”“Formal Admission 前需要什么当前安全事实”是业务语义，不能期待通用产品自动知道。

所以 08 的自有价值在 policy model 和跨模块 Authority contract，而不是基础设施数量。成熟组件越多，Zuno 自己的安全代码反而应该越薄、越聚焦。

### 安全拒绝为什么也需要可解释，而不是只返回 403

高风险系统必须 fail closed，但如果拒绝只有一个通用 `DENY`，工程师和业务人员无法判断是权限不足、数据外发限制、Approval 缺失、SecurityEpoch 过期、Secret 不可用还是 Legal Hold 导致。结果往往是调用方为了“修复可用性”绕开门禁。

08 因此应该返回最小但可解释的 decision reason / requirement：告诉消费者下一步是禁止、等待审批、重新获取当前决定、切换允许 Provider，还是必须人工处理。敏感策略细节不必暴露给不可信客户端，但可信内部模块需要足够信息选择正确恢复路径。

可解释拒绝并不意味着上层可以修改安全判断。01 可以把原因翻译成用户行动，04 可以等待或 Replan，07 可以换到允许的 Provider，但只有 08 能在条件变化后形成新的 Authorization / Approval 事实。

### Authorization 到真正执行之间为什么还存在 TOCTOU 风险

即使 08 在某一时刻返回 ALLOW，执行模块真正读取文件、发送模型请求或越过 Tool send boundary 之前仍可能经过排队、重试和人工等待。期间 SecurityEpoch、资源版本或 Approval 都可能变化，这就是典型的 time-of-check / time-of-use 问题。

解决方式不是把所有动作塞进一个巨大安全事务，而是让 Decision 绑定关键前提，并在真正产生风险的边界尽量晚地验证当前适用性。已经发生的历史动作不回滚，尚未发生的新动作则不能拿旧 allow 当永久票据。

因此“拿到 AuthorizationDecision”只是满足门禁的一部分，消费者还必须确认它仍匹配当前资源、动作和 policy epoch。

### 后台 Worker 为什么不能继承用户的全部长期权限

异步任务离开 HTTP 请求以后，如果直接保存一个长期用户 token 或管理员 Secret，任何后续 Step 都可能拥有超过自己需要的权限，凭证泄露的影响面也会被放大。

更合理的是传播稳定 principal / scope refs，在每个受保护边界获得当前 Decision，并让 Secret 通过受用途和时间限制的 lease 使用。Specialist、Subgraph 或 Tool Worker 的权限上限不能高于触发它的合法 Scope，也不能因为它是“系统内部服务”就自动绕过政策。

这是一种 least-privilege delegation：长期保存的是身份和因果，不是无限期可执行所有动作的能力。

### “允许执行”为什么不等于“这个动作业务上是正确的”

08 可以证明当前主体有权执行某个动作、数据允许外发、审批满足政策，但它不负责判断模型结论是否正确、Evidence 是否充分、Tool 参数是否符合专业语义。安全 Authority 也不能变成新的 God Validator。

例如一个动作完全有权限，却引用了错误案件版本；这应该由 01/02/03/05/06 的业务与执行语义拦截。反过来，一个专业结果再正确，如果当前没有授权，也不能越过 08。

把 permission 与 correctness 分开，可以防止“Security 已经 allow，所以后面无需校验”的危险推断。

### Policy 版本升级为什么也需要兼容和可回溯

安全策略会演进：某类模型 Provider 可能被禁止，Approval 门槛可能提高，数据生命周期规则也可能变化。如果只覆盖一份全局配置，事后很难解释历史动作为什么当时被允许，也无法区分旧决定是“当时合法”还是“现在仍适用”。

SecurityEpoch / PolicyVersion 的价值就是把历史 Decision 绑定到当时规则，同时让新动作识别政策已经变化。策略发布机制可以复用成熟 Policy Engine，但 Zuno 需要保留足够版本和 reason，支持回溯、撤权传播和安全回归测试。

策略升级的目标不是让过去瞬间变非法，而是让未来受保护动作按新规则收敛，并能解释这个边界发生在什么时候。

### 当前、目标与缺口

Current 是否已有 Policy Engine、SecurityEpoch、Approval binding、Secret Lease、durable audit 和 per-store lifecycle enforcement，必须由代码和安全测试证明；Target 设计不能冒充实施完成。

Target 已明确持续授权、Authorization/Approval/HumanDecision 分离、强制审计前置、外发决策和生命周期语义。Gap 包括策略语言、真实身份集成、撤权延迟、Decision Cache 性能、安全 fault injection、Legal Hold / purge 实现和生产合规证据。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

1. `Continuous Authorization（持续授权）`：新的受保护访问必须消费当前有效安全事实。
2. AuthorizationDecision、ApprovalDecision、HumanDecision 三者 Owner 与语义不同。
3. Approval 必须绑定 action identity / action hash；动作语义变化后不得复用旧批准。
4. Model Provider technically available != data egress permitted。
5. Secret Material 不进入普通 Prompt、Checkpoint、Trace、业务 payload 或普通数据库列。
6. `MANDATORY_BEFORE_EFFECT` 要求存在时，committed AuditPersistenceReceipt 是 06 执行的必要条件。
7. Retention != Recall Eligibility != Physical Purge Completion。
8. Policy / Security service 不可用时，高风险路径默认 fail closed。
9. 08 拥有 policy decision；目标 Store / Module 拥有 execution fact。
10. 安全决定不能被 Model、Runtime、Application、Tool 或 Provider 本地默认值放宽。
11. 历史合法事实不因后续撤权被改写；撤权控制新的受保护使用。
12. 不建立跨所有 Store 的安全 2PC。

### B2 Responsibility / Ownership

**Owns**：PrincipalRef / trusted identity assertion policy、Tenant / Matter Scope、SecurityEpoch / PolicyVersion、AuthorizationDecision、ApprovalDecision、ModelEgressDecision、ToolPermissionDecision、Credential / Secret usage policy、EffectiveLifecycleDecision、AuditRequirement、DecisionReason、expiry / refresh semantics、security qualification / policy compatibility。

**Does not own**：02 HumanDecision / Domain Admission；03 knowledge facts；04 Plan / Budget control；06 Effect truth；07 Model usage truth；01 publication / delivery truth；各 Store 的 purge / enforcement completion；09 Telemetry truth。

### B3 Upstream / Downstream

上游接收 01 的 trusted principal / request context、02 / 03 / 04 / 05 / 06 / 07 提交的 resource/action context、Platform 提供的 identity directory / secret-delivery / clock primitives。

下游：03 消费材料读取和检索授权；04 在 resume / retry / replan 后消费新决定；05 消费 capability scope；06 消费 tool authorization / approval / audit / credential refs；07 消费 model-egress / provider / credential decisions；02 在正式准入时消费当前授权；01 在 publication / delivery / validity query 时消费安全事实；09 只消费脱敏 refs。

### B4 Authoritative Facts / Core Objects

核心事实族：PrincipalRef、TrustedIdentityAssertionRef、TenantScopeRef、MatterScopeRef、SecurityEpoch、PolicyVersion、AuthorizationDecision、ApprovalDecision、ModelEgressDecision、ToolPermissionDecision、CredentialVersionRef、SecretRef、SecretLeaseRef、EffectiveLifecycleDecision、AuditRequirement、AuditPersistenceReceiptRef、LifecycleEnforcementRef、DecisionReasonCode、expiry / refresh requirement。

字段和物理表仍是 Target Candidate，不表示 Current 实现已经存在。

### B5 Cross-boundary Contracts

#### AuthorizationDecision

至少绑定 principal、tenant / matter / resource scope、requested action、purpose、data classification、policy epoch、decision outcome、reason、issued / expiry、refresh requirement 和 decision identity。调用方只能消费或重新请求，不能自行放宽。

#### ApprovalDecision

至少绑定 approver principal、approval identity、prepared action identity / hash、operation / ToolVersion、target resource、policy epoch、decision、issued / expiry、revocation / invalidation reason。安全相关参数或 action hash 改变后重新审批。

#### ModelEgressDecision

至少绑定 source data classification / scope、allowed provider / region / processing class、purpose、policy epoch、decision expiry。07 fallback 只能从允许集合中选。

#### EffectiveLifecycleDecision

表达 retention、recall eligibility、purge obligation、legal hold、compliance exception、decision priority / reason 和生效时间。Store 产生自己的 enforcement fact。

#### AuditRequirement / AuditPersistenceReceipt

08 拥有 Requirement；Audit persistence boundary 拥有实际持久化 Receipt。`MANDATORY_BEFORE_EFFECT` 时 06 只接受与当前 action hash / policy epoch 匹配的 committed receipt。

### B6 Normal Flow

```text
protected operation requested
→ resolve trusted principal / tenant / matter / resource / action / purpose
→ load current SecurityEpoch / policy
→ evaluate Authorization
→ evaluate egress / tool / secret restrictions when applicable
→ determine Approval requirement
→ bind Approval to action hash when required
→ determine AuditRequirement
→ require durable AuditPersistenceReceipt when required
→ issue typed decision refs / Secret Lease refs
→ target module re-checks freshness and executes
→ target module records its own execution fact
```

### B7 State / Lifecycle

最终 enum 名称在实现任务中可以调整，但语义必须覆盖：

```text
Policy: ACTIVE → SUPERSEDED / RETIRED
Authorization: EVALUATED → ALLOW / DENY; ALLOW → EXPIRED / REVOKED / SUPERSEDED
Approval: REQUIRED → PENDING → GRANTED / DENIED; GRANTED → EXPIRED / REVOKED / INVALIDATED
Secret Lease: ISSUED → ACTIVE → EXPIRED / REVOKED
Lifecycle: EVALUATED → RETAIN / NO_RECALL / PURGE_REQUIRED / LEGAL_HOLD
Store Enforcement: PENDING → ENFORCED / FAILED / BLOCKED_BY_HOLD
```

### B8 Failure Taxonomy

| 失败 | 权威边界 | 默认处理 | 可自动继续条件 |
| --- | --- | --- | --- |
| identity / tenant / scope 缺失 | 08 | deny / clarification | 获得可信上下文后重新评估 |
| policy engine unavailable | 08 | fail closed | 仅显式低风险降级策略 |
| stale SecurityEpoch | 08 | re-evaluate | 新决定成立后 |
| authorization revoked | 08 + target | block new protected use | 新授权成立后 |
| approval missing / expired | 08 | wait / deny | 新批准成立后 |
| action hash mismatch | 08 + 06 | invalidate approval | 重新审批 |
| model egress denied | 08 | deny / alternate allowed route | 只能使用允许 Provider |
| Secret Lease unavailable | 08 / Platform | wait / stop | 新 lease / allowed credential |
| Mandatory Audit write failed | audit boundary | block Effect | committed matching receipt |
| cross-tenant resource | 08 | deny + durable audit when required | 不自动继续 |
| lifecycle policy conflict | 08 | fail closed / compliance review | 明确新决定 |
| Store purge failed | target Store | keep pending / failed | Store-level Retry |
| prompt injection proposes high-risk Tool | 04/05/06 + 08 | proposal remains non-executable | 全部门禁通过后才执行 |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

Authorization 在相同 principal / resource / action / purpose / policy epoch 下可以稳定重算，但不能无限缓存。SecurityEpoch、资源版本或动作语义变化后必须新评估。

Approval 只在 action hash、ToolVersion、policy epoch、有效期和审批范围仍匹配时复用。Replan 产生新的 PreparedAction 时重新审批。Reconcile 若需要再次访问远端或 Secret，也重新消费当前授权。

恢复锚点是 durable policy / decision / approval / audit facts，而不是 Trace。08 不承担 02 Admission、03 rebuild、06 Effect Reconcile 或 01 Delivery recovery，只在这些恢复过程继续提供当前安全资格。

### B10 Security / Approval / Audit

这是本模块主责。所有门禁都必须明确 fail-open / fail-closed 策略；法律材料越权、模型敏感外发、Secret、高风险 Effect、Formal Admission 和 Mandatory Audit 默认不得因为 Provider 故障而自动放行。

普通日志、Trace 和 Eval 必须数据最小化；Secret NEVER EXPORT。安全审计需要的 durable facts 与 09 Telemetry 分离。

### B11 Persistence / Transaction Boundaries

Policy / SecurityEpoch、需要历史复核的 Authorization / Approval、EffectiveLifecycleDecision、AuditRequirement 和必要 audit refs 需要达到治理要求的耐久度。单个安全决定写入可以在 08 自己的 Store 内事务化，但不与 02 / 03 / 04 / 06 / 07 建立全局 2PC。

高风险 Effect 前的 AuditPersistenceReceipt 必须在独立耐久边界成功；Store 生命周期通过 per-store enforcement facts 收敛。Platform 提供 PostgreSQL、CAS、Lease、Fencing、Secret Delivery、Clock 等物理原语，不改变政策结果。

### B12 Observability / Evaluation

至少观测 decision identity、SecurityEpoch、resource / action class、allow / deny / revoke / expiry reason、approval wait、egress denial、Secret Lease error、audit gate failure、lifecycle enforcement lag、cross-tenant denial。默认只输出 opaque refs 和分类结果。

评测至少覆盖 cross-tenant、no-egress、revocation-during-run、stale credential、secret leakage、approval action-hash invalidation、prompt-injection-to-tool、duplicate effect gate、mandatory audit failure、legal-hold / deletion、policy-engine outage 与恢复后重新授权。

### B13 Current / Target / Gap / Evidence

**Current**：[`current-test-baseline.md`](../evidence/current-test-baseline.md) 证明当前测试入口保留 Security fail-closed、approval binding、artifact authorization、tenant isolation 等有限行为；`docs/evidence/` 仍明确 Full CI、法院 QA、production qualification 未建立。

**Target**：Continuous Authorization + action-bound Approval + Model Egress + Secret Lease + Mandatory Audit + lifecycle governance + tenant isolation 的统一安全边界。

**Gap**：正式 Policy Engine、cross-tenant / no-egress E2E、撤权传播、approval invalidation、credential rotation、prompt injection、legal hold / purge enforcement、audit recovery、法院部署安全资格和生产证据。

**状态**：detail design candidate available；implementation / qualification / production readiness not established。

### B14 Code / Database / Migration Constraints

- 不预冻结独立 Security Service；优先模块化实现和 typed decision ports。
- 不允许任何消费者用本地默认值放宽安全策略。
- 不允许明文 Secret 进入普通业务持久化、Checkpoint、Prompt 或 Trace。
- 不把 HumanDecision 合并进 ApprovalDecision。
- 不把 Store 生命周期执行压成一条全局 `deleted=true`。
- 不默认引入跨 Store 2PC、全局分布式锁或事件溯源。
- 物理服务拆分继续受 ADR-0012 Evidence Gate。

#### B14.1 Detail Freeze Candidate：Authorization / Approval 字段组

`AuthorizationDecision` candidate 至少包含：`decision_id`、`principal_ref`、`tenant_scope_ref`、可选 `matter_scope_ref`、`resource_ref / resource_version_ref`、`action`、`purpose`、`data_classification`、`policy_version / security_epoch`、`outcome`、`reason_code`、`issued_at`、`expires_at / refresh_after`、必要 `provider / region / tool class constraints`。

`ApprovalDecision` candidate 至少包含：`approval_id`、`approver_principal_ref`、`prepared_action_ref`、`action_hash`、`tool_version / operation_ref`、`target_resource_ref`、`policy_version / security_epoch`、`outcome`、`issued_at`、`expires_at`、`revoked_at`、`invalidation_reason`。

Decision identity 与 execution identity 分离。`ALLOW` / `GRANTED` 不能直接作为 ToolAttempt、ModelCall、DomainVersion 或 Publication completion proof。

#### B14.2 Detail Freeze Candidate：Policy / SecurityEpoch 与缓存新鲜度

安全缓存 key 必须覆盖真正影响语义的 principal、tenant / matter、resource version、action、purpose、policy epoch 和必要数据分类。缓存 TTL 只能进一步缩短资格，不能超过 Decision 自身 expiry。

策略变更如果影响授权语义，必须产生新的 SecurityEpoch / PolicyVersion；旧 Decision 在新的受保护访问中重新评估。消费者可以持有 decision ref 做历史关联，但不得把旧 ref 当永久 capability token。

#### B14.3 Detail Freeze Candidate：Secret / Credential / Lease

Credential metadata 与 Secret Material 分离。候选字段至少包括 `credential_ref`、`credential_version`、`allowed_consumer / operation class`、`lease_id`、`issued_at`、`expires_at`、`revoked_at`、`rotation_epoch`；明文 Secret 只通过受控 delivery channel 在短生命周期内出现。

任何持久化对象只保存 ref / version / lease outcome。Retry / Resume 如果原 Lease 已失效，重新取得资格，不复用旧 Secret Material。

#### B14.4 Detail Freeze Candidate：Mandatory Audit 与动作绑定

`AuditRequirement` 至少绑定 `requirement_id`、`action_hash / protected_operation_ref`、`policy_epoch`、`minimum_fact_set`、`durability_class`、`timing=MUST_BEFORE_EFFECT | MAY_BE_AFTER` 等语义。

`AuditPersistenceReceipt` 至少能证明 `audit_record_id`、matching action / requirement、持久化边界、committed_at 和不可否认的 outcome。06 在 `MANDATORY_BEFORE_EFFECT` 下必须检查 Receipt 与当前 PreparedAction / action hash 匹配。

#### B14.5 Detail Freeze Candidate：生命周期与 per-store enforcement

EffectiveLifecycleDecision 至少表达 `subject_ref`、`policy_version`、`retention_until`、`recall_eligible`、`purge_required`、`legal_hold_refs`、`compliance_exception_refs`、`effective_at`、`reason_code`。

每个 Store 的 `LifecycleEnforcementFact` 独立表达 `store_owner`、`subject_ref`、`decision_ref`、`state`、`attempt`、`completed_at / failed_at`、`failure_class`。08 不伪造全局 purge complete；治理查询通过多个 Store facts 汇总。

#### B14.6 Detail Freeze Candidate：Crash Window / Revocation Matrix

| Window | Durable truth | 恢复 / 下一步 | 禁止 |
| --- | --- | --- | --- |
| Decision 形成后响应丢失 | durable decision 可查 | 同输入查询 / 重算 | 产生语义不同的隐式 allow |
| Approval granted 后 action hash 改变 | 旧 Approval 历史仍在 | INVALIDATED + 新审批 | 复用旧批准 |
| Readiness 后、模型外发前撤权 | 新 SecurityEpoch 生效 | 07 重新 egress gate | 使用旧 allow |
| Tool 发出后撤权且 outcome unknown | 现实结果未知 | 06 Reconcile；阻止新 Attempt | 写成未执行 |
| Audit write 失败 | 无 matching receipt | block Effect | 事后用 Trace 补票 |
| Purge 部分 Store 成功 | per-store facts 不一致 | 继续剩余 enforcement | 宣称全局已删除 |
| Secret rotation 发生在 Retry 前 | 旧 Lease 过期 / revoked | 获取新 lease | 重放旧 Secret |

#### B14.7 Detail Freeze Candidate：Schema Evolution / Policy Rollout

1. Policy / Decision schema 必须向后读取历史记录；旧 Decision 按当时 policy version 解释。
2. 新的 mandatory 字段采用 add → backfill / derive when valid → verify → tighten constraint；不能伪造历史审批或授权默认值。
3. action-hash / canonicalization 算法带版本；算法升级不能让旧 Approval 失去可解释性。
4. Policy rollout 需要支持 canary / shadow evaluation 只用于比较，不得让未激活 policy 静默执法。
5. Credential / Secret schema migration 不把 Secret Material 搬进普通表。
6. 生命周期策略 schema 升级不得把 Legal Hold、No-Recall 和 Purge 合并成单一状态。
7. Policy Engine / Store 物理迁移必须证明历史 decision/audit refs 仍可查询。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

08 进入 Module Detail Freeze Review 前至少验证：

| 场景 | 必须证明 |
| --- | --- |
| cross-tenant read / retrieval | fail closed，且无旁路缓存泄露 |
| SecurityEpoch 在 Runtime interrupt 期间变化 | Resume 后重新门禁 |
| Readiness 后 egress 前撤权 | 07 不外发 |
| Approval 后 action hash / ToolVersion 改变 | 旧 Approval 无效 |
| Secret Lease 过期 / rotation | Retry 获取新 lease，不泄露旧 Secret |
| Policy Engine outage | 高风险路径 fail closed |
| Mandatory Audit persistence failure | 06 不产生 Effect |
| Tool 已发出后撤权 + timeout | 继续 Reconcile，不伪造未执行 |
| Legal Hold + No-Recall 同时存在 | 禁止召回但保留要求仍执行 |
| 多 Store purge 一个失败 | 全局状态不虚报 complete |
| Prompt Injection 诱导高风险 Action | Proposal 无法绕过 04/06/08 gates |
| cached old authorization | 新受保护访问因 epoch/version 检查拒绝复用 |

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

08 的 Decision 证明政策判断，不证明目标动作已经执行。`AuthorizationDecision=ALLOW` 不证明材料已读取、模型已调用、工具已执行或 Domain 已准入；`ApprovalDecision=GRANTED` 只证明指定 action hash 的审批成立。

`AuditRequirement` 不等于审计已经持久化；`EffectiveLifecycleDecision=PURGE_REQUIRED` 不等于 Store 已 purge。真正 execution proof 分别来自 AuditPersistenceReceipt 和各 Store enforcement facts。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

Authorization / Approval / Egress / Secret / Lifecycle 决定必须绑定 principal、tenant / matter / resource、action、SecurityEpoch / PolicyVersion、decision identity、expiry / refresh；Approval 额外绑定 action identity / hash / ToolVersion。

旧 SecurityEpoch 的 allow 不能因为进入 Checkpoint、cache、PreparedAction 或 ModelRoutingDecision 就自动延长。AuthorizationDecision、ApprovalDecision、Secret Lease、Audit Receipt、LifecycleDecision 使用不同 identity namespace，通过 causation refs 关联。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

撤权、PolicyVersion 更新或 Approval 失效只约束新的受保护访问和尚未执行动作，不重写过去合法历史。已经载入内存的数据是否允许继续纯计算必须由显式政策决定。

晚到结果如果要被继续使用、发布、外发、执行 Effect 或 Formal Admission，必须消费当前安全决定。任务取消不等于撤销既有 Effect / Admission；02 / 06 各自保存现实与业务历史。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

```text
current SecurityEpoch / PolicyVersion
→ historical decision / approval / audit refs needed for reconstruction
→ current Authorization / Egress / Secret / Approval eligibility for next protected action
→ matching AuditPersistenceReceipt when required
→ target module resumes and records its own execution fact
→ 09 records redacted correlation
```

一致性测试至少覆盖：撤权发生在 interrupt / retrieval / model / tool / admission 不同阶段；Approval action-hash drift；Secret rotation；Audit failure；Legal Hold + No-Recall；partial purge；旧缓存 Decision；Prompt Injection；Tool outcome unknown 与撤权并发。
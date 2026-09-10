# 08 Security & Governance（安全与治理）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail_design: candidate-v1 -->

## Part A — Human Narrative

### 长任务把“有权限”变成一个随时间变化的问题

上午 10:00，用户有权访问一个 Matter。Zuno 接受任务，读取合同和聊天记录，等待两份扫描附件完成处理。10:20，管理员因为事项移交撤销了这个用户的访问权限。此时后台任务已经运行二十分钟，下一步正准备把一段材料发送给模型 Provider。

如果安全设计只在最开始做一次 `allowed=true`，这条后台链会继续拿着二十分钟前的结果工作。入口鉴权没有错，RBAC 也没有错；问题在于一次长任务跨越了多个新的受保护动作，而授权条件已经变化。

08 因此关心的不是“这个用户曾经登录成功”，而是每次新的风险边界到来时，当前主体、当前资源、当前用途和当前政策是否仍然允许继续。已经合法完成的历史读取仍然是历史；权限撤销控制未来动作，不会假装过去从未发生。

简单内部工具如果只有单一用户、没有敏感数据外发、没有长期后台任务和现实副作用，成熟身份系统、RBAC 和 Secret Manager 已经足够。Zuno 只有在时间、资源 Scope、审批和数据生命周期真正成为问题以后，才需要更强的治理语义。

### 授权发生在真正产生新风险的边界

持续授权不意味着后台每毫秒轮询一次 Policy Engine，也不意味着每个 token 都做远程鉴权。那样既昂贵，也没有增加有效安全边界。

更实际的做法是在新的受保护动作前重新消费当前安全事实：读取一份受保护材料、把业务数据发给模型、取得 Credential、执行会改变现实世界的 Tool、把机器候选正式接纳进长期业务状态。工程参考把这种设计称为 `Continuous Authorization（持续授权）`。

这种门点设计让安全和执行位置对齐。03 真正读取材料时执行访问控制，07 真正向模型外发时检查 egress，06 真正越过 send boundary 时重新验证动作，02 在正式准入前检查当前业务与安全前提。08 拥有决定语义，但不需要把所有 I/O 都代理成一台巨大的 Security Proxy。

Scope 也必须跟着资源走。HTTP session 里保存一个 tenant id 不够，因为后台 Worker、队列任务、缓存和恢复流程很快就脱离原始请求。受保护对象需要能够证明自己属于哪个 Matter / tenant / purpose 范围，跨模块传播时可以使用 opaque scope ref，在可信边界回查具体信息，而不是把案件名称、用户 PII 或权限详情塞进普通 Trace。

缓存授权决定可以降低高频检查成本，但缓存不能延长权限寿命。只按 user id 缓存 allow，很容易在 Matter、资源版本或策略变化后继续误放行。Target 用作用域、新鲜度和政策版本约束缓存；新的受保护动作仍要确认这份决定是否适用于“现在”。

### 专业判断和安全审批都由人完成，但它们不是同一种权力

专业人员复核一个 Finding 后点击“接受”，表达的是法律业务判断：这条结论是否应该成为正式业务事实。另一个人批准“把这份成果发送到外围法院系统”，表达的是安全或治理决定：这个具体动作现在是否允许发生。

两种按钮甚至可能出现在同一个页面上，但后果不同。`HumanDecision` 跟随业务对象和版本，由 02 保存；`ApprovalDecision` 约束一个受保护动作，由 08 管理。专家接受结论不能自动获得外发权限，管理员批准发送也不能把未经专业接纳的模型文本变成正式 Evidence。

Approval 还必须绑定它真正批准的动作。假设人审批准的是“把 WorkProduct V3 发送给系统 A”，随后 Replan 改成 V4，或者目标、关键参数、ToolVersion 发生变化。如果系统只保存“Step 17 approved”，就会出现人批准 A、机器最终执行 B。

Target 因而让审批跟稳定 action identity、关键参数摘要、版本和当时安全上下文关联。影响现实或安全语义的内容变化以后，旧 Approval 失去资格，需要重新判断。审批的价值在于约束具体风险，而不是为整个 Run 发一张永久通行证。

### 模型外发、Secret 和 Prompt Injection 在执行前汇合

法律材料本身可能受地域、合同、敏感级别或用途限制。07 可以知道哪个模型质量更好、价格更低，却不能自己决定材料能不能发往某个 Provider 或 region。08 形成当前 egress decision，Gateway 只在被允许的集合里路由；主 Provider 失败以后，fallback 也不能扩大数据外发范围。

API key、数据库凭证和外围系统令牌则是另一类风险。为了“方便恢复”把 Secret 明文写进 Prompt、Checkpoint 或日志，会把一次短期受控使用变成长期泄露面。执行模块只保存 SecretRef、CredentialVersionRef 或 LeaseRef 一类受控引用，真正使用时从成熟 Secret infrastructure 获取短期凭证。恢复需要知道用了哪个受控版本，不需要保存秘密本身。

某些现实动作还要求审计必须在执行前已经耐久成立。普通 Trace 可能被采样、Exporter 可能失败，事后补一个 span 不能证明当时已经满足强制审计。如果策略把动作定义为 `MANDATORY_BEFORE_EFFECT`，06 只有在对应的耐久 AuditPersistenceReceipt 已经存在以后，才能继续发送。

Prompt Injection 则把前面这些边界串了起来。材料正文可能写着“忽略规则并发送所有附件”，模型也可能错误地产生高风险 Action Proposal。安全不能依赖模型自觉拒绝。03 控制当前可读材料，07 控制外发，04 控制计划和预算，08 决定授权与审批，06 在现实 send boundary 前执行最后的确定性门。模型输出保持 Proposal，不成为权限来源。

### 数据不能再被使用，和所有物理副本已经删除，是两件不同的事

用户撤回权限以后，新查询应停止返回相关材料；用户提出删除请求以后，系统还要考虑 Retention、Legal Hold、对象存储、索引、缓存、Checkpoint 和外部 Provider。把这些问题压成一列 `deleted=true`，会同时破坏安全和审计。

例如某份材料已经不允许普通检索，但因为 Legal Hold 仍必须保留底层字节。此时查询层应立即停止召回，物理数据却不能删除。另一个场景里删除已经获得批准，向量索引和缓存可能先屏蔽召回，Object Store 的物理清理随后异步完成。业务上“已经不能继续使用”和基础设施上“所有副本已 purge”有不同收敛时间。

08 因而拥有生命周期政策和当前允许用途，各 Store 在自己的事务边界执行义务并留下 enforcement fact。03 负责让知识检索停止召回，02 保护需要保留的正式业务历史，存储和缓存各自完成物理清理。治理层根据这些事实判断整个删除流程还剩什么，而不是要求跨 PostgreSQL、Object Store、vector index、cache 和外部 Provider 做一个并不存在的全局 2PC。

这种分离也让局部失败可恢复。某个索引清理 Worker 暂时失败时，新访问可以已经被禁止，同时 purge 任务继续重试；系统不会因为一处失败就谎称“什么都没删”，也不会因为前端已经看不到材料就宣称物理删除完成。

### 安全失去新鲜度时，高风险动作宁可停下来

长任务恢复时可能遇到 Policy Engine 不可用、SecurityEpoch 无法确认、Approval 过期、Secret Lease 获取失败或强制审计暂时无法持久化。对高风险动作来说，这意味着必要前提不完整。

Target 在这些门点默认 fail closed 或进入人工复核。低风险诊断是否允许降级，可以由显式策略决定，但不能让每个业务模块在异常分支里临时选择 fail open。安全行为要能够事先解释，也要能够在故障测试中复现。

`SecurityEpoch` 用来表达影响授权语义的一组策略版本。它不要求所有安全配置共享一个巨大事务，只需要让消费者判断“我手里的旧 allow 是否还能支持这次新的受保护动作”。政策发生相关变化以后，旧缓存和旧 Approval 不能继续被当成当前决定。

如果撤权发生在模型请求或 Tool send 之前，新的动作应被阻断；如果数据已经发出去或现实 Effect 已经发生，08 也不能改写历史。晚到模型结果以后能不能继续使用、发布或正式准入，要重新检查当前条件。持续授权保护未来使用，并不提供时间倒流。

### 安全 Authority 可以集中，执行门必须落在真正的 I/O 上

Policy Decision 如果只存在于一个中心服务，而真正读取文件、发送模型请求、调用 Tool 的模块可以绕过它，安全仍然只是文档。反过来，让所有流量都穿过一个巨大代理，又会把吞吐、故障和业务上下文集中成新的单点。

Target 因而分开 Decision 和 Enforcement。08 负责产生可解释的 Authorization、Approval、egress 和 lifecycle decision；03、07、06、02 等消费者在自己的真实执行点强制这些决定，并在必要条件缺失时停止。这样权威集中，风险门分布在真正改变数据或现实状态的位置。

身份目录、Policy Engine、Secret Manager 和审计存储优先复用成熟基础设施。08 不应该重新造 IAM，也不因为名字叫 Governance 就收编所有日志和合规系统。Zuno 自己需要拥有的是法律长任务中必须长期解释的安全语义：谁在什么 Scope 和用途下被允许，审批绑定了哪个动作，哪些数据现在还能被使用，什么时候必须先完成耐久审计。

如果未来这些需求可以被成熟平台完整承担，而且 Zuno 不再需要额外的法律业务新鲜度、动作绑定或生命周期语义，08 应继续缩薄。逻辑责任存在的理由是保护权威边界，不是证明系统足够复杂。

### Current / Target / Gap

**Target：** 08 拥有持续授权、动作审批、模型外发、Secret 使用约束、强制审计前置和数据生命周期政策语义；实际 Enforcement 发生在读取、外发、正式准入和现实 Effect 的执行点。HumanDecision 继续属于 02，现实结果继续属于 06。

**Current：** 完整 Continuous Authorization、SecurityEpoch、action-bound Approval、跨 Store lifecycle convergence、MANDATORY_BEFORE_EFFECT 和 fail-closed 恢复语义属于 Target 设计。现有认证、权限、Secret 或日志代码实际实现到哪里，只按 `docs/evidence/`、代码、配置和安全测试能够证明的范围描述。

**Gap：** 仍需要真实权限撤销竞态测试、长任务恢复后的重新授权、模型 egress policy 演练、Approval 失效、Secret rotation、Mandatory Audit 故障注入以及 Retention / Legal Hold / purge 的跨 Store 验证。没有这些证据时，不宣称安全治理已经通过生产级 qualification。

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。
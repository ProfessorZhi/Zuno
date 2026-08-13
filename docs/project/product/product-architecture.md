# Product Architecture：用户如何完成法律工作？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 用户、外部 Host 和法律工作成果如何形成一个可复核的产品闭环？
owner: Product Architecture Owner
replaces: docs/project/modules/01-product-surface.md（Superseded）

## Part A — Architecture Narrative

### 产品要完成的工作

用户购买的不是一个 Agent Run，而是案件材料处理、证据组织、法律分析、人工复核和可交付 WorkProduct。Agent 是完成工作的一种执行方式；Matter、Review、HumanDecision 和 WorkProduct 才是用户能理解并负责的产品对象。Zuno 的产品边界因此围绕法律工作成果，而不是围绕聊天消息或模型调用次数。

### Target Scenario

这是 Target Scenario，不是历史事实：

用户创建 Matter，上传合同、诉状或证据，等待系统完成解析和分析。系统在 Matter 中显示材料版本、证据来源、待补证据和分析进度；Agent 可以执行检索和法律能力，但中间候选不会伪装成最终事实。用户进入 Review，查看 Finding、引用和冲突，做出 HumanDecision，最后确认 WorkProduct 并通过 Zuno UI 或外部 Host 交付。

### 产品概念之间的关系

Matter 是法律工作的边界和权限容器；DocumentVersion 是 Matter 中可追溯的材料版本；AgentRun 是一次执行记录；Review 是对候选和结论进行核验的产品任务；HumanDecision 是业务人员的正式判断；WorkProduct 是可以交付、引用和审计的结果。Host 可以是 Zuno UI、WorkBuddy 或组织系统，但 Host 不能绕过 Domain Owner 直接写 Finding 或 HumanDecision。

### 责任和非责任

产品层负责用户可见的工作流、状态解释、Review 入口、交付和审计可见性；不负责重新定义法律事实、复制 Retrieval 状态机、决定模型 Provider 或执行未经授权的外部动作。Domain、Knowledge、Runtime、Security 和 Tool 是相邻 Owner；产品层只通过稳定 Contract 呈现它们的结果。

### 为什么不能只是聊天页面

聊天页面能承载回答，却很难表达一个材料版本变更后哪些结论 stale、哪些证据缺失、谁已经审核以及 WorkProduct 是否仍可交付。普通 Host + Legal Backend 仍是优先替代方案；只有当 Matter-centric Review、Evidence Sufficiency、HumanDecision 和交付审计在复杂任务中产生可测收益，才保留更强的产品状态模型。

### 失败、取舍与反转

若上传成功但解析失败，用户必须看到可恢复的 Processing Failure，而不是一个空白答案；若新材料使已审核 Finding stale，系统必须阻止旧 WorkProduct 被误当成当前结论。显式 Review 和版本可见性增加了界面和状态复杂度，但换来专业人员可解释的责任边界。若用户只需要一次性问答且没有版本、复核和交付需求，应降级为 Host + Tool；若用户测试不接受 Domain State 视图，应重新检查产品边界，而不是增加更多 Agent。

### Current / Target / Gap

Current 只接受仓库代码、测试和实际运行证据；Target 是 Matter-centric Legal Case Intelligence 产品和可替换 Host；Hypothesis 是 Review、WorkProduct 和 Domain-aware UX 能改善任务完成与人工接受率；Gap 是真实用户流程、法院 QA、交付协议、可用性和效果测量。

## Part B — Detailed Architecture Specification

### Product Contract

| 对象 | 输入 | 输出 | Owner |
|---|---|---|---|
| Matter | principal、tenant、workspace、matter metadata | MatterId、scope、status、audit reference | Platform/Domain |
| AgentRun | MatterId、task、DomainSnapshot、budget、policy | RunId、status、progress、RunOutcome reference | Agent Runtime |
| Review | candidate/findings、EvidenceReference、reviewer | HumanDecision、decision version、review status | Domain/Product |
| WorkProduct | accepted Finding、HumanDecision、citation、delivery policy | immutable work product version、delivery receipt | Product/Domain |

### 状态与版本

Product API 只暴露用户可理解的 pending、running、review_required、stale、ready、failed 和 delivered 语义；底层 DomainVersion、PlanVersion 和 Provider State 由对应 Owner 管理。WorkProduct 只能引用已接受版本；引用版本变化时必须重新审查或生成新版本，不能覆盖旧交付物。

### 接口、命令与查询

HTTP/API 负责 Matter、Document Upload、Run Submit、Run Status、Review、WorkProduct Query 和 Delivery Query。长任务返回 Job/Run Receipt，不阻塞请求等待模型或 OCR。SSE/WebSocket 只传进度和可见事件，不传隐藏思维链。外部 Host 通过 MCP/API 获得同样的 Domain Admission 和 Review Contract。

### 失败、幂等与恢复

Create Matter、Upload、Submit Review 和 Deliver WorkProduct 必须有 Idempotency Key。重复请求返回同一业务结果或明确冲突；上传重复由 DocumentVersion Hash/Source Identity 处理。Run 超时进入可恢复状态；Review 期间权限变化、材料更新或 Finding stale 时暂停并重新验证。审计保存主体、Matter、版本、决定、时间和结果，不保存隐藏思维链。

### Security、Observability 与 Evidence

每次用户操作绑定 Tenant/Matter/Scope/Policy Epoch；跨 Host 请求必须保留 CorrelationId、Authorization Decision 和 Receipt。观测至少覆盖 Run、Review、WorkProduct、DomainVersion、Citation、失败类别和交付结果。产品质量不能由 UI 存在证明，需通过任务完成、Evidence Sufficiency、Citation Correctness 和 Reviewer Acceptance 测量。

### Compatibility and Gap

Current API 形态以仓库和测试为准；Target Contract 允许 Host 替换。迁移不得把旧 Chat transcript 直接当作 Review 或 WorkProduct。Gap 包括真实用户验证、状态可用性、外部 Host 兼容、审计导出、权限撤回和交付失败演练。

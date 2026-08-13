# Product Architecture：用户如何完成法律工作？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 用户、外部 Host 和法律工作成果如何形成一个可复核的产品闭环？
owner: Product Architecture Owner
replaces: docs/project/modules/01-product-surface.md（Superseded）

## Part A — Architecture Narrative

### 用户真正要交付的是什么

一名法律工作人员打开案件，不是为了“拥有一个 Agent”，而是要把一堆材料变成可以复核、引用和交付的工作成果。产品因此把 Matter、材料版本、证据缺口、待审核结论和 WorkProduct 放在同一条工作线上。Agent 只是其中一种执行方式；如果它换成 WorkBuddy、一个后台任务或人工录入，案件的责任边界也不应跟着消失。

### 一个目标工作场景

以下是 Target Scenario，不是历史项目事实。用户创建 Matter，上传合同、诉状和证据。系统先确认材料版本和可见范围，再显示哪些内容已经解析、哪些证据仍缺失。分析过程中，检索结果和专业能力只形成候选；用户进入 Review 后，能看到 Finding 的来源、冲突和所依赖的材料版本，随后作出 HumanDecision，最后确认 WorkProduct。交付可以从 Zuno UI 发出，也可以由 WorkBuddy 或组织系统作为 Host 发起，但 Host 不能跳过 Domain Admission。

这个顺序很重要：若界面只展示一段流畅的答案，用户无法知道答案是否基于最新材料，也无法区分“模型建议”和“已经审核的业务结论”。产品层要负责解释这些状态，而不是替 Domain、Knowledge 或 Runtime 重新实现它们。

### 为什么不把它做成聊天页

聊天页适合一次性问答，却不擅长表示版本、复核责任和可交付结果。比如用户上传一份新证据后，刚刚审核过的 Finding 可能只对旧版本成立；如果产品仍把旧答案留在对话末尾，用户很容易误以为它仍然有效。Matter-centric 视图和 Review 流程确实增加了状态和界面成本，但它们把“谁看过、依据什么、现在是否还能交付”变成可解释的产品事实。

### 失败时用户应该看见什么

考虑上传成功、解析任务却在中途失败的情况。产品不能用空白页面掩盖失败，也不能让 Agent 继续把未完成的材料当作完整输入；它需要显示 Processing Failure、受影响的 DocumentVersion 和可重试入口。另一种更危险的情况是新材料使已审核 Finding 变 stale，此时旧 WorkProduct 应被标记为需要复核，而不是继续显示为当前结论。显式状态会牺牲一些界面简洁性，换来专业人员可以承担的责任边界。

普通 Host 加 Legal Backend 仍然是产品设计的竞争方案。如果用户只是偶尔提问，没有版本、复核或交付要求，Host + Tool 更简单，也更合适。只有真实任务证明 Review、Evidence Sufficiency 和 WorkProduct 能改善人工接受率，才值得保留完整产品状态。

仓库和测试目前只能证明部分接口与设计表面；Matter-centric Legal Case Intelligence 是 Target，Review 和 WorkProduct 带来增益是 Hypothesis。真实用户流程、法院 QA、交付协议和可用性仍是 Gap，不能写成 Current 或 Production 事实。

这条边界也保留了回退路径：当业务只需要一次低风险检索时，可以直接使用外部 Host，而不必启动完整的案件工作台。

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

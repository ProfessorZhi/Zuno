# 01 Product Surface

updated: 2026-07-14  
status: target-boundary-foundation  
module_number: 01  
formal_path: `docs/modules/01-product-surface.md`  
agent_mirror: `.agent/modules/01-product-surface.md`

> 本文是 Zuno 第 01 个逻辑模块——Product Surface——的第一轮 Target 边界设计。
>
> 本轮只冻结产品入口、北向场景、Ownership、Trust Boundary、Projection 原则、交互语义和不可违反的不变量；不冻结完整 API 字段、Projection 状态机、数据库表、SSE Cursor 编码、Retention 数值或前端组件结构。
>
> Product Surface 的第二轮实施级设计必须在 Agent Core、Security、Tool Runtime、Input、Knowledge、Memory、Observability & Eval 和 Infrastructure 的相关 Contract 稳定后完成。

## 0. 文档边界与事实源

本文统一承载第一轮边界事实：

```text
Product Surface 解决的问题
产品入口和用户场景
负责与不负责的范围
跨模块 Ownership
产品 Trust Boundary
Command / Query / Stream 的语义边界
Projection 与领域事实的关系
长任务、审批、取消、Artifact 和质量披露的产品语义
第一轮架构不变量
第二轮待冻结 Contract
第一轮 Requirement 与验证证据
```

文档边界：

```text
docs/modules/01-product-surface.md
    第一轮正式 Target 边界事实源。

.agent/modules/01-product-surface.md
    字节级一致的 Agent 镜像。

其他模块正式 Target 文档
    提供 Product Surface 第二轮设计所依赖的领域 Contract。

.agent/programs/
    Current → Target 的实现、迁移、切流和收口计划。

docs/status/production-readiness.md
    Current、Gap、Measurement 和完成证据状态。
```

规范优先级：

```text
全局架构原则
→ 各领域事实 Owner 的正式 Target Contract
→ 本文第一轮 Product Surface 边界
→ 第二轮 Product Surface 实施级设计
→ 已确认 Program
→ 代码与 Migration
```

本文不是 Current Baseline，也不是完整实现规格。文档完成后只能声明 `design available` 和 `boundary foundation available`。

---

# Part I：定位、问题与边界

## 1. 为什么需要 Product Surface

Zuno 不是一次 HTTP 请求内完成的普通 CRUD 系统。知识问答、文件摄取、Agent 任务、审批、副作用、外部等待、断线恢复和结果发布可能跨越多个进程、多个领域模块和较长时间。

如果 Web Router、Frontend Store 或单个 Workspace Service 直接承担这些职责，会出现：

```text
HTTP 200 被误认为 Run 成功
SSE 关闭被误认为任务完成
Frontend 根据字符串推断 Approval、Tool Effect 或 RunOutcome
FastAPI Router 直接调用 Planner、Retriever、Tool 和数据库
用户断线导致后端任务被错误取消
Upload 成功被误认为文档已经可检索
Tool 响应丢失后允许用户盲目 Retry
模型生成文本被当成正式发布结果
Projection 缓存反向覆盖领域事实
权限撤销后旧页面继续展示敏感内容
```

一句话定义：

> Product Surface 是 Zuno 的北向产品边界。它通过 Web、Desktop 和 External API 接收用户意图，把命令交给真正的领域 Owner，并把各模块已提交且已授权的领域事实投影成可查询、可恢复、可解释的产品体验。

## 2. Product Surface 不是 Agent Core

```text
Product Surface
    用户想做什么
    用户可以看到什么
    用户当前允许做什么
    如何通过 HTTP / SSE / Desktop 交付

Agent Core
    Run 如何计划、调度和执行
    Retry、Repair、Fallback 或 Replan 如何选择
    Interrupt 和控制命令如何仲裁
    Final Gate 与 RunOutcome 如何提交
```

Product Surface 不建立第二套 Task Controller，不直接修改 Run、Plan、Step、Approval、Tool Effect、Evidence、Memory 或 Eval 的领域状态。

## 3. 负责范围

Product Surface 负责：

```text
Web、Desktop 和 External API 的北向适配
用户提交、对话和产品操作入口
API Request / Response DTO
Command 接受、拒绝、重复和冲突的产品语义
Query API 和授权后的 View Model
Product Projection 和 Display Mapping
Snapshot、SSE 和未来可选 WebSocket 的交付
断线重连、Cursor、Gap 和 Resync 的产品协议
用户输入 Interrupt 的表单与提交入口
Approval 的展示与决策入口
Cancel、Resume、New Run 和后端提供动作的交互入口
Citation、Artifact、Quality Disclosure 和管理视图
Channel Delivery、Client Render 和 User Read 状态
浏览器与客户端渲染安全
产品级错误映射和用户可理解的恢复建议
```

## 4. 不负责范围

Product Surface 不负责：

```text
创建或验证 Plan
调度 Step 或 Action
选择 Retry、Repair、Fallback 或 Replan
直接调用模型厂商 SDK
直接执行 Tool 或外部副作用
批准权限、修改 Policy 或推进 Security Epoch
解析 PDF、OCR、切分、索引或修改 Knowledge 事实
写入长期 Memory
生成 Trace、Eval 或质量证明事实
保存 LangGraph Checkpoint
把 Queue ACK、HTTP 2xx、SSE 完成或本地 UI 状态当作领域成功
```

## 5. 外部参与者与渠道

```text
End User
Workspace Admin
Approver
Auditor / Eval Operator
Web Client
Desktop Client
External API Client
Channel Adapter
```

不同渠道可以拥有不同交互能力，但不能改变领域事实语义。Desktop 能调用本地能力，不代表 Desktop 可以绕过 Agent Core、Security、Tool Runtime 或 Idempotency。

## 6. Cross-module Ownership

| 模块 | 事实 Ownership | Product Surface 的关系 |
| --- | --- | --- |
| Product Surface | User Interaction、RuntimeRequest、CommandReceipt、Conversation Presentation、Product Projection、ChannelDelivery、ClientRendered、UserRead | 直接拥有 |
| Input / Ingestion | SourceObject、ParseJob、DocumentVersion、Ingestion 状态 | 查询并投影，不推断可检索性 |
| Knowledge | RetrievalRound、Evidence、CitationLineage、Knowledge Snapshot | 展示授权后的 Evidence/Citation View |
| Model Gateway | ModelInvocation、Usage、Provider Failure | 仅展示允许披露的执行和成本摘要 |
| Memory & Context | MemoryVersion、ContextPack、Memory Commit/Delete | 展示可见、可管理的受控视图 |
| Agent Core | AgentRun、Goal、Plan、Step、Interrupt、ControlDecision、Publication、RunOutcome | 创建请求、提交 Signal、查询并投影 |
| Capability / Skill | CapabilityDefinition、SkillDefinition、Selection Result | 展示可用能力，不自行决定执行 |
| Tool Runtime | PreparedToolAction、ToolAttempt、EffectReceipt、EffectReconciliation | 展示审批和 Effect 状态，不执行 Tool |
| Security | Principal、Authorization、Approval、Policy、Grant、Security Epoch | 每个入口消费安全决策 |
| Observability & Eval | Trace、Metric、EvalResult、Evidence Registry Projection | 展示分层质量和审计视图 |
| Infrastructure | Object、Queue、Lease、Checkpoint、Outbox、Delivery Primitive | 消费 primitive，不把 Receipt 当业务结果 |

## 7. Trust Boundary

以下客户端输入默认不可信：

```text
user_id
tenant_id
workspace_id
trace_id
run_id 的所有权声明
approval_mode
access_scope
security role
model_id
provider
api_key
base_url
tool credential
skill allowlist
desktop bridge token
artifact URI
citation URI
```

客户端可以提交用户选择或偏好，但服务端必须重新解析 Principal、Tenant、Workspace、Resource Grant、Security Epoch、Capability 范围、Secret Ref 和可用动作。

---

# Part II：核心产品场景与端到端语义

## 8. 统一产品主路径

```text
User Intent
→ Product Command API
→ Authentication / Authorization
→ RuntimeRequest or Domain Command
→ True Domain Owner
→ Domain Fact Commit
→ Domain / Integration Event
→ Product Projector
→ Authorized Snapshot / Delta
→ Web / Desktop / External API
```

Product Surface 只接受用户意图、交付命令和展示事实。它不在命令请求线程内复制完整 Agent Runtime。

## 9. 普通知识问答

```text
用户提交问题
→ Product 接受 UserSubmission
→ 提交 Create Run 请求
→ 返回 CommandReceipt
→ Agent Core 创建 Run 和 Deterministic Single-Step Plan 或 Dynamic DAG Plan
→ Product 展示 Run Progress
→ Agent Core 提交 RunOutcome 和 Publication
→ Product 形成 Assistant Message Projection
→ ChannelDelivery 交付
```

规则：

- 每个正式回答都必须绑定 AgentRun 和 RunOutcome。
- 简单问答仍然必须经过 Agent Core 的 Plan、Trace、Budget、AnswerPolicy、Final Gate 和 Publication。
- Token Stream 只能是 Provisional Content，不是正式 Assistant Message。
- 页面关闭或 SSE 断开不取消 Run。

## 10. Strict Grounded Answer

```text
Evidence sufficient
    → 正式答案、Citation 和 Quality Disclosure

Evidence insufficient
    → ABSTAINED，而不是伪造结论

Evidence conflict unresolved
    → PARTIAL 或 ABSTAINED，并披露冲突

Evidence revoked or inaccessible
    → Publication 前阻断；Publication 后创建更正或撤回视图
```

Product Surface 不自行计算 Evidence Sufficiency，不用“检索到文档数量”冒充质量结论。

## 11. 文件上传与摄取

Product 必须区分：

```text
Upload Accepted
Source Object Committed
File Registered
Parse Queued
Parsing
OCR Required / Blocked
Document Version Ready
Index Handoff Accepted
Knowledge Version Searchable
```

Upload API 返回成功只表示上传入口接受或对象提交成功，不表示文档已经解析、索引或可用于回答。

## 12. 长任务、离开页面与断线恢复

```text
Run continues on server
Client disconnects
→ Domain Run remains unchanged
Client reconnects
→ Reauthorize
→ Resume Stream or refetch Snapshot
→ Continue from Projection Watermark
```

Product 必须支持用户离开页面后重新打开任务。客户端连接状态和 Run 状态是两个正交维度。

## 13. User Input Interrupt

用户补充信息通过 Product 交互提交，但输入分类和 GoalVersion 变化由 Agent Core 决定：

```text
Supplemental Input
Clarification Response
Constraint Change
Output Contract Change
Objective Change
Cancellation Request
New Task
```

Product 不根据按钮名称自行决定 Retry 或 Replan。

## 14. Approval

```text
Tool Runtime PreparedToolAction
→ Security Authorization / Approval Required
→ Product Approval View
→ User Approve or Deny
→ Security Approval Decision
→ execution-time revalidation
→ Tool Runtime execution or rejection
→ Agent Core consumes result
```

Product 展示准备动作、风险、目标资源、范围和到期时间；Product 不创建 Approval 成功事实，也不直接执行 Tool。

## 15. Tool Effect UNKNOWN

```text
ToolAttempt executed
→ external result cannot be confirmed
→ Effect = UNKNOWN / RECONCILING
→ Product displays reconciliation state
→ ordinary Retry action is unavailable
→ owner-provided Reconcile or Human Review action
→ definitive outcome or HUMAN_REQUIRED
```

Tool UNKNOWN 不是普通失败。前端不得通过重复点击制造第二次副作用。

## 16. Cancellation

```text
User requests cancel
→ CommandReceipt ACCEPTED
→ Agent Core arbitrates CANCEL
→ Run enters CANCELLING
→ new dispatch stops
→ interruptible work is cancelled
→ non-interruptible effects drain or reconcile
→ RunOutcome CANCELLED or PARTIAL
```

“取消请求已接受”与“取消收口已完成”必须分别展示。

## 17. RunOutcome 展示

Product 必须保留以下终局差异：

```text
COMPLETED
PARTIAL
ABSTAINED
REFUSED
BLOCKED
FAILED
CANCELLED
EXPIRED
```

`PARTIAL`、`ABSTAINED`、`REFUSED` 和 `BLOCKED` 不是统一的红色技术错误。每种 Outcome 必须有不同说明、允许动作和审计语义。

## 18. Artifact、Publication 与 Delivery

```text
ArtifactCandidate / ArtifactVersion
    内容对象与验证状态

Publication
    Agent Core 对正式结果的发布事实

ChannelDelivery
    Product 或渠道 Adapter 的交付事实

ClientRendered
    客户端是否成功渲染

UserRead
    用户是否阅读或确认
```

以下等式全部禁止：

```text
Artifact Generated = Published
Object Stored = Delivered
Publication PUBLISHED = Client Rendered
Client Rendered = User Read
```

## 19. 管理与质量视图

普通用户、Workspace Admin、Approver、Auditor 和 Eval Operator 看到的字段不同。Product 必须通过 Authorized View 隐藏：

```text
Secret
完整 Tool Args
内部 Prompt
隐藏思维链
原始 Checkpoint
未经授权的 Evidence 内容
其他租户资源存在性
内部安全规则细节
```

Quality Disclosure 只能陈述已有 Eval 或运行证据，不能把“有一个分数栏位”写成质量已经证明。

---

# Part III：产品对象、Projection 与真实状态

## 20. 第一轮概念对象

| 对象 | Owner | 第一轮语义 |
| --- | --- | --- |
| `PrincipalSessionRef` | Security | 当前身份与安全上下文引用 |
| `ConversationThread` | Product Surface | 用户可见对话容器，不是 Agent Checkpoint |
| `UserSubmission` | Product Surface | 用户一次提交的原始意图事实 |
| `UserMessage` | Product Surface | 被接受进入对话历史的用户内容 |
| `RuntimeRequest` | Product Surface | 向 Agent Core 提交的不可变产品请求 |
| `CommandReceipt` | Product Surface | 命令已接受、拒绝、重复或冲突的结果 |
| `AgentRunRef` | Agent Core | Product 保存引用，不复制 Run 事实 |
| `ProductProjection` | Product Surface | 可重建的产品读模型 |
| `AuthorizedView` | Product Surface + Security Decision | 对特定 Principal 可见的响应 |
| `AvailableAction` | 对应 Domain Owner 决定，Product 投影 | 当前用户确实允许执行的动作 |
| `ChannelDelivery` | Product Surface / Channel Adapter | 结果向渠道交付的事实 |
| `ClientRendered` | Product Surface | 客户端渲染事实 |
| `UserRead` | Product Surface | 用户阅读或确认事实 |

这些对象的最终字段和数据库映射在第二轮设计后冻结。

## 21. Conversation、Message、Run 和 Publication 的关系

第一轮冻结：

```text
ConversationThread
    可以包含多个 UserMessage 和多个 Assistant Message Projection。

UserSubmission
    触发一个 RuntimeRequest 或另一个明确 Domain Command。

RuntimeRequest
    最多创建一个 AgentRun；重复请求通过幂等返回原结果。

AgentRun
    可以产生零个或多个 Provisional Content，但最多形成一个当前有效 RunOutcome。

Publication
    是正式结果事实；Assistant Message Projection 从 Publication 构造。

Retry / Try Again
    默认创建新的 RuntimeRequest 和新的 Run，不复活已终结 Run。
```

## 22. Projection 不是事实源

```text
True Domain Facts
→ Versioned Events / Queries
→ Product Projector
→ ProductProjection
→ Security-aware Mapping
→ AuthorizedView
```

Projection 必须可删除、重建和校验。Projection 丢失不能改变 AgentRun、Approval、Tool Effect、Evidence、Memory 或 Eval 的真实状态。

## 23. Projection 的三种状态维度

第一轮要求明确区分：

```text
Domain Status
    Run、Approval、Tool Effect、Ingestion、Publication 等领域状态。

Projection Freshness
    Product 读模型是否已经追上来源事实。

Client Connection Status
    在线、重连、断线、Cursor 过期等交付状态。
```

例如：

```text
Run = RUNNING
Projection = CURRENT
Client = DISCONNECTED
```

这是合法组合，不得把它映射为 Run 失败。

## 24. AvailableAction 原则

前端只能展示后端 Authorized Projection 提供的 `AvailableAction`。它不得根据状态字符串自行推断：

```text
Retry
Approve
Resume
Cancel
Download
Reconcile
Publish
Delete
```

每个动作必须绑定目标资源、授权结果、幂等语义和有效期。具体字段第二轮冻结。

## 25. Display Mapping 原则

Product 可以把复杂领域状态映射成用户语言，但必须满足：

```text
Mapping 是确定性的
Mapping 可测试
Mapping 不覆盖源状态
Mapping 保留终局差异
Mapping 能解释等待原因
Mapping 能显示 Projection 是否过期
Mapping 只暴露后端允许的下一步动作
```

---

# Part IV：Command、Query、Stream 与安全边界

## 26. Command API 语义

Command API 表达“请求执行某个领域操作”，不表达“操作已经完成”。

第一轮冻结的命令类别：

```text
Create Run
Submit Signal / Supplemental Input
Resolve User Interrupt
Submit Approval Decision
Request Cancel
Request Owner-provided Recovery Action
Create New Run From Previous
Request Artifact Publication or Delivery
Submit Feedback
```

命令结果至少必须区分：

```text
ACCEPTED
REJECTED
DUPLICATE
CONFLICT
```

具体 Envelope、字段、HTTP Code 和 Idempotency Key 规则第二轮冻结。

## 27. Query API 语义

Query API 返回授权后的 Projection，不直接暴露：

```text
ORM Row
LangGraph State
Raw Checkpoint
Provider SDK Response
完整 Trace Span
隐藏思维链
Secret
未经脱敏的 Tool Args
内部 Critic 或 Replan Payload
```

第一轮目标 View：

```text
Conversation View
AgentRun View
Plan Progress View
Step Progress View
Interrupt View
Approval View
Tool Effect View
Ingestion View
Evidence / Citation View
Artifact View
RunOutcome View
Quality Disclosure
Admin / Audit View
```

## 28. Stream 语义

近期开启：

```text
HTTP Commands
HTTP Queries
SSE Product Projection Stream
```

WebSocket 属于 Future Optional，只有在双向低延迟交互明确需要时再引入。

SSE 第一轮原则：

```text
断线不取消 Run
流关闭不表示 RunOutcome
Heartbeat 只表示连接健康
重连必须重新鉴权
支持 Resume Cursor 或 Snapshot Resync
至少一次交付允许重复，客户端必须去重
检测 Gap 后必须重新获取 Snapshot
Terminal Event 只表示观察到终局事实，不是 TCP 终止语义
```

Cursor 编码、Stream Sequence、Retention 和 Backpressure 数值第二轮冻结。

## 29. Provisional Content

```text
Progress Stream
    可以长期保存或重放的结构化进度。

Provisional Content
    Policy 允许时提供的临时生成内容，可以被替换或撤回。

Transactional Final Publication
    Final Gate 后正式发布的结果。
```

Provisional Content 不进入长期 Memory，不作为正式 Citation、Feedback Target 或 Assistant Message 事实。

## 30. Product Error 与 Domain Outcome 分离

```text
Transport Error
Command Rejection
Authorization Failure
Projection Stale / Gap
Domain RunOutcome
Publication Failure
Channel Delivery Failure
Client Render Failure
```

这些不是同一种错误。Product Error Response 不得覆盖已经提交的 Domain Outcome。

## 31. Authorization Checkpoints

必须在以下位置重新授权：

```text
Command submission
Query
SSE connect
SSE reconnect
Sensitive delta delivery
Approval decision
Artifact metadata
Artifact download
Citation content access
Admin operation
```

Security Epoch 或 Grant 变化后，Product 必须停止继续交付不再授权的内容，并要求 Reauthorization 或重建 Authorized View。

## 32. 客户端渲染安全

Product Surface 必须防止：

```text
不受信任 Markdown / HTML 执行脚本
危险 URL Scheme
外部图片追踪
Artifact Preview 逃逸 Sandbox
MIME Sniffing
文件名与 Content-Disposition 注入
Tool Output 作为可信 HTML 渲染
内部 Object URI 或 Secret 泄露
```

具体 Sanitizer、CSP、Download Token 和 Preview Sandbox Contract 在第二轮冻结。

---

# Part V：第一轮架构不变量

## 33. Invariant Registry

### INV-PRODUCT-001：前端不是后端事实源

Frontend Store、Local Cache 和浏览器状态不能提交领域终局。

### INV-PRODUCT-002：Product Surface 不建立第二个 Agent Controller

FastAPI Router、Product Service 和 Frontend 不直接编排 Planner、Retriever、Tool、Retry 或 Replan。

### INV-PRODUCT-003：HTTP 2xx 不等于领域成功

HTTP 2xx 只表示请求处理或命令接受结果。

### INV-PRODUCT-004：SSE 关闭不等于 Run 成功或取消

连接生命周期和 Run 生命周期正交。

### INV-PRODUCT-005：正式答案必须来自 Publication 和 RunOutcome

模型 Token、Queue Message、Checkpoint 或本地拼接文本都不是正式答案。

### INV-PRODUCT-006：Projection 不得反向修改源领域事实

Projection 可以重建，源事实只能由对应 Owner 修改。

### INV-PRODUCT-007：Product 不冒充其他模块的事实 Owner

Product 只保存必要 Ref、Projection 和自身交付事实。

### INV-PRODUCT-008：终局语义必须完整保留

PARTIAL、ABSTAINED、REFUSED、BLOCKED、FAILED、CANCELLED 和 EXPIRED 不得合并。

### INV-PRODUCT-009：AvailableAction 必须来自授权后的后端 Projection

Frontend 不自行推断可执行动作。

### INV-PRODUCT-010：Tool UNKNOWN 禁止普通 Retry

必须等待 Tool Runtime Reconcile 或明确 Human Action。

### INV-PRODUCT-011：Approval 不由 Product Surface 决定

Product 只提交用户决策，Security 保存 Approval 事实。

### INV-PRODUCT-012：Upload Accepted 不等于 Searchable

Input 和 Knowledge 的状态必须独立展示。

### INV-PRODUCT-013：Artifact、Publication、Delivery、Render 和 Read 分离

任何一层成功不能冒充下一层成功。

### INV-PRODUCT-014：重复 Command 不产生重复 Run 或副作用

相同幂等请求返回原 CommandReceipt 或明确 Conflict。

### INV-PRODUCT-015：客户端身份和权限声明不可信

Principal、Tenant、Workspace、Grant 和 Security Epoch 必须由服务端解析。

### INV-PRODUCT-016：Query、Stream 和 Download 都必须授权

创建时授权不代表永久授权。

### INV-PRODUCT-017：Projection Freshness 必须可见

过期、Gap、Rebuild 或 Unavailable 不能被伪装为最新事实。

### INV-PRODUCT-018：Provisional Content 不是正式记录

不得写入长期 Memory、正式 Citation 或 Eval Ground Truth。

### INV-PRODUCT-019：隐藏思维链和 Secret 不进入产品 View

只展示结构化决策摘要、Evidence、Policy 结果和必要错误信息。

### INV-PRODUCT-020：Product Mode 不创建旁路 Runtime

普通问答、严格依据、深度研究和 Agent 任务只能作为 UX Preset，仍进入统一 Agent Runtime Contract。

### INV-PRODUCT-021：取消请求与取消完成分离

Product 必须展示 CANCELLING 和最终 CANCELLED / PARTIAL。

### INV-PRODUCT-022：连接恢复必须重新鉴权

Resume Cursor 不替代 Authorization。

### INV-PRODUCT-023：用户可见质量声明必须有证据

未测量、被阻塞或不可用的质量状态不得显示为质量已证明。

### INV-PRODUCT-024：未知枚举必须安全降级

旧客户端遇到新安全、权限或副作用状态时默认 fail-closed，不提供危险动作。

---

# Part VI：第一轮冻结项与第二轮待设计项

## 34. 第一轮冻结项

以下原则进入正式 Target Boundary，后续模块不得自行推翻：

```text
Product Surface 是北向产品边界，不是 Agent Core
所有正式产品入口复用统一 Agent Runtime Contract
Product 不拥有 Run、Approval、Tool Effect、Evidence、Memory 或 Eval 事实
用户可见状态来自授权后的 Product Projection
HTTP、SSE、Queue 和本地 UI 不决定业务成功
Command、Query 和 Stream 分离
断线不取消 Run
Tool UNKNOWN 不允许盲目 Retry
每个可执行 UI 动作来自 Authorized AvailableAction
RunOutcome、Artifact、Publication、Delivery、Render 和 Read 分离
普通、严格、研究和 Agent 模式只是 UX Preset
Product 全链路重新授权并响应 Security Epoch 变化
```

## 35. 第二轮待冻结 Contract

以下内容必须等待相关模块 Contract 稳定后再冻结：

```text
RuntimeRequest 完整字段
CommandReceipt 完整字段和 HTTP Mapping
ConversationThread、Message 和 Feedback 的最终状态机
Product Projection Version 与 Source Watermark 结构
AuthorizedView 和 AvailableAction 字段
AgentRun、Plan、Step、Interrupt 的显示枚举
Approval View 与 PreparedToolAction 显示字段
ToolAttempt、Effect 和 Reconcile 显示枚举
Input Parse / OCR / Index 的显示枚举
Evidence、CitationLineage 和 Source Access 字段
Memory / ContextPack 用户可见字段
Quality Disclosure 指标和阈值
Artifact Download、Publication Delivery 和 Correction 字段
SSE Event Schema、Cursor 编码、Retention 和 Backpressure
Product 数据库表、索引、事务和 Migration
目标代码目录与模块物理边界
REST Path、API Version 和兼容适配器退役计划
Browser CSP、Sanitizer、Preview Sandbox 和 Download Token 细节
```

## 36. 依赖模块需要向 Product 暴露的最小能力

| 模块 | 第二轮所需 Contract |
| --- | --- |
| 02 Input | Upload、SourceObject、Parse/OCR、DocumentVersion、Index Readiness、Delete |
| 03 Knowledge | Evidence、CitationLineage、Sufficiency、Conflict、Source Access |
| 05 Memory | User-visible Memory、Context Disclosure、Correction/Delete、Privacy Delete |
| 06 Agent Core | RuntimeRequest、Run、Plan、Step、Interrupt、Signal、Publication、RunOutcome |
| 07 Capability | Capability/Skill Discovery、Selection Result、Unavailable Reason |
| 08 Tool Runtime | PreparedToolAction、ToolAttempt、EffectReceipt、UNKNOWN、Reconcile、Human Required |
| 09 Security | PrincipalContext、Authorization、Approval、Grant、Epoch、Revocation |
| 10 Observability & Eval | Trace/Eval Summary、Measurement Status、Quality Claim、Audit Link |
| 11 Infrastructure | Object Commit、Outbox Delivery、Cursor Store、Retention、Lease/Receipt 语义 |

## 37. 兼容入口原则

当前 `/completion`、`/workspace/simple/chat` 和 `/workspace/task` 等入口在未来 Program 中只能成为兼容适配器或被收口。它们不得长期保留相互独立的成功、审批、取消、Artifact 或 SSE 语义。

本文不定义具体迁移阶段和 Cutover；迁移必须进入 `.agent/programs/`。

---

# Part VII：Requirement、测试与完成证据

## 38. 第一轮 Requirement Index

| ID | Requirement |
| --- | --- |
| `ARCH-PRODUCT-001` | Product Surface 必须是统一北向产品边界 |
| `ARCH-PRODUCT-002` | Product Surface 不得成为第二个 Agent Controller |
| `ARCH-PRODUCT-003` | 所有正式产品入口必须复用统一 Agent Runtime Contract |
| `ARCH-PRODUCT-004` | Product 必须区分 Command、Query 和 Stream |
| `ARCH-PRODUCT-005` | HTTP、SSE、Queue 和 Client 状态不得决定领域成功 |
| `ARCH-PRODUCT-006` | Product 必须消费领域 Owner 的已提交事实 |
| `ARCH-PRODUCT-007` | Product Projection 必须可重建且不能反向写源事实 |
| `ARCH-PRODUCT-008` | AuthorizedView 必须重新校验 Principal、Scope 和 Security Epoch |
| `ARCH-PRODUCT-009` | 客户端身份、权限和 Secret 声明必须视为不可信 |
| `ARCH-PRODUCT-010` | 简单问答也必须进入 Agent Core 正式治理路径 |
| `ARCH-PRODUCT-011` | 页面或 Stream 断开不得取消 Run |
| `ARCH-PRODUCT-012` | Provisional Content 与正式 Publication 必须分离 |
| `ARCH-PRODUCT-013` | Upload、Parse、Index 和 Searchable 必须分离 |
| `ARCH-PRODUCT-014` | User Input 必须通过 Signal / Interrupt 语义进入 Agent Core |
| `ARCH-PRODUCT-015` | Approval UI 必须展示 Security 和 Tool Runtime 提供的受控事实 |
| `ARCH-PRODUCT-016` | Tool UNKNOWN 不得提供普通 Retry |
| `ARCH-PRODUCT-017` | Cancel Requested、CANCELLING 和终局必须分离 |
| `ARCH-PRODUCT-018` | Product 必须完整保留 RunOutcome 终局差异 |
| `ARCH-PRODUCT-019` | Artifact、Publication、Delivery、Render 和 Read 必须分离 |
| `ARCH-PRODUCT-020` | Quality Disclosure 不得把未测量状态冒充质量已证明 |
| `ARCH-PRODUCT-021` | Conversation、UserSubmission、RuntimeRequest、Run 和 Publication 必须有清晰关系 |
| `ARCH-PRODUCT-022` | 重复 RuntimeRequest 不得创建重复 Run |
| `ARCH-PRODUCT-023` | Frontend 只能展示后端提供的 Authorized AvailableAction |
| `ARCH-PRODUCT-024` | Projection Freshness、Domain Status 和 Connection Status 必须分离 |
| `ARCH-PRODUCT-025` | SSE 必须支持重新鉴权、恢复或 Snapshot Resync |
| `ARCH-PRODUCT-026` | Projection Gap 必须触发显式 Resync |
| `ARCH-PRODUCT-027` | Query 不得暴露 Raw Checkpoint、Secret 或隐藏思维链 |
| `ARCH-PRODUCT-028` | Citation 和 Artifact 内容访问必须独立授权 |
| `ARCH-PRODUCT-029` | Product 必须提供浏览器和客户端渲染安全边界 |
| `ARCH-PRODUCT-030` | Product UX Preset 不得形成 Runtime 旁路 |
| `ARCH-PRODUCT-031` | 第二轮 Contract 必须等待相关领域模块稳定后冻结 |
| `ARCH-PRODUCT-032` | 文档完成只能声明 Boundary Design Available，不得声明 implementation available 或 production ready |

## 39. 第一轮验证矩阵

```text
Document Governance
    正式文档和 Agent 镜像字节级一致
    模块入口和文档路由引用正确
    第一轮状态和第二轮待冻结边界明确

Ownership
    Product 不拥有 AgentRun、Approval、Tool Effect、Evidence、Memory、Eval
    Publication 与 ChannelDelivery Ownership 不混淆

Semantic Guards
    HTTP 2xx、SSE close、Queue ACK 不等于成功
    Disconnect 不取消 Run
    UNKNOWN 不允许普通 Retry
    Upload Accepted 不等于 Searchable

Scenario Review
    Normal QA
    Strict Grounded
    Upload / Ingestion
    Long-running reconnect
    User Input Interrupt
    Approval
    Tool UNKNOWN
    Cancellation
    Partial / Abstained / Refused / Blocked
    Artifact / Publication / Delivery

Future Contract Guard
    不在第一轮冻结数据库表
    不在第一轮冻结完整 DTO
    不在第一轮冻结 SSE Cursor 编码和 Retention 数值
```

## 40. 完成状态

本文和验证器完成后只能声明：

```text
design available
boundary foundation available
ownership aligned
scenario baseline available
second-round inputs identified
```

不能声明：

```text
contract-complete
implementation-spec-complete
implementation available
measurement proven
quality proven
production ready
```

第二轮 Product Surface 设计必须重新读取当时最新 `main` 的代码、测试、Migration、领域文档和运行证据，再完成状态机、Contract、存储、事务、兼容迁移和完整 Requirement-to-Evidence 闭环。

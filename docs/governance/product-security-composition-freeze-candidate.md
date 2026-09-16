# Product Security Composition Freeze Candidate

status: `READY_FOR_REVIEW / IMPLEMENTATION_NOT_AUTHORIZED`
base_main: `3cc0d43710d66ae7414c03cda04274f34ea538cb`
source_review: `REPO_WIDE_CURRENT_PATH_REVIEW`
production_readiness: `NOT_ESTABLISHED`

RB019 已经把现实 Effect send boundary 上最直接的错误路径关掉：外部结果 Unknown 不会因 restart replay 被升级完成；Mandatory Audit proof 会在发送前耐久提交并绑定 Security-owned requirement；manual reconciliation 只能消费匹配 provider effect 的 durable one-shot judgment；Tool Effect 的 Current Security fact identity 也不再由 trace 单独决定。

沿着这条链继续往上追以后，新的断点已经不在 06 Effect recovery 内部，而在 Product 请求怎样拿到 08 Security / Budget owner fact 并把它们注入 Agent Runtime。这个问题不应继续挂在 RB019 名下，也不适合通过给某个 resolver 补默认值来隐藏。

最简单的产品接线应该是：应用启动时构造一次 WorkspaceRuntimeComposition；Product Adapter 只携带 opaque decision ids；Security / Budget resolver 读取各自 Owner 的 durable fact；Agent Core 校验 scope / epoch / expiry / hash；通过后才进入运行和 Tool send gate。如果仓库已经具备这些对象，但启动时没有真正把它们接起来，那么继续增加新的 Security 状态机不会解决问题。

## Current source evidence

### Server startup 没有建立 WorkspaceRuntimeComposition binding

`src/backend/zuno/main.py::init_config()` 当前会初始化数据库、Product security action guard、Package-A ingestion、MCP guards 和默认 Agent，但没有调用 `configure_workspace_product_composition(...)`。

Repo-wide search 只找到两类 `configure_workspace_product_composition` 调用：

- 定义本身；
- test/runtime reset 时显式传 `None`，用于清空 binding。

没有找到 production startup 构造真实 `WorkspaceRuntimeComposition` 并绑定的 Current call site。

Workspace product runtime 对这个缺口采取 fail-closed：product profile 下 composition 为 `None` 时返回 `BLOCKED_CONFIGURATION`，不会自动回退到 synthetic resolver。

因此 Current 结论是：

```text
WORKSPACE_PRODUCT_COMPOSITION_BINDING = NOT_IMPLEMENTATION_PROVEN
```

这不是“resolver 已经生产接线、只是缺测试”。当前 source evidence 没有建立正式启动装配。

### SecurityDecision resolver 的 expiry contract 与 Current persistence 不一致

`PostgresSecurityDecisionResolver` 要求 owner fact 同时满足 tenant、workspace、principal、action、resource、epoch、decision、hash 和 expiry，并明确把 missing / malformed `expires_at` 当成 fail-closed。

但 Current `security_authorization_decisions` schema 没有 `issued_at / expires_at` 字段，`read_authorization_decision_fact()` 也没有返回 expiry。

Target Security reference 把 AuthorizationDecision 的 `issued_at / expires_at / refresh_before_effect` 放在 Detail Freeze Candidate 中，因此“需要过期语义”有 Target 根据；但 Current migration 没有完成对应持久化。

同时 Agent contract 的 `SecurityDecisionRef.expires_at` 仍是 optional，Agent Core validator 对缺失 expiry 并不会直接拒绝。由此可见 Current 不是一个已经冻结完成的单一语义：resolver 比当前 contract/persistence 更严格。

本阶段禁止用以下方式绕过：

- resolver 自己生成 `now()+5m`；
- 从 trace / request deadline 猜 expiry；
- 把 Approval deadline 直接当 AuthorizationDecision expiry；
- 因为 `expires_at` optional 就删除 Target refresh 语义。

需要先决定 Owner fact 的正式字段和 refresh 规则，再改 migration / resolver。

### Budget resolver 只有接口形状，没有 production owner store

`PostgresBudgetDecisionResolver` 明确禁止根据 request `budget_limits` 或 composition default 自行批准。它要求 `budget_decision_id` 对应 Server-owned owner fact。

但 Current `resolve_owner_fact()` 默认直接返回 `None`，注释要求 production binding/subclass 自己实现。Repo-wide search 没有找到 `PostgresBudgetDecisionResolver(...)` 的实例化，也没有找到 budget decision owner-store 的 Current implementation surface。

因此：

```text
BUDGET_OWNER_FACT_STORE = NOT_IMPLEMENTATION_PROVEN
BUDGET_RESOLVER_PRODUCTION_BINDING = NOT_IMPLEMENTATION_PROVEN
```

在 Budget owner store 出现前，不能把 request-declared limits 升级成 formal Budget Admission。

### PostgresSecurityApprovalFactSink 与 send-gate facts 目前不是一套 identity

`ToolControlPlaneRuntime` 会在 approval waiting / approved-before-effect 等阶段把 approval fact 写给 `PostgresSecurityApprovalFactSink`。这条 sink 直接写 `security_effective_epochs`、principal contexts、authorization decisions、audit requirements 和 approval rows。

Current fact payload 没有 `tenant_id`；sink 用 `workspace_id` 优先充当 tenant。真正 Tool Effect Gateway 则使用 `request.tenant_id`（缺失时才回退 user id），并使用另一套 action-scoped Epoch / Decision identity。

时间顺序也不同：Product admission 的 Security decision 必须在 Agent run 之前成立；approval fact sink 发生在 Tool Runtime 已经进入 approval 生命周期以后。因此它不能被描述成同一次 Product admission 的前置 owner fact。

这条 sink 需要先定性：

```text
A. Security authoritative writer
B. Approval ledger / projection
C. Legacy duplicate path to remove
```

在定性之前，不应只把 `tenant_id` 塞进去然后保留两套 Authority writer。

## Freeze boundary

新的 slice 只冻结 Product → Agent Runtime 的 Security / Budget composition，不重新设计 06 Effect Control，也不新增全局 Security Service。

### PSC-A — Production composition root

要求明确：

- server startup 在哪里创建 WorkspaceRuntimeComposition；
- engine / resolver / Tool runtime dependencies 由谁注入；
- test reset 与 production binding 如何隔离；
- composition 缺失继续 fail closed；
- 不允许 Product Adapter 自己 new resolver 形成旁路。

Acceptance evidence 至少包含一次真实 app/startup composition probe，而不是单独 new `WorkspaceAgentRuntime` 的 unit test。

### PSC-B — SecurityDecision owner fact

先冻结 AuthorizationDecision 的 Current first-stage contract：

```text
decision_id
tenant / workspace / principal scope
action / resource
decision
security_epoch_ref
prepared_action_hash（需要绑定现实动作时）
issued_at
expires_at / no-expiry 的显式语义
decision_hash
```

还要明确 refresh-before-effect 与 Tool send gate 的关系：Agent admission 的 allow 只能证明当时可进入计划；现实副作用发送前仍由 08/06 重新检查 current Security 条件。两层判断不能合并。

如果 Current schema 需要 migration，migration 只增加被这条 contract 真正消费的字段，不顺带实现全量 Target composed epoch。

### PSC-C — Budget owner fact

禁止让 `PostgresBudgetDecisionResolver` 继续以“Postgres”命名但没有 owner store。

两种合法方向：

- Build：定义最小 durable BudgetDecision store 和 resolver；
- Defer：Product profile 暂时继续 fail closed，并把 Budget formal admission 从当前可运行范围中明确拿掉。

如果没有真实业务使用 formal budget admission，优先 Defer，而不是为了完整架构增加新的预算服务。

### PSC-D — Approval fact sink ownership

必须决定 `PostgresSecurityApprovalFactSink` 的最终身份。

如果它只是 approval ledger / projection：

- 不再写会被当作 authorization authority 的表，或明确拆成 projection surface；
- tenant / workspace 字段保留真实作用域；
- send gate 不消费它作为 current allow。

如果它确实是 authoritative writer：

- 必须与 Product admission / Tool send gate 使用同一 Owner contract、tenant identity 和 epoch semantics；
- 不允许另一套 Gateway writer 同时产生不同 identity 的 authorization fact。

默认不接受“两套 writer 都保留，因为现在测试没冲突”。

## Required tests

实现阶段至少需要以下 fault / composition probes：

1. server startup 后 product profile 能取得非空 WorkspaceRuntimeComposition；reset 后仍 fail closed；
2. foreign tenant / workspace 的 SecurityDecision id 不能被 resolver 消费；
3. expired decision fail closed；fresh matching decision 可以 admission；
4. Agent admission 后、真正 side-effect send 前 SecurityEpoch revoke，仍由现有 pre-effect gate 阻止 provider；
5. same opaque decision id + changed durable content fail closed；
6. Budget owner fact 缺失时不允许 request limits 自批准；如果选择 Build，matching owner fact 才能 admission；
7. approval sink 不产生第二套可被误认为 current authorization 的冲突事实；
8. app startup / product request E2E 至少证明一次 Product Adapter → owner resolver → Agent admission 的真实 production composition path。

这些测试应进入 existing selected verification 或独立可重复的 product composition gate；不能只用 Mock resolver 证明 wiring。

## 不在本 slice 实现

本 freeze candidate 不授权：

- 新 Security microservice；
- 全局 Epoch Service；
- 跨 Store / remote 2PC；
- 完整 Target composed SecurityEpoch migration；
- Secret rotation 全协议；
- Audit class / pre-send-abort lifecycle 的后续状态机；
- Provider remote-query reconciliation；
- Cancel-in-flight orchestration；
- GraphRAG、Memory、Multi-Agent、Native Runtime 扩张。

这些问题有各自的 Owner 和 failure shape，不能借 Product composition 一次性收进来。

## Build / Buy / Extend / Defer

基础设施继续复用 PostgreSQL、现有 SecurityUnitOfWork、Agent resolver ports 和 FastAPI lifespan。当前问题没有证据要求引入外部 Policy Engine 或新的服务。

SecurityDecision persistence 属于 Extend：已有表与 UoW，只补正式 owner contract 需要的字段和一致性。

Budget owner store 当前优先 Defer，除非 Product requirements 能证明 formal Budget Admission 是当前必须上线的业务路径。

Approval sink 优先 Simplify：如果 repo-wide call-site review 证明它只是重复 ledger，应删除重复 authority write，而不是再设计第三套同步协议。

## Implementation authorization request

本文件目前只请求 Review，不授予实现权限。

如果后续批准，建议授权拆成四个可独立验收的 slice：

```text
PSC-A  FastAPI startup / WorkspaceRuntimeComposition production binding
PSC-B  SecurityDecision durable expiry/scope contract + resolver
PSC-C  Budget owner fact: explicit BUILD or DEFER decision
PSC-D  PostgresSecurityApprovalFactSink ownership cleanup
```

每个 slice 必须独立通过自己的 acceptance gate。PSC-A 绿色不能代替 PSC-B；Security resolver 能返回值也不能代替 Budget owner fact；删掉 duplicate sink 也不能证明 Product admission 已完整。

在用户明确批准前，`implementation_authorization = NOT_GRANTED`。
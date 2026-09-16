# Round 019 Post-Implementation Review

status: `CURRENT_REVIEW / ORIGINAL_RB019_P0_CLOSED / FOLLOWUP_GAPS_SCOPED / NO_NEW_IMPLEMENTATION_AUTHORIZATION`
current_main: `ff0f497e3eea862fa44b0a8d5979e9ad31ac5ad0`
selected_verification_run: `35056938670`
selected_result: `208 passed, 16 warnings in 28.28s`
artifact_id: `10431201132`
production_readiness: `NOT_ESTABLISHED`

RB019 最初冻结的是三条很窄的现实失败：外部 Effect 在 restart replay 时把 UNKNOWN 错误升级成 completed；`MANDATORY_BEFORE_EFFECT` 没有真正挡住缺少 durable audit proof 的发送；正式 Alembic entrypoint 仍引用已经退休的 settings 路径。三条问题都已经进入 main 修复，并由同一套 selected PostgreSQL verification 反复回归。

实现以后继续做 fault review，又暴露出几条紧邻原边界的问题。这些问题没有要求增加新模块。修复集中在已有 06 Tool Runtime & Effects、08 Security & Governance 和 Platform persistence primitive 上：audit proof 发送后必须关闭 capacity lifecycle；06 消费的 proof 必须绑定 08 真正持久化的 AuditRequirement；manual reconciliation 只能根据已经耐久保存、且 provider effect identity 匹配的 judgment 收敛；Security owner 的 Effect epoch / AuthorizationDecision identity 不能在数据库发生冲突时返回一份只存在于调用参数里的“成功 receipt”。

这些 follow-up 现在也已经进入 main。当前可以证明的结果是：

- unresolved Effect 重启以后继续保持 `reconcile_required / UNKNOWN_EFFECT`，同一 action 不会因为存在 result ref 就升级完成；
- conclusive reconciliation 可以收敛 executed / not-executed，且 response-loss replay 不会重新 dispatch；
- manual judgment 必须匹配 durable reconciliation 的 `provider_effect_id`，同一 reconciliation 在当前 one-shot schema 下只能有一个 authoritative judgment；exact replay 幂等，不同第二结论 fail closed；
- mandatory audit 缺 committed proof 时 executor 为 0；proof 与 Security-owned AuditRequirement 的 id/hash、AuthorizationDecision、PreparedAction hash、SecurityEpoch 和 tenant context 绑定；requirement 漂移会在 provider send 前 fail closed；
- provider dispatch 以后 audit row 进入 `effect_observed`，不会永久占用 `durable` capacity；
- Tool Effect 的 Current SecurityEpoch identity 不再由 `trace_id` 单独决定。同一 trace 下的不同 action 获得不同 epoch identity，同一 action 即使 response-loss replay 使用不同 trace 仍命中同一 durable Security fact；
- `ensure_effective_epoch()` 和 `ensure_authorization_decision()` 会重新读取 durable row 并校验 immutable identity，不再把 `ON CONFLICT DO NOTHING` 当成“请求内容已经持久化”的证明；
- fresh PostgreSQL 可以通过正式 Alembic entrypoint 直接 upgrade 到 head，不再需要 `zuno.settings` test shim。

这些结果仍然只属于 selected verification。Full CI、生产部署、真实 Provider、真实法院外围系统、性能、HA / DR 和 Production Qualification 都没有因此成立。

## 剩余问题已经越过原 RB019 实施面

继续沿 06 / 08 边界检查以后，剩余问题已经不再是原三条 P0 的小修补。

### Reconciliation 还缺真实 Provider query

Current 已经有 durable UNKNOWN、escalation、one-shot manual judgment 和 conclusive resolver，但没有找到 production provider-facing `query_effect(action / remote correlation)` adapter。今天能证明的是“已知结论怎样耐久收敛”，不能写成“系统可以自动向所有 Provider 对账”。没有 remote query 能力的高风险 Tool 继续只能进入人工路径，不能猜测现实结果。

manual reviewer 的 Current authority 也仍然很弱：repository 只用 `workspace-user:manual-reviewer` 前缀判断 reviewer。provider effect identity 和 judgment conflict 已经闭合，但 reviewer role / tenant / approval policy 本身还没有独立 authoritative binding。当前 schema 同时只有 `UNIQUE(tenant_id, reconciliation_id)` 的 one-shot judgment；是否需要多次 assessment 应由实际工作流和 Evidence 决定，不因为“更完整”就新增 migration。

### Mandatory Audit 的 policy 与生命周期还没有完整闭环

Current 已经证明 committed proof gate、matching Security requirement binding 和 post-dispatch capacity close。剩余问题集中在三个不同方向：

- 08 的 durable requirement 还没有表达 Target 中 `BEST_EFFORT | DURABLE | MANDATORY_BEFORE_EFFECT` 的 audit class；当前不能把 legacy `trace / trace_and_review` 字符串自行映射成新的 authority；
- `infra_mandatory_audit_events` 没有 tenant column。proof identity / payload 已经包含 tenant，但这不等于数据库级 cross-tenant isolation 已被证明；
- proof 已经提交、但真正 send 前又被 Security / sandbox 阻断时，不能写成 `effect_observed`，现有 `durable` capacity 又可能无法释放；send 后 crash、来不及写 lifecycle close 也有类似 recovery 问题。仓库没有冻结足够明确的 audit-capacity terminal semantics，因此不在本轮发明 `ABORTED` 一类新状态。

### EffectiveSecurityEpoch 的 Current 修复仍低于 Target composed epoch

Current Tool Effect path 已经移除 trace-only epoch identity，使用稳定 action scope，并校验 durable Epoch / AuthorizationDecision identity。Target Security contract 仍更完整：EffectiveSecurityEpoch 可以表达 workspace / principal / resource scope 和多个 epoch 组成部分。Current `security_effective_epochs` schema 没有这些字段。

这意味着当前修复关闭的是“trace 被错误当作业务 identity”和“durable row 与返回 receipt 不一致”，没有实现 Target composed SecurityEpoch。继续扩展需要独立 schema / migration / recovery 设计。

### Workspace product Security composition 尚未建立 Current implementation proof

Repo-wide source review 能找到 `WorkspaceRuntimeComposition`、`PostgresSecurityDecisionResolver`、`PostgresBudgetDecisionResolver` 和 `configure_workspace_product_composition()`，也能看到 product profile 在 composition 缺失时明确 fail closed；但没有找到 production startup 把一个真实 `WorkspaceRuntimeComposition` 传给 `configure_workspace_product_composition(...)` 的调用，也没有找到 `PostgresSecurityDecisionResolver(...)` 的生产实例化。当前唯一明确调用 `configure_workspace_product_composition` 的代码是测试/状态 reset 使用的 `None`。

因此准确结论是 `PRODUCT_COMPOSITION_BINDING: NOT_IMPLEMENTATION_PROVEN`，不是“产品运行时已经接好但测试不够”。

这里还存在两个相邻 source gap，进一步说明不应该在 RB019 里顺手补 wiring：

1. `PostgresSecurityDecisionResolver` 当前要求 owner fact 提供 `expires_at`，但 `security_authorization_decisions` 的 Current schema / `read_authorization_decision_fact()` 没有对应字段。Security Target 把 issued / expiry / refresh 语义列入 AuthorizationDecision candidate；如何落地需要一次明确 schema 决策。
2. `PostgresSecurityApprovalFactSink` 在 Tool approval 阶段写入同一组 Security authority tables，但传入 fact 没有 `tenant_id`，sink 会优先把 `workspace_id` 当 tenant；真正 Effect Gateway 则使用 request tenant。该 sink 发生在 Agent admission 之后，不是同一次 run 的前置 Security owner fact，但它是否应该继续写 authority tables、还是只作为 approval ledger/projection，需要单独收敛 Owner 语义。

### Cancel-in-flight 仍然只有 primitive

`ToolCancellationReceipt`、AsyncJob 状态和相关 repository primitive 已经存在，但没有新的 Evidence 证明“用户取消 / deadline / plan cancel → provider cancel → callback race → final Effect truth”形成生产 orchestration。这个问题保持 `NOT_IMPLEMENTATION_PROVEN`。

## Current / Target / Evidence / Unknown

**Current**：`main@ff0f497e3eea862fa44b0a8d5979e9ad31ac5ad0`；GitHub run `35056938670`；selected pytest `208 passed, 16 warnings in 28.28s`。RB019 原始 AUTH-A/B/C 与紧邻的 audit lifecycle、requirement binding、manual judgment binding、Effect Security fact identity 已经进入 main regression。

**Target**：继续以 01–09 canonical Owner map 为准。06 拥有 Effect / Reconciliation truth；08 拥有 Security / Approval / AuditRequirement / expiry-refresh semantics；Platform 只提供 durability、lease、fencing、clock 等物理 primitive。

**Evidence**：上述 main SHA / run / artifact，以及历史 #201/#203/#205/#207/#210 fault runs。历史负向 Evidence 不删除，只标明后续 closing SHA / run。

**Unknown / Not Proven**：provider remote query、authoritative manual reviewer binding、multi-assessment 是否需要、audit class、audit cross-tenant DB isolation、pre-send-abort / crash-replay audit lifecycle、Target composed SecurityEpoch、production WorkspaceRuntimeComposition binding、SecurityDecision expiry persistence、approval fact sink 的最终 Owner 定位、cancel-in-flight orchestration、Full CI、Production Readiness。

## 下一阶段需要新的 scoped freeze

原 RB019 的实施授权已经完成它要解决的问题。后续不应该继续以“RB019 follow-up”名义扩张。

下一轮如果继续实现，建议先冻结一个独立的 **Product Security Composition** slice，只回答四个问题：

```text
PSC-1  production WorkspaceRuntimeComposition 在哪里、何时、由谁绑定？
PSC-2  Product admission 消费的 SecurityDecision owner fact 从哪里产生，expiry / refresh 怎样耐久表达？
PSC-3  PostgresSecurityApprovalFactSink 是 authoritative writer、approval ledger，还是可删除的 legacy projection？
PSC-4  tenant / workspace / principal / resource scope 如何在 Product admission 与 Tool send gate 之间保持同一套 identity？
```

在这四个问题冻结前，不建议新增 Security Service、全局 Epoch Service、跨 Store 2PC，也不建议为了让 resolver“能返回值”而随意补一个 synthetic expiry。
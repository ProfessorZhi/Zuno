# Product Security Composition Implementation Status

status: `PSC_A_B_IMPLEMENTED_SELECTED_VERIFIED / PSC_C_DEFERRED_BY_SCOPE / PSC_D_OWNERSHIP_RESOLVED_SELECTED_VERIFIED`
current_main_evidence: `293fa144f70be0467d1363eb3662d1b39a874cf8 / run 35202465804 / 214 passed, 22 warnings`
production_readiness: `NOT_ESTABLISHED`
source_freeze: [`product-security-composition-freeze-candidate.md`](product-security-composition-freeze-candidate.md)
current_evidence: [`../evidence/current-test-baseline.md`](../evidence/current-test-baseline.md)

Product Security Composition freeze candidate 在 `main@c283d364...` 时冻结了四个独立问题。PSC-A 与 PSC-B 已实现并进入 main selected verification；PSC-C 按 freeze 的 Build / Defer gate 选择 `DEFERRED_BY_SCOPE`，没有为了架构对称性新建 Budget owner service；PSC-D 已把重复 Security authority writer 收敛成 approval event projection。四个 slice 都已有明确 Current 决策，但这不等于 Product Runtime 已完整可执行或 Production Ready。

## PSC-A — Production composition root

**Current：IMPLEMENTED / SELECTED VERIFIED。**

FastAPI `init_config()` 已经在数据库 bootstrap 后建立 server-owned `WorkspaceRuntimeComposition`。Composition 使用现有 PostgreSQL runtime schema 的 `PostgresAgentRunStore`，并注入 Tool、Security、Infrastructure UoW factories。fresh-PostgreSQL probe 证明 runtime state、checkpoint 与 pending interrupt 可以跨新的 Store instance 恢复，真实 startup probe 证明正式 `init_config()` 能建立 composition，reset 后 binding 会清除。

Current evidence 绑定 `main@c3938ccb92c8234977ebd5e2956acec697981d24`、GitHub Actions run `35071244101`、PostgreSQL 16.15；selected suite 得到 `210 passed, 18 warnings in 32.79s`，artifact `10436282705`。这仍然是 selected verification，不是 Full CI 或 Production Qualification。

PSC-A 还恢复了真实 startup path 上一个已有的调用错误：Package-A ingestion runtime 现在按其 keyword-only contract 传入。这个修复只是让正式启动链能够继续到 product composition，不改变 ingestion Owner。

PSC-A 的退出条件已经满足；后续不要继续在这一 slice 增加 resolver、Budget、Approval 或新的 Runtime topology。

## PSC-B — SecurityDecision owner fact

**Current：IMPLEMENTED / SELECTED VERIFIED / DEFAULT NOT ENABLED WITHOUT EXPLICIT TTL POLICY。**

PSC-B 复用 08 Security 的既有 Policy/Persistence boundary，没有新增 Security Service。`PostgresSecurityDecisionResolver` 现在同时承担 Product owner port 的发行与解析：当前 Tool policy 先由 `ToolSecurityGate` 评估，随后把 tenant / workspace / principal / action / selected resource、SecurityEpoch、issued/expiry 与 durable hash 写入 Security-owned PostgreSQL facts；Product Adapter 只得到 opaque `decision_id + security_epoch_ref`，Agent Runtime 再通过 owner resolver 读取并重新校验。

Migration `20260916_58` 只给现有 Security surface 增加 PSC-B 真正消费的字段：`security_principal_contexts.workspace_id` 与 `security_authorization_decisions.expires_at`。旧 row 保持 nullable，不伪造历史 expiry。`created_at` 作为 owner-issued `issued_at` 被 resolver 读取。Product SecurityDecision 的 durable hash 和 Agent owner-ref hash都覆盖时间边界；旧无时间字段 ref 保持原 hash 形状。

授权寿命没有在代码中硬编码。只有 deployment config 显式设置正值 `server.security.product_decision_ttl_seconds` 时，startup 才绑定 Product decision issuance；缺失、`null` 或非正值继续 fail closed。仓库 example 默认仍是 `null`。因此 PSC-B 证明的是“受配置控制的正式 owner path 已实现”，不是“任意部署默认自动授权”。

Current evidence 绑定 `main@a727bf8000bdda38614905d710c093e1fcc6807a`、GitHub Actions run `35121830478`、PostgreSQL 16.15；selected suite 得到 `213 passed, 21 warnings in 36.93s`，artifact `10458161042`。新 probes 已证明：matching owner fact 可以 issue→persist→resolve；foreign tenant / workspace、过期 fact、同 identity durable content tamper 均 fail closed；同 Product submission replay 不刷新授权寿命；真实 `WorkspaceAgentRuntime.start()` 可以消费 Security owner fact，并在 PSC-C 未绑定时准确停在独立 Budget blocker。

PSC-B 还把 Security resource scope 与 Agent `allowed_tools` 收窄到当前 plan 实际选择的 tool，避免 session 中其他已注册 Tool 扩大 owner decision 的资源范围。

Product admission 的 Security allow 只证明“现在可以进入该计划动作”。现实副作用真正发送前仍由既有 08/06 pre-effect gate 重新检查当前 Security 条件；PSC-B 没有合并这两层 Authority。

## PSC-C — Budget owner fact

**Current：DEFERRED_BY_SCOPE / FORMAL OWNER ADMISSION REMAINS FAIL-CLOSED。**

Current Workspace API / Web surface 暴露的 `WorkspaceTaskBudget` 只有 `max_steps / max_tokens / timeout_seconds / cost_ceiling`。这些值来自调用方，用于约束 Runtime mechanics；repo-wide source review 没有发现 durable BudgetDecision owner store、issuer、admin/billing policy flow，或其他能够回答“谁批准这次正式预算”的当前业务 Authority。

因此本 slice 选择 freeze 明确允许的 Defer 方向，而不是为了接口对称性创建新表或 Budget Service。production composition 继续保持：

```text
budget_decision_resolver = None
```

此前名为 `PostgresBudgetDecisionResolver` 的类没有 PostgreSQL owner store、没有 production instantiation，默认 `resolve_owner_fact()` 只能返回 `None`。PSC-C 已删除这个误导 surface，保留通用 `BudgetDecisionResolver` owner port 作为未来真实业务需要出现后的扩展点。

PostgreSQL regression probe 会给真实 `WorkspaceAgentRuntime` 显式传入 caller-declared budget limits；Security owner fact 通过以后，Runtime 仍然得到 `budget_owner_resolver_unbound`，不生成 `BudgetDecisionRef`，也不会调用模型。这证明 request limits 可以限制运行参数，但不能自批准 formal Budget Admission。

PSC-C 的重新 Build 条件不是“架构图缺一个模块”。只有出现明确 Product requirement，并能指出真实 Budget owner / policy source，例如组织或 workspace quota、billing policy、管理员批准的 run envelope 或等价 durable Authority，才重新评估最小 owner store。

## PSC-D — Approval fact sink ownership

**Current：OWNERSHIP RESOLVED / PROJECTION ONLY / SELECTED VERIFIED。**

Source review 发现旧 `PostgresSecurityApprovalFactSink` 在 Tool approval 生命周期里会再次写 `SecurityEpoch`、PrincipalContext、AuthorizationDecision、Approval rows 与 AuditRequirement，而同一 Tool send path 已经通过正式 `SecurityUnitOfWork` / Gateway 写入并消费自己的 Security authority facts。两套 writer 使用不同 identity / tenant 口径，继续并存会让同一现实动作出现两个可被误认为 Authority 的 Security 事实来源。

PSC-D 没有增加新 Approval Service。具体 sink 已降级并改名为 `PostgresSecurityApprovalEventSink`：它只把 `approval_waiting / approved_before_effect` 等生命周期事件写入既有 `security_outbox_events`，用于 durable ledger / projection；它不再写任何 Security authority table。Tool Runtime 直接把真实 `request.tenant_id` 传入 projection，不再用 workspace 代替 tenant。

`ensure_security_event()` 同时收紧幂等语义：同 `(tenant_id, idempotency_key)` 的 exact replay 返回同一持久化事件；如果 aggregate、topic 或 payload/hash 改变则 fail closed，不能静默吞掉 identity collision。

Current evidence 绑定 `main@293fa144f70be0467d1363eb3662d1b39a874cf8`、GitHub Actions run `35202465804`、PostgreSQL 16.15；selected suite 得到 `214 passed, 22 warnings in 39.74s`，artifact `10488681251`。PSC-D probe 证明同一 approval event exact replay 只留下 1 条 `security_outbox_events`；tenant / workspace / PreparedAction hash 保持真实绑定；同时 `security_effective_epochs`、`security_principal_contexts`、`security_authorization_decisions`、`security_approval_requests`、`security_approval_decisions`、`security_audit_requirements` 在该 projection path 上全部保持 0。changed-content replay 会明确 conflict。

这项 ownership cleanup 不等于新增 Product Approval workflow。`WorkspaceRuntimeComposition.approval_flow` 仍然是 `"none"`；需要人工 Approval 的现实 Effect 继续由现有 Tool/Security send-boundary lifecycle 管理。PSC-D 只消除了第二套 Authority writer。

## PSC 收口后的边界

```text
PSC-A  production composition root                     IMPLEMENTED / SELECTED VERIFIED
PSC-B  Product SecurityDecision owner fact             IMPLEMENTED / SELECTED VERIFIED
PSC-C  formal Budget owner admission                    DEFERRED_BY_SCOPE / FAIL-CLOSED
PSC-D  approval sink ownership                          PROJECTION_ONLY / SELECTED VERIFIED
```

这组结果说明 Product → Agent 的 composition 与 Security owner path 已有 Current implementation，Budget formal admission 被有意拿出当前可运行范围，旧 approval side-writer 已降级为 projection。它仍不能扩写成“完整 Product Admission 已实现”：当前没有 formal Budget owner fact，也没有新的 Product Approval flow；真实 Provider、完整业务 E2E、Full CI 和 Production Qualification 仍需要各自证据。

后续工作继续受原 freeze 排除项约束：不因 PSC 收口而引入新 Security/Budget microservice、全局 Epoch Service、跨 Store 2PC、GraphRAG / Memory / Multi-Agent 扩张，也不顺带处理 remote reconciliation 或 cancel orchestration。

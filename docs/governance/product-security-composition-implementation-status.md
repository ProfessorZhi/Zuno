# Product Security Composition Implementation Status

status: `PSC_A_B_IMPLEMENTED_SELECTED_VERIFIED / PSC_C_D_OPEN`
current_main_evidence: `a727bf8000bdda38614905d710c093e1fcc6807a / run 35121830478 / 213 passed, 21 warnings`
production_readiness: `NOT_ESTABLISHED`
source_freeze: [`product-security-composition-freeze-candidate.md`](product-security-composition-freeze-candidate.md)
current_evidence: [`../evidence/current-test-baseline.md`](../evidence/current-test-baseline.md)

Product Security Composition freeze candidate 在 `main@c283d364...` 时冻结了四个独立问题。PSC-A 与 PSC-B 现在都已经落地并进入 main selected verification；PSC-C 的 Budget owner fact 与 PSC-D 的 Approval writer ownership 仍保持独立未闭环。

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

**Current：OPEN / NOT IMPLEMENTED。**

`PostgresBudgetDecisionResolver.resolve_owner_fact()` 默认仍没有 production owner store。PSC-A 保持：

```text
budget_decision_resolver = None
```

不允许 request-declared budget limits 或 composition default 直接升级为 formal Budget Admission。

下一步仍需做显式 Build / Defer 决策。若没有当前 Product requirement 证明 formal Budget Admission 是上线前置条件，应继续优先 Defer，而不是为了对称性新建预算服务。

## PSC-D — Approval fact sink ownership

**Current：OPEN / OWNERSHIP NOT RESOLVED。**

PSC-A 没有绑定 `PostgresSecurityApprovalFactSink`：

```text
security_approval_sink = None
approval_flow = "none"
```

这是有意的 fail-closed 边界。当前 sink 与 Effect send-gate Security writer 使用不同 identity / tenant 口径，而且发生在 Tool approval 生命周期内部；在明确它是 authoritative writer、ledger/projection 还是 legacy duplicate path 之前，不把它塞进新的 production composition。

## 下一实施顺序

建议继续保持独立验收：

```text
PSC-B  SecurityDecision owner fact / resolver contract
PSC-C  Budget owner fact BUILD-or-DEFER
PSC-D  Approval fact sink ownership cleanup
```

PSC-B 已通过 selected verification。下一步只判断 PSC-C 的 BUILD-or-DEFER；PSC-D 的删除或降级也不能反过来当成完整 Product Admission 已完成。

任何后续实现都继续受原 freeze 的排除项约束：不引入新 Security microservice、全局 Epoch Service、跨 Store 2PC、GraphRAG / Memory / Multi-Agent 扩张，也不顺带处理 remote reconciliation 或 cancel orchestration。
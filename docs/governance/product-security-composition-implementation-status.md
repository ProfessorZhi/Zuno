# Product Security Composition Implementation Status

status: `PSC_A_IMPLEMENTED_SELECTED_VERIFIED / PSC_B_C_D_OPEN`
current_main_evidence: `c3938ccb92c8234977ebd5e2956acec697981d24 / run 35071244101 / 210 passed, 18 warnings`
production_readiness: `NOT_ESTABLISHED`
source_freeze: [`product-security-composition-freeze-candidate.md`](product-security-composition-freeze-candidate.md)
current_evidence: [`../evidence/current-test-baseline.md`](../evidence/current-test-baseline.md)

Product Security Composition freeze candidate 在 `main@c283d364...` 时冻结了四个独立问题。PSC-A 现在已经落地并进入 main selected verification；PSC-B、PSC-C、PSC-D 的 Authority / Contract 问题没有因为 composition root 可用而自动解决。

## PSC-A — Production composition root

**Current：IMPLEMENTED / SELECTED VERIFIED。**

FastAPI `init_config()` 已经在数据库 bootstrap 后建立 server-owned `WorkspaceRuntimeComposition`。Composition 使用现有 PostgreSQL runtime schema 的 `PostgresAgentRunStore`，并注入 Tool、Security、Infrastructure UoW factories。fresh-PostgreSQL probe 证明 runtime state、checkpoint 与 pending interrupt 可以跨新的 Store instance 恢复，真实 startup probe 证明正式 `init_config()` 能建立 composition，reset 后 binding 会清除。

Current evidence 绑定 `main@c3938ccb92c8234977ebd5e2956acec697981d24`、GitHub Actions run `35071244101`、PostgreSQL 16.15；selected suite 得到 `210 passed, 18 warnings in 32.79s`，artifact `10436282705`。这仍然是 selected verification，不是 Full CI 或 Production Qualification。

PSC-A 还恢复了真实 startup path 上一个已有的调用错误：Package-A ingestion runtime 现在按其 keyword-only contract 传入。这个修复只是让正式启动链能够继续到 product composition，不改变 ingestion Owner。

PSC-A 的退出条件已经满足；后续不要继续在这一 slice 增加 resolver、Budget、Approval 或新的 Runtime topology。

## PSC-B — SecurityDecision owner fact

**Current：OPEN / NOT IMPLEMENTED。**

`PostgresSecurityDecisionResolver` 与 Current Security persistence 仍存在 contract gap。Target reference 要求 AuthorizationDecision 具备 issued / expiry / refresh 语义，而 Current `security_authorization_decisions` durable surface 没有完成这套字段与 resolver 的一致实现。

PSC-A 明确留下：

```text
security_epoch_ref = ""
security_decision_resolver = None
```

因此 Product tool-plan admission 仍不会因为 PSC-A 绿色而获得 synthetic Security allow。

PSC-B 实现前仍要先冻结：

- AuthorizationDecision 的正式 durable expiry/no-expiry 语义；
- workspace / principal / resource scope 从哪一个 Security-owned fact 得到；
- Product admission epoch 与现实 Effect send 前 continuous authorization 的分工；
- owner decision hash 覆盖哪些稳定字段。

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

PSC-B 通过以后再判断 PSC-C；PSC-D 的删除或降级不能反过来当成 Product Security Admission 已完成。

任何后续实现都继续受原 freeze 的排除项约束：不引入新 Security microservice、全局 Epoch Service、跨 Store 2PC、GraphRAG / Memory / Multi-Agent 扩张，也不顺带处理 remote reconciliation 或 cancel orchestration。
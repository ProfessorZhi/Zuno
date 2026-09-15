# Round 019 P0 Implementation Freeze

status: `READY_FOR_SCOPED_IMPLEMENTATION_AUTHORIZATION`
base_main: `4a1875c19fa2292ed34c332098f850bbf4c95841`
module_detail_freeze: `SELECTED_BOUNDARIES_ONLY`
implementation_authorization: `REQUESTED / NOT_YET_GRANTED`
production_readiness: `NOT_ESTABLISHED`

这份文档把 Round 019 已经由 Current Evidence 证明的 P0 implementation gaps 收敛成可以直接实施的最小工程切片。它不重新设计九模块，也不把任何 Target 升级成 Current。目标只有一个：在不扩大架构面的前提下，先关闭现实副作用 send boundary 上已经确认的两条错误路径，再恢复正式 migration entrypoint，使后续 fault verification 有可信基础。

本轮不批准 GraphRAG 扩张、Persistent Multi-Agent、Native Runtime 扩张、长期 Memory 新服务或新的 Version Service。它们继续受 baseline / A/B / kill test 约束。

## Slice P0-A — 保持 UNKNOWN Effect 的 certainty，直到 Reconciliation 真正收敛

### Current failure

Current `ToolInvocationGateway` 已经能够在外部动作结果不确定时耐久保存：

- `ToolAttempt=UNKNOWN / DISPATCHED`；
- `ToolExecutionReceipt=UNKNOWN / UNKNOWN_EFFECT`；
- `Reconciliation=OPEN / RECONCILE`；
- 第一次调用向上返回 `reconcile_required / UNKNOWN_EFFECT`。

但 restart 后使用同一 action / idempotency identity replay 时，当前上行语义只看到一个通用 `replayed + result_ref`，没有区分这个引用指向 confirmed EffectReceipt，还是仍未关闭的 Reconciliation。Runtime 因而可能把 unresolved effect 错误升级成 `completed`。

这是 certainty 解释错误，不是 duplicate dispatch 问题。现有诊断中 executor 没有第二次执行。

### Minimal change

不新增新的全局状态机。修复集中在现有 06 → 04 的 typed result boundary：

1. replay 结果必须携带足以区分以下事实的 typed outcome：
   - confirmed executed；
   - confirmed not executed；
   - outcome unknown / reconciliation open；
   - manual reconciliation required；
   - async/pending result（如果已有现有语义）。
2. Runtime 只有在收到 conclusive Effect truth 时才能把 side-effecting Step 推进为 completed / accepted。
3. OPEN / WAITING_PROVIDER / ESCALATED reconciliation 在重启和重复调用后继续保持 reconciliation-required，不因为存在 `result_ref` 就升级 certainty。
4. 现有 idempotency identity、PreparedAction、Attempt 和 EffectReceipt identity 保留，不创建第二套 key。

### Reconciliation convergence

保存 UNKNOWN 只是起点。当前已有 `escalate_due_reconciliations()` 和 `record_manual_effect_assessment()`，但没有证据表明它们最终修复 Effect truth。

第一阶段只实现能够闭环 Current 已有数据模型的最小 convergence：

- 定义一个 conclusive reconciliation write path，输入必须绑定 action identity、matching open reconciliation、当前 evidence / remote correlation 或 authorized manual assessment；
- 结果只允许 `CONFIRMED_EXECUTED | CONFIRMED_NOT_EXECUTED | STILL_UNKNOWN | MANUAL_REQUIRED` 或当前 schema 的等价枚举；
- conclusive 结果写入后，Reconciliation 进入 resolved 语义，并形成/更新上层可消费的 typed effect certainty；
- `STILL_UNKNOWN` 不伪装成 resolved success；
- manual assessment 只有在它给出 conclusive effect judgment 时才可以驱动 resolved truth；纯备注不改变 certainty。

如果 Current schema 无法表达一个稳定 `ReconciliationReceipt`，允许在 06 Owner 内增加最小 receipt surface；禁止把它放到 Runtime 或 Telemetry 里。

### Remote query boundary

本切片不要求一次性支持所有 Provider 的 remote query。先定义 provider-facing reconciliation port：

```text
query_effect(action / external correlation)
    -> CONFIRMED_EXECUTED
     | CONFIRMED_NOT_EXECUTED
     | STILL_UNKNOWN
     | UNSUPPORTED
```

只有具体 Tool/Provider 真正拥有可验证查询能力时再实现 adapter。没有 remote query 的高风险 Tool 可以直接进入 manual path；不得为了自动化完整度猜测结果。

### Required tests

必须恢复并转绿原 restart replay fault probe：

```text
first call -> UNKNOWN + OPEN reconciliation
restart process/runtime
same action replay
executor_calls remains 1
runtime remains reconciliation_required
no completed until conclusive reconciliation
```

新增至少三条：

1. manual conclusive executed → resolved → replay returns confirmed executed；
2. manual conclusive not-executed → resolved → only then a new send may be considered after fresh security/plan checks；
3. STILL_UNKNOWN / MANUAL_REQUIRED → replay never upgrades to completed。

### Exit / kill condition

如果某类 Tool 不产生现实副作用，或者远端协议天然同步且结果可证明，不强制进入完整 reconciliation lifecycle。Effect Control 复杂度只服务真正存在 uncertain external effect 的 operation。

## Slice P0-B — `MANDATORY_BEFORE_EFFECT` 必须在 send boundary 前消费 committed audit proof

### Current failure

Current Security 可以产生 matching `AuditRequirement`，Infrastructure 也已经提供 `record_mandatory_audit()` / `assert_audit_durable_for_effect()`，但 production Tool send path 没有把 durable audit proof 接成真正的 dispatch gate。

现有 fault probe 已经证明：

```text
AuditRequirement exists
+ durable audit receipt absent
-> provider executor still called
-> EffectReceipt created
-> completed
```

这违反 Target：Requirement 只说明“必须审计”，不能证明“审计已经耐久提交”。

### Minimal change

不新建 Audit Service。复用现有 08 requirement + infrastructure durable audit primitive：

1. Gateway 在 dangerous provider dispatch 前解析当前 PreparedAction 对应的 AuditRequirement；
2. 若要求为 `MANDATORY_BEFORE_EFFECT`，必须验证 matching durable audit proof 已 committed；
3. proof 至少绑定当前 action identity/hash、requirement identity / policy epoch，以及当前实现已有的 durability identity；
4. 缺失、mismatch、过期或无法确认时 fail closed，executor 调用必须为 0；
5. 如果动作在队列中等待导致 action hash / policy epoch / approval 变化，旧 audit proof 不自动继承。

普通 telemetry span、普通 log、Security requirement row 都不能作为 durable audit proof 的替代品。

### Transaction / ordering

禁止持有数据库 transaction / lock 等待远端 provider。建议顺序保持：

```text
PreparedAction / Attempt intent durable
-> current Security / Approval / Secret checks
-> mandatory audit durability proof
-> COMMIT local prerequisites
-> provider send
-> effect observation / receipt
```

Audit proof 的具体持久化 boundary 可以继续复用 Current Infrastructure，不要求跨 06/08/remote 做 2PC。

### Required tests

必须恢复并转绿原 Mandatory Audit negative probe：

```text
requirement exists
no durable proof
executor_calls == 0
no EffectReceipt
attempt is NOT_DISPATCHED / blocked
```

另加：

1. matching durable proof → send allowed；
2. proof action hash mismatch → send blocked；
3. policy/security epoch changes after proof → new protected send re-evaluates；
4. audit storage unavailable → high-risk effect fail closed。

### Exit condition

只有被 policy 标记 `MANDATORY_BEFORE_EFFECT` 的动作承担这个强门。低风险只读/普通 telemetry 不被强行提升到同一 durability 成本。

## Slice P0-C — 修复正式 Alembic entrypoint，再把 migration evidence 当作可执行入口

`infra/db/alembic/env.py` 仍然导入 `zuno.settings.resolve_app_config_path`，Current settings 已经位于 `zuno.platform.settings`。此前 PostgreSQL fault probes 用 test-only alias 绕过这一 blocker；这不能继续作为正式 deployment evidence。

最小修复：

- 更新正式 import 到当前 canonical settings path；
- 不改变 migration body 和历史 revision；
- fresh PostgreSQL 上执行正式 `alembic upgrade head`，不允许 test-only module alias；
- 至少补一次 upgrade path smoke，证明入口能真正到达 migration chain。

这个切片属于基础设施维护，不应和 Effect/Audit 业务修复放进同一个 transaction 或状态设计。

## 暂不实施的两项 P0 文档结论

### Memory / Context Authority

文档已经关闭 Authority：Memory Provider 非权威，08 管 recall/lifecycle，01/04 消费当前 snapshot，02 Domain truth 优先。当前没有 A/B 证明 structured long-term memory 值得继续扩张，因此本阶段不新增 Memory Service、MemoryEpoch、全局 conflict resolver 或新的 approval workflow。

下一步只有两种合法方向：

- 先做 Memory on/off A/B，证明跨会话收益后再冻结持久化与 concurrency contract；
- 无收益则删除或缩小 structured long-term memory，只保留 Raw Event / task summary / context assembly。

### Dependency version drift

总体与模块文档已经把 version ownership 与 re-resolution / Replan 讲清。代码实现要等 P0-A/B 收敛后，再做一个独立 E2E：Plan 基于 Capability/Provider/Tool v1，dispatch 或 resume 前切到 v2，验证等价替换可以 re-resolve、语义变化必须 Replan/Review。禁止引入全局 Version Service。

## Scoped implementation authorization request

若用户批准本 Freeze，下一阶段只授权以下三类业务/基础设施修改：

```text
AUTH-A  06 Effects + 04 Runtime：Effect certainty replay + Reconciliation convergence
AUTH-B  08 Security + 06 Effects + Infrastructure audit boundary：Mandatory Audit send gate
AUTH-C  Platform/Alembic：formal migration entrypoint stale import repair
```

允许修改与上述语义直接相关的 tests / fault probes / evidence docs。禁止顺带扩张 GraphRAG、Multi-Agent、Memory、Runtime topology、Provider marketplace 或微服务部署。

## Acceptance gate

三个 Slice 独立通过，不能用一个绿色 CI 替代另两个：

- P0-A：restart replay 保持 UNKNOWN；conclusive reconciliation 后才完成；duplicate dispatch 仍受抑制；
- P0-B：mandatory audit proof 缺失时 executor 0 次；matching proof 才允许 send；
- P0-C：正式 Alembic entrypoint 无 shim clean upgrade 到 head。

完成后再更新 `docs/evidence/current-test-baseline.md`、`effect-security-slice-c-review.md` 与 freeze readiness。只有新 Evidence 真正证明 Target violation 被关闭，06/08/04 的 Freeze blocker 才能从 `FAILS_TARGET / NOT_IMPLEMENTATION_PROVEN` 升级。

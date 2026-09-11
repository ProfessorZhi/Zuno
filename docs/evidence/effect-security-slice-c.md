# Effects ↔ Security Slice C Evidence

status: `CURRENT_REVIEW / TEST_ONLY_EXPLORATION_COMPLETE / IMPLEMENTATION_BLOCKED / NO_MODULE_FROZEN`  
module_detail_freeze: `NOT_YET`  
implementation_authorization: `NO`

这份记录收拢 06 Tool Runtime & Effects、08 Security & Governance 以及相邻 04 Runtime / 09 Audit persistence 在现实副作用 send boundary 上已经得到的 Current 证据。它不替代 Target Architecture，也不把诊断分支当成 main 的绿色 selected baseline。

Slice C 已经不再缺“再多跑几个单元测试”。当前证据已经足以区分三类事实：哪些保护机制确实在 Current 路径上工作，哪些路径已经被 GitHub PostgreSQL fault probe 证明违反 Target，以及哪些 Target 收敛能力还没有 Current implementation proof。继续在同一 Slice 上穷举小故障的边际收益已经低于转向其他责任域的收益。

## 已经成立的 Current 基础

Current 不是只有 `runtime_batch.py` 的对象模型。`ToolInvocationGateway` 处于当前产品调用路径，数据库执行使用 PostgreSQL-backed `ToolUnitOfWork`、`SecurityUnitOfWork` 和 `InfrastructureUnitOfWork`。现有 migration surface 包含 PreparedAction、Attempt、ExecutionReceipt、EffectReceipt、Reconciliation、Async Job、Cancellation、Compensation、Security epoch / approval / secret 和基础 infrastructure facts。

这些结构已经支持把“发送尝试”“本地观察”“现实 Effect 确定性”和“结果仍未知”分开保存。它们仍带有若干旧 decomposition 编号和 PHASE-era metadata；这些字符串属于 compatibility / nomenclature drift，不是当前 01–09 Target owner map 的新事实。

## 正向 fault evidence

### SecurityEpoch 在发送前撤销会阻止 Effect

PR #203 / run `34560042535` 在 PostgreSQL 16.15 上注入：prepare 与 Approval 成功以后、真正 send-before reauthorization 之前，把 matching effective epoch 从 `active` 改成 `revoked`。

结果：

- `194 passed, 1 warning in 10.68s`；
- artifact `10183996777`；
- 当前 `validate_pre_effect_authorization()` 返回 `stale security epoch before effect`；
- provider executor 调用 0 次；
- ToolAttempt=`FAILED / NOT_DISPATCHED`；
- ToolExecutionReceipt=`FAILED / NO_EFFECT`；
- 没有 EffectReceipt，也没有 Reconciliation。

因此 Current 可以证明：**早先合法的 Approval 不会永久授权未来发送；SecurityEpoch 在 send 前失效时，当前 Gateway 会重新检查并 fail closed。**

### Secret 在 lease 校验前撤销会阻止 Effect

PR #207 / run `34566365522` 把 fault window 推到更晚：Approval 和当前 SecurityEpoch reauthorization 都成功，只在 Gateway 即将 issue / validate 本次短期 Secret lease 前把 exact SecretRef 设为 `revoked`。

结果：

- `194 passed, 1 warning in 8.83s`；
- artifact `10186164476`；
- `validate_secret_lease()` 返回 `secret lease references a revoked secret`；
- provider executor 调用 0 次；
- ToolAttempt=`FAILED / NOT_DISPATCHED`；
- ToolExecutionReceipt=`FAILED / NOT_DISPATCHED / NO_EFFECT`；
- 没有 EffectReceipt、Reconciliation 或 committed SecretLease。

这个结果只证明 **pre-lease Secret revoke fail closed**。它没有证明 rotation 后选择新的 CredentialVersion、旧 Lease 传播失效、Retry 取得新 Lease或多 Provider / audience qualification。

### 远端已成功、本地 EffectReceipt 写失败时会退回 Unknown

PR #210 / run `34567699688` 注入另一个 send 后窗口：provider executor 已经返回成功，并给出稳定 provider effect identity；随后 test-only Tool UOW 只让 `record_effect_receipt()` 持久化失败，其他 Gateway / Security / Infrastructure / PostgreSQL 路径保持当前实现。

结果：

- `194 passed, 1 warning in 10.49s`；
- artifact `10186625101`；
- provider executor 只调用 1 次；
- Gateway 返回 `reconcile_required`，没有声称 completed；
- ToolAttempt=`UNKNOWN / DISPATCHED`；
- ToolExecutionReceipt=`UNKNOWN / DISPATCHED / UNKNOWN_EFFECT`；
- 没有 committed EffectReceipt；
- `OPEN / RECONCILE` 持久化成功，并保留 `provider-effect:mail:remote-success:1`。

因此可以采用一个严格限定的 Current 结论：**远端已经返回成功、但本地 EffectReceipt 不能耐久提交时，当前 Gateway 会把现实结果降回 Unknown 并留下 Reconciliation，而不是凭远端返回值宣布本地 confirmed completion。**

这仍不是“真实进程在纳秒级 crash”证明。它验证的是现有 exception / persistence-failure recovery 分支。

## 已经确认的 Target violation

### Restart replay 会把仍未解决的 Reconciliation 错误升级成 completed

PR #201 / run `34559517466` 首次执行时能够正确留下：

- ToolAttempt=`UNKNOWN / DISPATCHED`；
- ToolExecutionReceipt=`UNKNOWN / UNKNOWN_EFFECT`；
- Reconciliation=`OPEN / RECONCILE`；
- Runtime=`reconcile_required / UNKNOWN_EFFECT`。

销毁 Runtime、在同一 PostgreSQL 上重建并用同一 action identity replay 后，executor 没有再次调用，说明 durable idempotency 在该场景阻止了 duplicate dispatch；但上层 Runtime 把 replay 返回成 **`completed`**。

Source review 与行为一致：当前 replay 上行只携带一个未区分 EffectReceipt / Reconciliation / AsyncJob 的 `result_ref`，而 Runtime 对通用 `replayed` 采用 confirmed semantics。**“有耐久结果引用”不能推出“现实 Effect 已经确认发生”。** 这条路径违反 06 对 Outcome Unknown 的 Authority。

### Mandatory Audit requirement 没有闭合成 send gate

PR #205 / run `34560692093` 验证：Security 已经留下 matching audit requirement，但没有 committed mandatory-audit persistence fact 时，Current Gateway 仍然调用 provider executor、创建 EffectReceipt 并返回 completed。

观测包括：

- `security_audit_requirement_count = 1`；
- `durable_audit_receipt_count = 0`；
- executor 调用 1 次；
- ToolAttempt=`DISPATCHED / DISPATCHED`；
- EffectReceipt count=1。

Current Infrastructure 已经存在 `record_mandatory_audit()` / `assert_audit_durable_for_effect()` 原语，但当前 Tool send path 没有把 matching committed audit proof 作为越过现实副作用边界的必要条件。**Requirement 存在不能替代 AuditPersistenceReceipt。**

## 已经确认的 implementation gap

### Reconciliation 有 durable ledger，但没有证明最终收敛实现

Current 可以创建 `OPEN / RECONCILE`、按年龄把 `OPEN / WAITING_PROVIDER` escalate 到 `ESCALATED / MANUAL_ASSESSMENT`，也可以验证人工 reviewer 后写入 manual assessment。

Repo-wide source review 没有建立以下 Current proof：

- 消费持久化 `reconciliation_query` 的 remote-query consumer；
- 把 reconciliation 写成 `RESOLVED` 的 runtime / repository writer；
- conclusive `ReconciliationReceipt` implementation surface；
- manual assessment 更新 Reconciliation / EffectReceipt / ExecutionReceipt 为最终 Effect truth 的收敛路径。

因此这里的准确结论是 `NOT_IMPLEMENTATION_PROVEN`。保存 UNKNOWN、能够 escalation、能够写人工 assessment，都不能扩写成“Reconcile 已闭环”。

### Cancel-in-flight 只有持久化 primitive，没有 orchestration proof

Current `ToolInvocationGateway.record_cancellation_request()` 能为已经存在的 PreparedAction / Attempt（可选 AsyncJob）写 `ToolCancellationReceipt`，并把外部撤销明确记录为 `NOT_GUARANTEED / external_effect_revoked=False`；若 async job 仍 `WAITING_CALLBACK`，还会把它推进到 `CANCEL_REQUESTED`。

Repo-wide call-site review没有建立 production orchestration consumer：没有看到当前 Runtime / Worker 在真实取消路径上调用这项 primitive，也没有对应 Current behavior test 证明“用户取消 / deadline / plan cancel → provider cancel → callback race → final effect truth”的闭环。

因此 cancel-in-flight 同样从“再写一个表测试”降级为 `NOT_IMPLEMENTATION_PROVEN` 的 orchestration gap。已有 repository primitive 不能等价成可用的取消协议。

## 独立基础设施 blocker

所有需要 fresh PostgreSQL migration chain 的 Slice C 诊断都暴露并绕开了同一个独立问题：正式 `infra/db/alembic/env.py` 仍导入已退休的 `zuno.settings`，当前 settings 位于 `zuno.platform.settings`。

诊断只在测试进程临时 alias 旧 module path，从而让 migration bodies 执行到 head。这个 shim 不是生产修复，也不证明正式 Alembic deployment entrypoint 可用。

## Slice C 结论

```text
slice_c: TEST_ONLY_EXPLORATION_COMPLETE / IMPLEMENTATION_BLOCKED
freeze_ready_06_effects: NO
freeze_ready_08_security: NO
freeze_ready_04_runtime_from_effect_recovery: NO
security_epoch_pre_send_revocation: PASS @ run 34560042535
secret_pre_lease_revocation: PASS @ run 34566365522
remote_success_local_receipt_failure_to_unknown: PASS @ run 34567699688
unknown_effect_restart_replay: FAILS_TARGET @ run 34559517466
mandatory_audit_before_effect: FAILS_TARGET @ run 34560692093
reconciliation_convergence: NOT_IMPLEMENTATION_PROVEN
cancel_in_flight_orchestration: NOT_IMPLEMENTATION_PROVEN
formal_alembic_entrypoint: STALE_IMPORT_BLOCKER
module_detail_freeze: NOT_YET
implementation_authorization: NO
```

继续对 06/08 做 no-egress、Secret rotation 或更多边缘 fault injection 仍可能补充局部证据，但它们不会改变 Freeze 决策。当前已经存在两条 confirmed Target violation 与两个关键 orchestration/convergence implementation gap；下一单位工程投入更适合转向其他责任域的 Current Evidence，而不是继续在一个已明确 blocked 的 Slice 上增加测试数量。

任何 replay certainty 修复、Reconciliation resolver、Mandatory Audit wiring、cancel orchestration、正式 Alembic entrypoint、Security enforcement 或其他业务实现都仍需要独立明确的 Implementation Authorization。
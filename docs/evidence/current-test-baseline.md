# Current Test Baseline

状态：`CURRENT / SELECTED_VERIFICATION_AVAILABLE / EFFECT_RECOVERY_NEGATIVE_EVIDENCE / SECURITY_REVOCATION_POSITIVE_EVIDENCE / MANDATORY_AUDIT_NEGATIVE_EVIDENCE / QUALITY_NOT_ESTABLISHED`

## 当前代码快照的 Selected Verification

当前 GitHub-native **selected code verification** 已经覆盖基础代码行为、真实 PostgreSQL Domain probes，以及 Wave-001 Domain revision 的真实 PostgreSQL DDL 可逆性。它绑定具体代码 commit、lockfile 依赖、测试集合、PostgreSQL service container 和 GitHub Actions run，可以作为这些被覆盖行为的 Current Evidence；它仍然不是 Full CI、完整 PostgreSQL integration、正式 benchmark 或 Production Qualification。

```text
verified_code_snapshot: c817bd345c9025524c6380ef208a131277d164bd
workflow: Current code selected verification
workflow_run: 34499552197
event: push / main
runner: ubuntu-24.04
python: 3.12.14
dependency_source: poetry.lock
postgresql_service: PostgreSQL 16.15 / healthy
selected_suite: 193 passed
compileall: PASS
model_gateway_strict_boundary: PASS
postgresql_domain_selected_probes: PASS
wave001_revision_postgresql_upgrade_downgrade_reupgrade: PASS
full_ci: NOT_RUN / NOT_ESTABLISHED
benchmark: BLOCKED_NOT_MEASURED
quality: NOT_YET_PROVEN
production_readiness: NOT_ESTABLISHED
artifact_id: 10161286870
```

GitHub run `34499552197` checkout 的就是 `c817bd345c9025524c6380ef208a131277d164bd`。Selected pytest 在该 SHA 上得到 `193 passed in 8.94s`。Workflow 使用 PostgreSQL 16.15 service，并通过 `ZUNO_TEST_DATABASE_URL` 让 Domain SQLAlchemy tests 和 Wave-001 revision probe 进入真实 PostgreSQL 路径。

当前 PostgreSQL Domain 证明包括四类严格限定的 shape：

- **commit 后调用方丢失响应**：D0→D1 已提交；新的 service instance 使用同一规范化输入与 idempotency identity 重放，只返回既有 committed result，不产生 D2；
- **两个请求同时基于 D0**：并发进入同一 Matter，最多一个提交 D1，另一个读取新 head 后返回 `VERSION_CONFLICT`；
- **commit 前故障**：已有 `before_commit` fault hook 抛错，事务不推进；新的 service instance 随后仍从 D0→D1 提交；
- **Wave-001 revision 真实 DDL 可逆性**：在独立随机 PostgreSQL schema 中执行 revision `20260813_57` 的现有 Alembic `upgrade()`，验证三张 Wave-001 表与 `uq_domain_mutation_idempotency` / `uq_domain_state_version`；随后执行 `downgrade()` 验证 revision 表被移除，再次 `upgrade()` 后重新验证同一表与约束。

最后一项只证明 **revision `20260813_57` 自身的 PostgreSQL DDL 可以 apply / downgrade / re-apply**。它不证明真实业务数据 backfill、锁影响、零停机迁移或生产回滚。

这些结果支持当前 `SqlAlchemyCanonicalDomainStore` 的 PostgreSQL transaction、row-lock / expected-version、idempotent replay baseline，以及 Wave-001 revision-level DDL 可逆性。它们**不等于 Target Formal Admission 已实现**。当前 `src/backend/zuno/domain/` 仍只有 Wave-001 mutation / persistence surface；Target `AdmissionReceipt`、完整 WorkProduct admission transaction 以及 Runtime 读取 matching Receipt 修复 Checkpoint 尚没有 Current implementation evidence。

同一 main run 还完成：

- `python -m compileall -q src/backend/zuno tests`；
- strict Model Gateway provider-SDK bypass scan；
- Model Gateway boundary verification；
- Knowledge runtime batch：`ARCH-KNOW-001..030`；
- Capability runtime batch：`ARCH-CAP-001..080`；
- Tool runtime batch：`ARCH-TOOL-001..080`；
- Model Gateway runtime batch：`ARCH-MODEL-001..088`；
- Security runtime batch：`ARCH-SEC-001..060`；
- selected behavior suite across Domain mutation / Citation provenance / Product Application / Runtime / Knowledge / Capability / Tool / Security / Observability / Retrieval / Eval contracts。

具体文件集合由 [`.github/workflows/current-code-selected-verification.yml`](../../.github/workflows/current-code-selected-verification.yml) 固定。

## Slice C 负向证据：UNKNOWN Effect 重启重放被错误升级成 completed

为了验证 06 Tool Runtime & Effects 与 04 Agent Runtime 的 send-boundary 恢复，PR #201 建立了一个**未合并的诊断分支**。它不改变 `src/backend`、Migration、依赖或 Target Contract，只增加 PostgreSQL fault probe。因为 probe 揭示 Current implementation defect，这个 PR 不进入 main；失败本身作为负向 Evidence 保留。

诊断 run `34559517466` 使用 PostgreSQL 16.15，除新增 fault probe 外原 selected suite 仍通过，最终结果为：

```text
diagnostic_branch: ci/postgres-effect-security-boundary-probe
diagnostic_run: 34559517466
base_main: ebfb4637fa57e698c6ff83a3f53073ce3445fda6
selected_result: 193 passed, 1 failed, 1 warning
artifact_id: 10183819018
failure_scope: UNKNOWN Effect restart replay
business_fix_applied: NO
```

这个 probe 先走当前 `ToolControlPlaneRuntime → ToolInvocationGateway → ToolUnitOfWork / SecurityUnitOfWork / InfrastructureUnitOfWork`，让一个需要 Approval 的外部写动作越过 send boundary 后抛出 `ToolEffectUnknownError`。第一次执行的 Current 行为是正确的：

- executor 只调用一次；
- `ToolAttempt` 耐久记录为 `UNKNOWN / DISPATCHED`；
- `ToolExecutionReceipt` 耐久记录为 `UNKNOWN / UNKNOWN_EFFECT`；
- `tool_effect_reconciliations` 留下 `OPEN / RECONCILE`，并保存 provider effect identity；
- Runtime 返回 `reconcile_required / UNKNOWN_EFFECT`。

随后销毁 Runtime 对象、用同一 PostgreSQL 数据库新建 Runtime，并用同一 action / idempotency identity 重放。Current 实现没有再次调用 executor，说明 durable idempotency 能阻止重复外部发送；但返回状态变成了 **`completed`**。测试在 `replay.status == "reconcile_required"` 处失败。

这说明当前恢复链存在一个明确语义缺陷：**未完成 Reconciliation 的外部 Effect 在重启后的幂等 replay 中被上层 Runtime 错误提升为完成。** Source review 与失败行为一致：当前 side-effect replay 只向上返回一个未携带类型/确定性的 `result_ref`，这个 ref 可能指向已确认 EffectReceipt，也可能指向仍然 OPEN 的 Reconciliation；上层 Runtime 对通用 `replayed` 状态采用完成语义。Target 要求 Outcome Unknown 在 06 完成 Reconcile 前继续保持 Unknown，因此这条路径阻塞 06/04 的 Freeze。

这里同时保留一个重要正向边界：**诊断中没有发生 duplicate dispatch。** 当前问题是 Effect certainty / lifecycle 被错误升级，不是这次测试观察到的二次外部发送。

## Slice C 正向证据：SecurityEpoch 在 send 前撤销会 fail closed

PR #203 用另一条**未合并的 test-only 诊断分支**验证 08 Security 的时间边界。它不修改 Security 或 Tool 业务实现，只在两个现有 UnitOfWork 边界之间注入一次耐久事实变化：Security prepare / Approval 完成时 epoch 仍是 `active`；Infrastructure idempotency / fencing transaction 提交后，test seam 将同一个 `security_effective_epochs` row 改为 `revoked`；随后继续执行 Gateway 现有的 `_reauthorize_execute_epoch() → validate_pre_effect_authorization()`。

GitHub run `34560042535` 的结果为：

```text
diagnostic_branch: ci/postgres-security-revocation-probe
diagnostic_run: 34560042535
base_main: 4f485cd4e018ce085e7e551953e9791e4ac53d82
selected_result: 194 passed, 1 warning
artifact_id: 10183996777
fault_window: active at prepare/approval -> revoked before send
business_fix_applied: NO
```

这个 fault window 的 Current 行为满足 Target：

- test seam 确认目标 epoch 从 `active` 变成 `revoked`；
- Gateway 的真实 pre-effect authorization 返回 `stale security epoch before effect`；
- provider executor **0 次调用**；
- `ToolAttempt` 耐久记录为 `FAILED / NOT_DISPATCHED`；
- `ToolExecutionReceipt` 耐久记录为 `FAILED / NO_EFFECT`；
- 没有生成 `ToolEffectReceipt`；
- 没有生成 `tool_effect_reconciliations`。

因此可以采用一个非常窄但重要的 Current 结论：**授权在 prepare / Approval 时成立，不会自动授权未来的外部发送；当 effective SecurityEpoch 在 send 前变成 revoked，当前 Gateway 会在真实 provider dispatch 前重新检查并 fail closed。**

这条证据不代表 08 已冻结。它只关闭 `revocation-before-send` 这一种 fault window；Approval action-hash drift、Secret rotation、Mandatory Audit、Policy Engine outage、no-egress、Legal Hold / No-Recall / purge convergence、Prompt Injection 等仍需自己的证明。它也不会抵消上面已经确认的 06/04 Effect replay defect。

## Slice C 负向证据：Mandatory Audit requirement 没有形成 send gate

PR #205 把 Target `MANDATORY_BEFORE_EFFECT` 放进当前 PostgreSQL Tool/Security/Infrastructure 路径。Source review 已确认两个基础能力分别存在：08 的 Security persistence 会创建 `security_audit_requirements`，平台 Infrastructure 也实现了 `record_mandatory_audit()` 与 `assert_audit_durable_for_effect()`；后者在没有耐久 mandatory-audit fact 时本来能够 fail closed。但仓库调用链中没有证据表明当前 `ToolInvocationGateway` 在 provider dispatch 前调用了这些 Audit durability helper。

诊断 run `34560692093` 将这条 wiring suspicion 变成了可复核的 Current 结果：

```text
diagnostic_branch: ci/postgres-mandatory-audit-boundary-probe
diagnostic_run: 34560692093
base_main: d459b1875d8488cb63b14a84ded11f80a48c4053
selected_result: 193 passed, 1 failed, 1 warning
artifact_id: 10184212936
failure_scope: MANDATORY_BEFORE_EFFECT durability gate
business_fix_applied: NO
```

新增 probe 在一个已批准、SecretRef 有效的 `mail.send` 外部写动作上**刻意不创建** `infra_mandatory_audit_events`。失败字典同时确认：

- `security_audit_requirement_count = 1`：08 的 audit requirement 确实存在；
- `durable_audit_receipt_count = 0`：对应现实 Effect 没有耐久 mandatory-audit proof；
- `executor_calls = 1`：provider dispatch 仍然发生；
- Gateway 返回 `completed`，result 非空；
- `ToolAttempt = DISPATCHED / DISPATCHED`；
- `effect_receipt_count = 1`：现实 Effect 被写成已发生。

这证明当前 send path 把“Security 要求审计”与“审计已经耐久提交”留成了两条没有闭合的事实链。Target 中 08 拥有安全/治理要求，09/平台负责可复核的 Audit persistence，06 在越过现实副作用 send boundary 前必须消费 matching committed Audit proof。**Requirement 存在不能代替 AuditPersistenceReceipt。** 当前实现没有建立这个执行门，因此 `MANDATORY_BEFORE_EFFECT` 不满足 Target，06 与 08 都不能据此 Freeze；09 的耐久审计能力也不能仅凭 helper 存在被宣称已接入 Effect path。

这里的失败与 #201 不同：#201 是“Effect 已经 Unknown 后，恢复时错误升级 certainty”；#205 是“Effect 发送之前，本应存在的耐久审计前置事实没有被 Gate 消费”。两者分别位于 send boundary 的两侧，都属于 Slice C 的硬 blocker。

## Alembic Current entrypoint 漂移

PR #201 的第一次 run `34559357122` 还暴露出一个独立 Current 基础设施问题：`infra/db/alembic/env.py` 仍导入已经退休的 `zuno.settings`，而当前 settings module 位于 `zuno.platform.settings`。因此标准 `alembic upgrade head` 在进入 migration chain 前就因 `ModuleNotFoundError` 失败。

PR #201 的第二次诊断、PR #203 和 PR #205 都只在**测试进程内部**临时将 `zuno.settings` alias 到 `zuno.platform.settings`，没有修改正式 Alembic 文件。借助这个 test-only shim，fresh PostgreSQL database 能顺序执行当前 migration chain；但这只能说明 migration bodies 在该 fresh-database 场景下可以继续运行，**不能写成正式 Alembic entrypoint 已通过**。部署入口仍有 stale import blocker，需要独立实现/维护授权处理。

## PostgreSQL 证据的边界

GitHub service container 不等于系统级 PostgreSQL qualification。Actions 日志仍能看到部分其他 selected tests / import-time platform components 尝试默认 `postgres` 用户并被数据库拒绝；这些路径没有被 Domain probes 声称为成功。Current 可采用的正向结论是 **显式 Domain PostgreSQL probes、Wave-001 revision probe、以及 #203 的 pre-effect revocation probe**；Current 负向结论包括 #201 的 Effect recovery defect 与 #205 的 Mandatory Audit gate defect。不能概括为“Zuno 全部 PostgreSQL 集成通过”。

当前仍未证明或已经明确阻塞的内容包括：

- 正式 Alembic entrypoint 无兼容 shim 的 clean upgrade；
- 真实业务数据的 backfill、约束收紧和在线迁移策略；
- Target AdmissionReceipt 与 Domain mutation 同事务提交；
- Domain commit 后 Runtime Checkpoint 丢失时的 owner-first E2E recovery；
- Checkpoint 已标完成但 matching Receipt 缺失时的 formal-complete denial；
- unresolved external Effect 在 restart replay 后保持 Unknown——#201 已证明这条路径**不满足 Target**；
- `MANDATORY_BEFORE_EFFECT` 在没有 committed audit proof 时阻止现实发送——#205 已证明这条路径**不满足 Target**；
- SecurityEpoch **pre-send revocation** 已由 #203 通过；其他 Approval hash drift、Secret rotation、Policy drift 与 no-egress fault window 仍未证明；
- Redis、RabbitMQ、Object Store、真实 Model / Tool Provider、外部 Host、HA / DR、负载和生产运维。

## 两类 GitHub Gate 与诊断分支

当前仓库保留两类可合入主线的 GitHub gate：

- `Architecture document set`：验证 Project / Architecture / Modules / Governance / Evidence 文档集合、语义一致性、Human Readability、entrypoints 和对应 repository tests；
- `Current code selected verification`：验证 lockfile 可安装性、代码边界、runtime-batch contracts、selected behavior tests、当前 Domain PostgreSQL probes，以及 Wave-001 revision-level DDL probe。

诊断 PR 不自动成为第三类 main gate。它们把 Target failure matrix 送进 Current 代码，并生成正负 evidence：PR #201 / run `34559517466` 证明 UNKNOWN Effect restart path 需要实现修复；PR #203 / run `34560042535` 证明 pre-send SecurityEpoch revocation fail closed；PR #205 / run `34560692093` 证明 Mandatory Audit requirement 在没有 durable audit proof 时仍允许 provider dispatch。三者都使用 test-only Alembic compatibility alias，因此不会替代 main 的正向 baseline，也不会被描述成 clean deployment qualification。

两类 main gate 组合后仍不等于 Full Project CI。Formal benchmark 继续 `BLOCKED_NOT_MEASURED`，法院 QA、capacity、SLA、HA / DR 与 Production Readiness 仍未建立。

## 历史 selected verification

历史记录继续保留，但不覆盖当前代码：

```text
historical_verified_head: 1ea56a5d61afa27ebda8f8745a6dbc6584796d05
final_selected_suite: 90 passed
full_ci: NOT_RUN / NO_GITHUB_STATUS
benchmark: BLOCKED_NOT_MEASURED
production_readiness: NOT_ESTABLISHED
```

`4736cf4409658e43af6e129e34dadbd97a5866ad` 的 run `34497460461` 恢复了 GitHub-native selected gate：`189 passed, 1 skipped`。`5b51627e43b6abcd940ac63100048171fd7f460c` 的 run `34498613045` 把真实 PostgreSQL Domain transaction / concurrency probes 接入后得到 `192 passed`。当前 main 正向判断优先使用上面的 `c817bd3...` / run `34499552197`；Slice C 的诊断 runs 只用于各自明确的正负结论。

## 后续 Evidence Gate

**Slice B — Domain ↔ Runtime crash authority** 在“不修改业务实现”的验证范围已经走到边界：当前 mutation transaction / concurrency / lost-response replay 与 Wave-001 revision-level PostgreSQL DDL 已有 GitHub evidence。剩余 Owner-first recovery 依赖 Target `AdmissionReceipt`、Formal Admission transaction 和 Runtime matching-Receipt consumer；这些当前没有实现证明。

**Slice C — Effects ↔ Security send boundary** 仍是 `BLOCKED_BY_IMPLEMENTATION_DEFECT`，且现在有两条互相独立的硬 blocker：#201 证明 restart replay 会把 unresolved Reconciliation 错误升级成 completed；#205 证明没有 durable mandatory-audit proof 时 provider 仍会 dispatch。#203 则证明 pre-send SecurityEpoch revocation 这一条当前会 fail closed。下一步若继续 test-only，应优先验证 Approval action-hash drift、Secret rotation / revocation 或 no-egress；这些结果可以继续缩小 08/06 uncertainty，但不会绕过已经确认的两个 Slice C implementation blocker。

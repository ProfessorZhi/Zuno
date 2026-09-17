# Current Test Baseline

状态：`CURRENT / SELECTED_VERIFICATION_AVAILABLE / PSC_A_COMPOSITION_VERIFIED / PSC_B_SECURITY_OWNER_FACT_VERIFIED / PSC_C_BUDGET_DEFERRED_BY_SCOPE / PSC_D_APPROVAL_PROJECTION_VERIFIED / EFFECT_REPLAY_FIX_VERIFIED / DURABLE_RECONCILIATION_JUDGMENT_VERIFIED / MANDATORY_AUDIT_REQUIREMENT_BINDING_VERIFIED / SECURITY_EFFECT_IDENTITY_VERIFIED / SECURITY_REVOCATION_POSITIVE_EVIDENCE / SECRET_REVOCATION_POSITIVE_EVIDENCE / QUALITY_NOT_ESTABLISHED`

## 当前代码快照的 Selected Verification

RB019 的 Effect/Audit 修复与 Product Security Composition PSC-A–D 的当前决策都已经进入 `main`。PSC-A/B 是实现并验证的 owner/composition path，PSC-C 是有证据约束的 Defer，PSC-D 是 authority-writer cleanup。当前 GitHub-native selected verification 直接绑定 `main@293fa144f70be0467d1363eb3662d1b39a874cf8`：

```text
verified_code_snapshot: 293fa144f70be0467d1363eb3662d1b39a874cf8
workflow: Current code selected verification
workflow_run: 35202465804
event: push / main
runner: ubuntu-24.04
python: 3.12.14
dependency_source: poetry.lock
postgresql_service: PostgreSQL 16.15 / healthy
selected_suite: 214 passed, 22 warnings in 39.74s
compileall: PASS
model_gateway_strict_boundary: PASS
runtime_batch_contracts: PASS
formal_alembic_entrypoint_fresh_postgres: PASS
workspace_product_composition_root: PSC-A PASS
postgresql_agent_run_store_recovery: PSC-A PASS
product_security_owner_fact_issue_resolve: PSC-B PASS
product_security_foreign_scope_expiry_tamper: PSC-B FAIL-CLOSED VERIFIED
product_security_replay_does_not_refresh_expiry: PSC-B PASS
product_security_agent_admission_reaches_budget_blocker: PSC-B PASS
caller_budget_limits_do_not_self_approve: PSC-C PASS / BUDGET OWNER UNBOUND
formal_budget_owner_service: PSC-C DEFERRED_BY_SCOPE
product_approval_projection_only: PSC-D PASS
product_approval_projection_authority_tables_untouched: PSC-D PASS
product_approval_projection_tenant_scope_and_conflict: PSC-D PASS
unknown_effect_restart_replay_preserves_unknown: PASS
conclusive_reconciliation_paths: PASS
mandatory_audit_before_effect: PASS
mandatory_audit_requirement_binding: PASS
security_effect_epoch_identity_not_trace_only: PASS
full_ci: NOT_RUN / NOT_ESTABLISHED
benchmark: BLOCKED_NOT_MEASURED
quality: NOT_YET_PROVEN
production_readiness: NOT_ESTABLISHED
artifact_id: 10488681251
artifact_sha256: bce09b936c349eba13b0b57327d27a3abfdab42544159356d9b5a3f1ac20b7f9
```

这条 run 证明的范围仍然是 selected suite，不是 Full CI 或 Production Qualification。PSC-A 证明正式 FastAPI startup 可以建立 `WorkspaceRuntimeComposition` 并使用 PostgreSQL-backed `AgentRunStore`；PSC-B 证明 08 Security owner path 可以发行并解析 Product SecurityDecision，显式持久化 workspace scope、issued/expiry 与 immutable hash，foreign scope / expiry / durable-content tamper 均 fail closed，同一 Product submission replay不刷新授权寿命。

PSC-B 的 issuance 只有在 deployment 显式配置正的 `server.security.product_decision_ttl_seconds` 时才绑定，仓库 example 默认保持 `null`。这仍是部署策略边界，不是测试里 300 秒 TTL 对产品默认值的宣称。现实副作用发送前依旧由既有 08/06 pre-effect gate 检查 current Security 条件。

PSC-C 没有新建 Budget store/service。Current Product API 里的 `budget_limits` 是 caller-declared Runtime limits；删除了没有 owner store 的伪 `PostgresBudgetDecisionResolver` 后，通用 Budget owner port 仍保留但 production resolver继续不绑定。真实 runtime probe 即使携带 `max_steps / max_tokens / timeout_seconds / cost_ceiling`，Security 通过后仍停在 `budget_owner_resolver_unbound`，没有 `BudgetDecisionRef`，也没有模型调用。因此 PSC-C 的 Current 状态是 `DEFERRED_BY_SCOPE`，不是“Budget owner admission 已实现”。

PSC-D 已解决旧 approval sink 的 Owner 冲突。`PostgresSecurityApprovalEventSink` 只写 `security_outbox_events` 作为 durable approval lifecycle projection；不再写 SecurityEpoch、PrincipalContext、AuthorizationDecision、Approval 或 AuditRequirement authority rows。projection 使用真实 request tenant；exact replay 幂等，same idempotency identity + changed content 明确 conflict。新 probe 在 fresh PostgreSQL 上同时验证 1 条 projection event 与 6 类 authority table 全部 0。

PSC-D 也没有创建新的 Product Approval flow。`approval_flow="none"` 仍是当前 Product composition 边界；formal Budget owner admission同样保持 Defer/fail-closed。仍未证明 provider remote-query adapter、authoritative reviewer role binding、完整 audit class / DB-level tenant isolation、pre-send-abort / crash-replay audit lifecycle、Target composed SecurityEpoch、真实 Provider E2E、Full CI 或 Production Readiness。

### RB019 前历史 selected baseline

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

## History — Slice C 负向证据：UNKNOWN Effect 重启重放被错误升级成 completed

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

这里同时保留一个重要正向边界：**诊断中没有发生 duplicate dispatch。** 当时的问题是 Effect certainty / lifecycle 被错误升级，不是这次测试观察到的二次外部发送。

**Current closure：** AUTH-A commit `18e4973365461ec939b95063c74f4a0457507e75` 把 replay result_ref 重新解释为 typed Effect / Reconciliation / Async state，并增加最小 conclusive reconciliation writer。当前 `main@ff0f497e3eea862fa44b0a8d5979e9ad31ac5ad0` 的 run `35056938670` 包含 restart PostgreSQL probe：OPEN reconciliation 在重启 replay 后继续返回 `reconcile_required / UNKNOWN_EFFECT`，executor 不会第二次 dispatch；conclusive executed 后才完成，confirmed-not-executed 也不会暗中重发。#201 因而保留为修复前 History，而不再描述今天 main 的失败。

## History → Current：Reconciliation 从缺失 resolver 收敛到最小 conclusive path

#201 证明 OPEN Reconciliation 可以被耐久保存，但“保存未知”只是 Reconcile 的起点。06 Target 要求能够通过远端 query / business key / idempotency status 或必要人工确认形成 `ReconciliationReceipt`，结论至少区分 `CONFIRMED_EXECUTED / CONFIRMED_NOT_EXECUTED / STILL_UNKNOWN / MANUAL_REQUIRED`，并据此修复 Effect state。

对 Current 源码的 repo-wide review 显示：

- `ToolInvocationGateway` 可以创建 `OPEN / RECONCILE` row；
- `escalate_due_reconciliations()` 只能把过期的 `OPEN / WAITING_PROVIDER` 推到 `ESCALATED / MANUAL_ASSESSMENT`；
- `record_manual_effect_assessment()` 可以要求授权人工 reviewer 并持久化人工结论；
- schema 允许 `RESOLVED`，但没有发现 Current runtime/repository writer 把 reconciliation 更新成 `RESOLVED`；
- 没有发现消费已保存 `reconciliation_query` 去调用远端查询接口的 Current consumer；
- 没有发现 Current `ReconciliationReceipt` implementation surface 或“人工 assessment → repaired Effect truth”的收敛路径。

搜索 `ReconciliationReceipt` 的 Current repo 命中集中在 Target / Architecture / Governance 文档；`WAITING_PROVIDER` 的实现命中集中在 schema 和 escalation 条件；`reconciliation_query` 的实现命中集中在创建/哈希保存，不形成查询执行链。

这段 source review 是 AUTH-A 之前的实现事实。Current 已经存在 `resolve_effect_reconciliation()` 和 conclusive manual-assessment → EffectReceipt / ExecutionReceipt / `RESOLVED` convergence；后续 PostgreSQL probes 还证明 manual judgment 必须匹配 durable reconciliation 的 provider effect identity，同一 reconciliation 在当前 one-shot schema 下 exact replay 幂等、不同第二 judgment fail closed。仍未证明的是 provider-facing remote-query consumer，以及 reviewer role / tenant / approval policy 的 authoritative binding；这些剩余边界不能被 durable judgment 的存在自动升级。

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

这条证据不代表 08 已冻结。它只关闭 `revocation-before-send` 这一种 fault window；完整 Secret rotation/retry、Mandatory Audit、Policy Engine outage、no-egress、Legal Hold / No-Recall / purge convergence、Prompt Injection 等仍需自己的证明。它也不会抵消上面已经确认的 06/04 Effect replay defect。

## Slice C 正向证据：Secret 在 lease 校验前撤销会 fail closed

PR #207 使用另一条**未合并的 test-only PostgreSQL 诊断分支**验证 Credential 自身的时间边界。这个场景与 #203 不同：SecurityEpoch、Approval 和 send 前 re-authorization 都保持有效；fault seam 只在 Gateway 即将发放并校验本次外部 Effect 的短期 Secret Lease 之前，把同一个 `security_secret_refs` row 从 `active` 改成 `revoked`，随后继续执行现有 `_issue_secret_lease() → validate_secret_lease()`。

GitHub run `34566365522` 的结果为：

```text
diagnostic_branch: ci/postgres-secret-revocation-boundary-probe
diagnostic_run: 34566365522
base_main: 5239689071099d4090bbdeee049b8822e1724782
selected_result: 194 passed, 1 warning in 8.83s
artifact_id: 10186164476
fault_window: approval + epoch reauth pass -> SecretRef revoked before lease validation -> send
business_fix_applied: NO
```

这个 fault window 的 Current 行为满足 Target 的 fail-closed 方向：

- exact SecretRef 确实从 `active` 变成 `revoked`；
- 当前 `validate_secret_lease()` 返回 `secret lease references a revoked secret`；
- provider executor **0 次调用**；
- `ToolAttempt` 耐久记录为 `FAILED / NOT_DISPATCHED`；
- `ToolExecutionReceipt` 耐久记录为 `FAILED / NOT_DISPATCHED / NO_EFFECT`；
- 没有生成 EffectReceipt；
- 没有生成 Reconciliation；
- Secret lease 的 issue + validate 位于同一 Security UOW，校验失败后事务回滚，因此没有留下 committed SecretLease。

因此可以采用另一条严格限定的 Current 结论：**即使 Approval 和当前 SecurityEpoch 都仍有效，只要绑定的 Secret 在现实发送前已经 revoked，当前 Gateway 也不会把早先的授权或 Credential 引用继续当成可发送资格。**

这不等于完整 Secret rotation / retry 已证明。当前 probe 没有验证 rotation 后如何选择新的 CredentialVersion、已有旧 Lease 的过期传播、Retry 是否取得新 Lease，也没有验证多 Provider / 多 audience 的 Credential qualification。它只关闭“pre-lease Secret revoke 是否会继续发送”这个 fault window。

## History — Slice C 负向证据：Mandatory Audit requirement 没有形成 send gate

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

这里的失败与 #201 不同：#201 位于 Effect 已经 Unknown 之后；#205 位于 Effect 发送之前。它们共同解释了 RB019 为什么把 certainty replay 与 audit-before-effect 分成两个独立 slice。

**Current closure：** AUTH-B commit `2f709ec9344b94bdc87289793d22bcac3ba2a10b` 已把 committed mandatory-audit proof 接到 provider send boundary，并在 audit commit 后重新检查当前 SecurityEpoch；`main@ff0f497e3eea862fa44b0a8d5979e9ad31ac5ad0` 保留 provider dispatch 后 `effect_observed` lifecycle，并进一步把 proof 绑定到 persisted Security AuditRequirement。run `35056938670` 的 PostgreSQL selected suite 证明：缺 proof 时 executor 为 0；matching proof 才能发送；audit 后撤销 SecurityEpoch 仍会阻止发送；相同 audit identity 不能绑定不同 action hash；capacity=1 的 channel 可以连续服务两个不同已发送 Effect。#205 继续保留为修复前负向 History。

## History — Alembic entrypoint 漂移

PR #201 的第一次 run `34559357122` 还暴露出一个独立 Current 基础设施问题：`infra/db/alembic/env.py` 仍导入已经退休的 `zuno.settings`，而当前 settings module 位于 `zuno.platform.settings`。因此标准 `alembic upgrade head` 在进入 migration chain 前就因 `ModuleNotFoundError` 失败。

PR #201 的第二次诊断、PR #203、PR #205 和 PR #207 当时都只在测试进程内部临时 alias 旧 module path，因此这些诊断本身仍不能证明正式部署入口。AUTH-C commit `7cd177a96200f57183ba117968ac4433cb6ebbff` 随后把正式 import 切到 `zuno.platform.settings`，并增加 fresh PostgreSQL `alembic upgrade head` probe；该 probe 已进入当前 `main@ff0f497e` 的绿色 selected run `35056938670`。stale-import blocker 已关闭，但这仍不等于真实业务数据 backfill、零停机 migration 或生产 rollback 已验证。

## PostgreSQL 证据的边界

GitHub service container 不等于系统级 PostgreSQL qualification。Actions 日志仍能看到部分其他 selected tests / import-time platform components 尝试默认 `postgres` 用户并被数据库拒绝；这些路径没有被 Domain probes 声称为成功。Current 可采用的正向结论包括显式 Domain PostgreSQL probes、Wave-001 revision probe、#203 的 pre-effect SecurityEpoch revocation、#207 的 pre-lease Secret revocation，以及 RB019 后进入 main selected suite 的 Effect replay certainty、最小 conclusive reconciliation、mandatory-audit send gate / post-dispatch capacity lifecycle 和 formal Alembic entrypoint。#201 与 #205 保留为修复前负向 History，不再描述今天 main 的失败。不能概括为“Zuno 全部 PostgreSQL 集成通过”。

当前仍未证明或仍需继续收敛的内容包括：

- 真实业务数据的 backfill、约束收紧和在线迁移策略；
- Target AdmissionReceipt 与 Domain mutation 同事务提交；
- Domain commit 后 Runtime Checkpoint 丢失时的 owner-first E2E recovery；
- Checkpoint 已标完成但 matching Receipt 缺失时的 formal-complete denial；
- provider-facing remote query / business-key reconciliation integration；
- manual reconciliation 的 authoritative reviewer role / tenant / approval-policy binding，以及 one-shot judgment 是否足够真实人工工作流；
- AuditRequirement 的 `BEST_EFFORT / DURABLE / MANDATORY_BEFORE_EFFECT` class 是否由 08 耐久表达并被 06 消费；
- mandatory audit proof 已提交、但 send 前再次被 Security 阻断时怎样释放 capacity 而不伪造 `effect_observed`；send 后 crash / restart 怎样修复遗漏的 audit lifecycle close；
- `infra_mandatory_audit_events` 的数据库级 tenant isolation，以及 proof 已绑定 tenant context 后的 cross-tenant fault probe；
- Target composed EffectiveSecurityEpoch 的 workspace / principal / resource scope persistence；Current 只证明 Tool Effect action-scoped identity 不再依赖 trace；
- production `WorkspaceRuntimeComposition` / SecurityDecisionResolver binding；当前 repo-wide source review 尚未建立正式启动装配证据；
- SecurityEpoch **pre-send revocation** 已由 #203 通过；SecretRef **pre-lease revocation** 已由 #207 通过；完整 Secret rotation/retry、Policy drift、no-egress 与其他治理 fault window 仍未证明；
- Redis、RabbitMQ、Object Store、真实 Model / Tool Provider、外部 Host、HA / DR、负载和生产运维。

## 两类 GitHub Gate 与诊断分支

当前仓库保留两类可合入主线的 GitHub gate：

- `Architecture document set`：验证 Project / Architecture / Modules / Governance / Evidence 文档集合、语义一致性、Human Readability、entrypoints 和对应 repository tests；
- `Current code selected verification`：验证 lockfile 可安装性、代码边界、runtime-batch contracts、selected behavior tests、当前 Domain PostgreSQL probes，以及 Wave-001 revision-level DDL probe。

诊断 PR 不自动成为第三类 main gate。它们把 Target failure matrix 送进 Current 代码，并生成正负 evidence：PR #201 / run `34559517466` 证明 UNKNOWN Effect restart path 需要实现修复；PR #203 / run `34560042535` 证明 pre-send SecurityEpoch revocation fail closed；PR #205 / run `34560692093` 证明 Mandatory Audit requirement 在没有 durable audit proof 时仍允许 provider dispatch；PR #207 / run `34566365522` 证明 pre-lease Secret revoke fail closed。四者都使用 test-only Alembic compatibility alias，因此不会替代 main 的正向 baseline，也不会被描述成 clean deployment qualification。

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

`4736cf4409658e43af6e129e34dadbd97a5866ad` 的 run `34497460461` 恢复了 GitHub-native selected gate：`189 passed, 1 skipped`。`5b51627e43b6abcd940ac63100048171fd7f460c` 的 run `34498613045` 把真实 PostgreSQL Domain transaction / concurrency probes 接入后得到 `192 passed`。这些历史 baseline 继续保留；当前 main 正向判断优先使用本文顶部的 `ff0f497e...` / run `35056938670`。Slice C 的旧诊断 runs 只用于解释各自当时的正负结论和后续修复动机。

## 后续 Evidence Gate

**Slice B — Domain ↔ Runtime crash authority** 在“不修改业务实现”的验证范围已经走到边界：当前 mutation transaction / concurrency / lost-response replay 与 Wave-001 revision-level PostgreSQL DDL 已有 GitHub evidence。剩余 Owner-first recovery 依赖 Target `AdmissionReceipt`、Formal Admission transaction 和 Runtime matching-Receipt consumer；这些当前没有实现证明。

**Slice C — Effects ↔ Security send boundary** 的原始 RB019 P0 violation 已关闭：restart replay certainty、最小 conclusive reconciliation、mandatory-audit send gate 和 formal Alembic entrypoint 都已有 main selected evidence，post-dispatch audit capacity lifecycle 也已转绿。Slice C 仍不是完整 Freeze / Production proof；下一层缺口集中在 provider remote-query reconciliation、manual reviewer Authority、audit-class / DB-level tenant isolation、pre-send-abort / crash-replay audit lifecycle、Target composed SecurityEpoch、production Workspace Security composition，以及 cancel-in-flight orchestration。继续 fault test 应针对这些仍有 Current surface 的具体边界，而不是重复已经转绿的 #201/#205 failure shape。
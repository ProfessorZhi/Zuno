# Module Detail Freeze Readiness Review

status: `REVIEW_COMPLETE / SLICE_A_VERIFIED / SLICE_B_PARTIAL_VERIFICATION_LIMIT / SLICE_C_BLOCKED_BY_IMPLEMENTATION_DEFECT / NO_MODULE_FROZEN`  
review_snapshot: `eca4a7ebcadbc1c964f174e3b2ce620f9ecbdf5e`  
selected_verification_snapshot: `c817bd345c9025524c6380ef208a131277d164bd`  
module_detail_freeze: `NOT_YET`  
implementation_authorization: `NO`

本文记录九个 Target 责任域进入 **Module Detail Freeze Review** 之前的 readiness 审查。它属于 Governance review，不拥有 Target Architecture，也不自动升级 Current Evidence。模块语义继续以 [`docs/modules/`](../modules/README.md) 及各模块 `reference.md` 为准；实现事实继续以 [`docs/evidence/`](../evidence/README.md) 为准。

这次审查只回答一个问题：**当前 Detail Design Candidate 是否已经拥有足够的实现、故障、迁移和跨 Owner 证据，可以进入冻结判断？**

结论仍然是：**0/9 模块满足进入冻结的证据条件，9/9 继续保持 `detail design candidate available`。** 九篇 Reference 已经把字段、Guard、Crash Window、Migration 和 Failure Injection 写到可审查粒度；Current fault probes 开始把其中一部分约束送进真实 PostgreSQL 和恢复路径。测试结果既有正向 baseline，也出现了能够阻止 Freeze 的负向证据。

## Slice A：current-head selected verification 已建立

GitHub-native `Current code selected verification` 已经成为稳定基础回归面：从 `poetry.lock` 建立 Python 3.12 环境，运行 compile、Model Gateway strict boundary、Knowledge / Capability / Tool / Model Gateway / Security runtime-batch verifier，以及跨 Domain、Citation、Application、Runtime、Retrieval、Observability 与 Eval 的 selected behavior tests。

## Slice B：纯验证能证明的 Domain baseline 已完成，跨 Owner recovery 停在 Implementation Gap

main `c817bd345c9025524c6380ef208a131277d164bd` 的 push run `34499552197` 在 PostgreSQL 16.15 service 上完成 `193 passed`。当前可以证明的范围包括 Wave-001 Domain mutation/version 的三个运行形状，以及 revision `20260813_57` 自身的真实 PostgreSQL DDL 可逆性：

1. **commit 后调用方丢失响应**：D0→D1 已提交；新的 service instance 使用同一规范化输入和 idempotency identity 重放，只返回既有 committed result，不产生 D2；
2. **两个请求同时基于 D0**：真实 PostgreSQL 并发下最多一个提交 D1，另一个在读取新 aggregate head 后返回 `VERSION_CONFLICT`；
3. **commit 前故障**：已有 `before_commit` fault hook 抛错后事务不推进，新 service instance 后续仍从 D0→D1 提交；
4. **Wave-001 revision apply / downgrade / re-apply**：在独立随机 schema 中执行现有 Alembic revision 的 `upgrade()`，验证三张表与两个关键 unique constraints；`downgrade()` 后 revision 表消失；再次 `upgrade()` 后结构重新成立。

第四项只证明 revision `20260813_57` 自身的 DDL 可逆，不证明真实业务数据 backfill、锁影响或零停机策略。

Source review 同时确认：当前 `src/backend/zuno/domain/` 只有 Wave-001 `mutation.py` / `persistence.py` surface，没有 Target `AdmissionReceipt` implementation。Architecture / ADR 要求 Formal Admission 的 Domain mutation 与 matching Receipt 在同一耐久边界提交，并由 04 在 Domain commit / Checkpoint mismatch 时查询 Receipt；当前代码还不能提供这条 proof。

因此 Slice B 保持 `PARTIAL`，并已经到达 **verification-only limit**。继续增加 mutation/revision test 不会关闭真正的 Owner-first recovery gap。要进一步证明 `Domain commit → matching AdmissionReceipt → Runtime repair`，必须先有对应 Current implementation；这属于业务实现，当前 `implementation_authorization: NO` 下不执行。

## Slice C：durable Effect truth 已存在，但 restart replay 破坏 Outcome Unknown

Source review 确认 Current 不只有 `runtime_batch.py` 的 dataclass。当前执行路径存在真实 `ToolInvocationGateway`，并由 `zuno.capability.runtime` 等调用点使用；有 PostgreSQL-backed `ToolUnitOfWork`、`SecurityUnitOfWork`、`InfrastructureUnitOfWork`，Migration 也包含 PreparedAction、Attempt、ExecutionReceipt、EffectReceipt、Reconciliation、Async / Cancellation / Compensation 等耐久表面。

Security 侧也已经有 send 前的再授权实现。`validate_pre_effect_authorization()` 会检查 prepared-action hash、SecurityEpoch 是否仍 active、DENY、Approval 状态与 deadline。因此“执行前重新消费当前安全事实”已经具备可测试 Current surface，不能再笼统写成只有 Target 设计。

真正的 blocker 出现在 06↔04 的恢复消费语义。PR #201 使用 test-only PostgreSQL fault probe，把当前完整调用链跑到外部 send boundary：

1. 一个 `WRITE_EXTERNAL + APPROVAL_REQUIRED` 动作在批准后执行；
2. executor 越过 send boundary 后抛 `ToolEffectUnknownError`；
3. Current Gateway 正确耐久化 `ToolAttempt=UNKNOWN/DISPATCHED`、`ToolExecutionReceipt=UNKNOWN/UNKNOWN_EFFECT`、`Reconciliation=OPEN/RECONCILE`；
4. Runtime 第一次正确返回 `reconcile_required / UNKNOWN_EFFECT`；
5. 销毁 Runtime 后在同一 PostgreSQL 上重建实例，用同一 action/idempotency identity replay；
6. executor 没有被再次调用，说明该场景没有观察到 duplicate dispatch；
7. 但 replay 返回 **`completed`**，测试在“仍应为 `reconcile_required`”处失败。

GitHub diagnostic run `34559517466` 的结果是 `193 passed, 1 failed, 1 warning`，artifact `10183819018`。失败只来自这个新增 Effect recovery invariant；它不进入 main 的绿色 selected baseline，却是可采用的负向 Current Evidence。

Source review解释了这一故障的形状：当前 idempotency replay 向上返回一个没有携带 receipt type / effect certainty 的 `result_ref`。这个 ref 可以指向已确认的 EffectReceipt，也可以指向仍 OPEN 的 Reconciliation；上层 Runtime 对通用 `replayed` 状态采用完成语义。于是“已经有耐久结果引用”被误当成“现实 Effect 已确认完成”。Target 06 要求 `Outcome Unknown` 在 Reconcile 前继续保持 Unknown，这条 Current 路径不满足该 Authority。

这次诊断同时证明了一部分值得保留的基础：PreparedAction / Attempt / ExecutionReceipt / Reconciliation 的 durable path 能工作，UNKNOWN 能被写入 PostgreSQL，restart replay 能命中 idempotency 并阻止该测试中的二次 dispatch。Freeze blocker 已经从“是否存在 durable Effect ledger”收敛成**恢复时如何解释耐久结果类型与 certainty**。

## 另一个 Current blocker：正式 Alembic entrypoint 的 stale import

PR #201 第一次 run `34559357122` 在行为测试前就暴露出 `infra/db/alembic/env.py` 仍导入已退休 `zuno.settings`。当前 settings 位于 `zuno.platform.settings`，所以标准 Alembic entrypoint 直接 `ModuleNotFoundError`。

第二次 run 没有修改 `env.py`，只在测试进程临时 alias 旧 module path，然后 fresh PostgreSQL database 从 `20260417_01` 顺序升级到 `20260813_57`。这说明 migration bodies 在该 fresh-database / compatibility-shim 场景下能够执行到 head，但**正式 entrypoint 仍然是 Current blocker**。不能把 test-only alias 写成部署修复。

## 九个责任域的 readiness 结论

| 模块 | 当前可引用基础 | Freeze 前仍缺的关键证明 | Verdict |
| --- | --- | --- | --- |
| **01 Application & Integration** | selected GitHub suite 已覆盖 Product Application boundary | Simple QA Host E2E、重复请求/响应丢失、正式 Publication、Domain invalidation + offline consumer、Delivery outcome unknown、Host version compatibility | `NOT_READY` |
| **02 Legal Domain & Work Product** | Wave-001 + PostgreSQL selected probes 已证明 mutation CAS、真实 D0 concurrency、commit 前 rollback、幂等 replay、Citation provenance、revision-level DDL apply/downgrade/re-apply | **Target AdmissionReceipt implementation**、Domain commit / Runtime Checkpoint crash E2E、receipt-absent denial、SecurityEpoch admission drift、正式 WorkProduct invalidation | `NOT_READY` |
| **03 Knowledge & Evidence** | selected suite 已覆盖 Knowledge runtime-batch 与 retrieval composition 基础 | `KnowledgeGeneration → validated manifest → ServingPointer → task ReadinessDecision` Current 闭环、activation crash、security revocation、provider rebuild、representative corpus、GraphRAG query-class 对照 | `NOT_READY` |
| **04 Agent Runtime & Control** | selected suite 已覆盖 plan、interrupt、restart、replan、tool idempotency、model roles 与 P0 recovery；Slice C 证明 restart replay 能阻止 duplicate dispatch | matching AdmissionReceipt consumer / repair；**unresolved Effect replay 当前被错误升级成 completed**；完整 late branch/Replan Barrier、fencing/takeover、SecurityEpoch drift、paused checkpoint/schema upgrade、Native Runtime necessity measurement | `NOT_READY` |
| **05 Capability & Skill** | selected suite 已覆盖 Capability runtime-batch contract | CapabilityVersion / ProviderBinding 的真实生命周期、task-class Qualification / Eligibility 质量证据、semantic drift、non-equivalent fallback、Research-to-Capability E2E | `NOT_READY` |
| **06 Tool Runtime & Effects** | Current execution path 已有 PostgreSQL-backed PreparedAction / Attempt / ExecutionReceipt / EffectReceipt / Reconciliation surface；UNKNOWN 首次写入与 restart idempotency 已由 diagnostic probe 到达 | **OPEN Reconciliation replay 被错误提升成 completed**；真实 remote query/manual reconcile、send 后 remote success/local crash、cancel-in-flight、compensation、Approval/Secret/Audit drift；runtime-batch 旧 taxonomy metadata 仍需 compatibility 决策 | `NOT_READY` |
| **07 Model Gateway** | strict provider-SDK / boundary gate、runtime-batch、model-role 与 cost/latency selected tests 已通过 | Role qualification、真实 Provider outage/fallback equivalence、Usage settlement、cancel race、egress/credential qualification、production credential、行为漂移回归 | `NOT_READY` |
| **08 Security & Governance** | selected suite 覆盖有限 fail-closed/approval contract；Current persistence 已实现 prepared-action hash、active epoch、Approval deadline 的 pre-effect validation | revocation-during-run E2E、no-egress、Approval action-hash invalidation、Secret rotation、Mandatory Audit failure、Policy Engine outage、Legal Hold / No-Recall / purge convergence、Prompt Injection gate | `NOT_READY` |
| **09 Observability & Evaluation** | selected suite 已覆盖 observability runtime contract 与部分 Eval contract | 正式 DatasetVersion、真实 task-class cases、Judge calibration、A/B/C baseline、critical failure release gate、cost/latency/recovery measurements、court telemetry policy；formal benchmark 仍 `MEASUREMENT_BLOCKED` | `NOT_READY` |

## Current compatibility drift 仍需单独处理

当前 `src/backend/zuno/capability/tool_runtime/runtime_batch.py` 已经具有 `PreparedToolAction`、`ToolAttemptRecord`、`EffectReceipt`、`ReconciliationRecord`、SecurityEpoch ref 和 audit gate 等表面，但若干 metadata 仍使用上一代 decomposition 的 owner 编号，例如 `08 Tool Runtime`、`07 Capability / Skill`、`06 Agent Core / Planning & Control`、`04 Model Gateway`；现有 tests 还主动断言这些旧字符串。Security runtime-batch 中也可看到类似旧编号。

这些旧字符串不能被当成当前 01–09 Target owner map 的证明。当前 Target 对应责任分别由 06 Effects、05 Capability、04 Runtime、07 Model Gateway、08 Security、09 Evaluation 等承担。这个问题目前更像 compatibility / nomenclature drift，没有证据表明它就是 #201 的 Effect certainty 缺陷；两者分开处理。因为修正 implementation-facing metadata 会修改 `src/backend`，本 review 不在 `implementation_authorization: NO` 下直接改。

## 后续 Evidence Slice

### Slice A — Current-head verification foundation — `VERIFIED`

GitHub-native selected gate 已建立，后续 code/test/dependency/migration 变化由它重新触发。

### Slice B — Domain ↔ Runtime crash authority — `PARTIAL / VERIFICATION-ONLY LIMIT REACHED`

**已证明：** Wave-001 Domain mutation 的真实 PostgreSQL transaction / D0 concurrency / pre-commit rollback / lost-response replay，以及 revision `20260813_57` 的 PostgreSQL apply/downgrade/re-apply。  
**实施阻塞：** Target AdmissionReceipt + Formal Admission + Runtime owner-first repair / receipt-absent denial。

### Slice C — Effects ↔ Security send boundary — `BLOCKED_BY_IMPLEMENTATION_DEFECT`

**已证明：** Current durable Effect surface 存在；第一次 send 后 Unknown 能落 PostgreSQL；OPEN Reconciliation 能跨 Runtime instance 保留；同一 action replay 在该诊断中没有再次 dispatch；Security pre-effect validation 具有 Current implementation surface。  
**已失败：** unresolved Reconciliation 在 restart replay 时被 Runtime 返回为 `completed`，不满足 Outcome Unknown authority。  
**独立基础设施 blocker：** 正式 Alembic entrypoint 仍引用退休的 `zuno.settings`；完整 fresh-database chain 只在 test-only import alias 下执行到 head。  
**还能纯验证：** 08 的 revocation-during-run / stale epoch fail-closed 可以继续做独立 fault probe；它不会消除已经确认的 06/04 blocker。  
**实施阻塞：** 修复 replay result typing/certainty、Runtime consumption semantics 或正式 Alembic entrypoint 均需独立 Implementation Authorization。

### Slice D — Knowledge generation / readiness

用真实多版本材料走 `DocumentVersion → generation build → manifest validation → serving activation → task Readiness → retrieval`，注入 partial write、activation crash、late Worker、新 DocumentVersion、Readiness 后撤权和 provider rebuild。GraphRAG 只在同 query class 的 baseline 对照里决定是否保留。

### Slice E — Capability ↔ Model Gateway qualification

选一个已有专业能力作为样本，让两个 Provider 返回相同 schema，但在 semantic contract、质量、region、budget 或 failure behavior 上不同。验证 Conformance、Qualification / Eligibility、non-equivalent fallback、ProviderVersion drift、model Usage 与 paused/late result provenance。

### Slice F — Application lifecycle E2E

用一个外部 Host 走 accepted → draft/runtime complete → formal WorkProduct → publication → delivery → new-evidence invalidation → consumer offline / reconnect。Application 只组合 Owner facts；Domain、Effects、Security 仍保持自己的 Authority。

### Slice G — Evaluation baseline

在至少一条业务 slice 稳定运行后建立冻结 dataset/config/baseline。GraphRAG、Reflection、Specialist 与 Native Runtime 都用 ablation / kill test 决定保留范围。

## Review verdict

```text
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
freeze_ready_modules: 0/9
selected_code_snapshot: c817bd345c9025524c6380ef208a131277d164bd
selected_github_run: 34499552197 / 193 passed
postgresql_domain_selected_probes: PASS
wave001_revision_postgresql_upgrade_downgrade_reupgrade: PASS
slice_b: PARTIAL / VERIFICATION_ONLY_LIMIT_REACHED
admission_receipt_current_implementation: NOT_ESTABLISHED
slice_c: BLOCKED_BY_IMPLEMENTATION_DEFECT
effect_unknown_restart_replay: FAILS_TARGET_INVARIANT @ diagnostic run 34559517466
formal_alembic_entrypoint: STALE_IMPORT_BLOCKER
formal_benchmark: MEASUREMENT_BLOCKED
production_readiness: NOT_ESTABLISHED
```

下一步可以继续做 08 的 test-only revocation-during-run probe，因为 Current pre-effect authorization 已有实现表面；但它只是继续缩小 Slice C 的 Security uncertainty，不会把 06/04 的已确认 replay defect 变成可冻结。任何业务 Runtime、Effect certainty、Alembic entrypoint、Security enforcement、数据库结构或其他 Target implementation 修改，仍需要独立明确的 Implementation Authorization。

# Module Detail Freeze Readiness Review

status: `REVIEW_COMPLETE / SLICE_A_VERIFIED / SLICE_B_PARTIAL_VERIFICATION_LIMIT / NO_MODULE_FROZEN`  
review_snapshot: `eca4a7ebcadbc1c964f174e3b2ce620f9ecbdf5e`  
selected_verification_snapshot: `c817bd345c9025524c6380ef208a131277d164bd`  
module_detail_freeze: `NOT_YET`  
implementation_authorization: `NO`

本文记录九个 Target 责任域进入 **Module Detail Freeze Review** 之前的 readiness 审查。它属于 Governance review，不拥有 Target Architecture，也不自动升级 Current Evidence。模块语义继续以 [`docs/modules/`](../modules/README.md) 及各模块 `reference.md` 为准；实现事实继续以 [`docs/evidence/`](../evidence/README.md) 为准。

这次审查只回答一个问题：**当前 Detail Design Candidate 是否已经拥有足够的实现、故障、迁移和跨 Owner 证据，可以进入冻结判断？**

结论仍然是：**0/9 模块满足进入冻结的证据条件，9/9 继续保持 `detail design candidate available`。** 九篇 Reference 已经把字段、Guard、Crash Window、Migration 和 Failure Injection 写到可审查粒度；当前阻塞主要在这些约束是否已经被 Current 代码和可复现验证证明。

## Slice A：current-head selected verification 已建立

GitHub-native `Current code selected verification` 已经成为稳定基础回归面：从 `poetry.lock` 建立 Python 3.12 环境，运行 compile、Model Gateway strict boundary、Knowledge / Capability / Tool / Model Gateway / Security runtime-batch verifier，以及跨 Domain、Citation、Application、Runtime、Retrieval、Observability 与 Eval 的 selected behavior tests。

## Slice B：纯验证能证明的 Domain baseline 已完成，跨 Owner recovery 停在 Implementation Gap

main `c817bd345c9025524c6380ef208a131277d164bd` 的 push run `34499552197` 在 PostgreSQL 16.15 service 上完成 `193 passed`。当前可以证明的范围包括 Wave-001 Domain mutation/version 的三个运行形状，以及 revision `20260813_57` 自身的真实 PostgreSQL DDL 可逆性：

1. **commit 后调用方丢失响应**：D0→D1 已提交；新的 service instance 使用同一规范化输入和 idempotency identity 重放，只返回既有 committed result，不产生 D2；
2. **两个请求同时基于 D0**：真实 PostgreSQL 并发下最多一个提交 D1，另一个在读取新 aggregate head 后返回 `VERSION_CONFLICT`；
3. **commit 前故障**：已有 `before_commit` fault hook 抛错后事务不推进，新 service instance 后续仍从 D0→D1 提交；
4. **Wave-001 revision apply / downgrade / re-apply**：在独立随机 schema 中执行现有 Alembic revision 的 `upgrade()`，验证三张表与两个关键 unique constraints；`downgrade()` 后 revision 表消失；再次 `upgrade()` 后结构重新成立。

第四项只证明 revision `20260813_57` 自身的 DDL 可逆，不证明从历史根 revision 到 head 的完整 migration chain、真实业务数据 backfill、锁影响或零停机策略。

Source review 同时确认：当前 `src/backend/zuno/domain/` 只有 Wave-001 `mutation.py` / `persistence.py` surface，没有 Target `AdmissionReceipt` implementation。Architecture / ADR 要求 Formal Admission 的 Domain mutation 与 matching Receipt 在同一耐久边界提交，并由 04 在 Domain commit / Checkpoint mismatch 时查询 Receipt；当前代码还不能提供这条 proof。

因此 Slice B 保持 `PARTIAL`，但已经到达 **verification-only limit**。继续增加 mutation/revision test 不会关闭真正的 Owner-first recovery gap。要进一步证明 `Domain commit → matching AdmissionReceipt → Runtime repair`，必须先有对应 Current implementation；这属于业务实现，当前 `implementation_authorization: NO` 下不执行。

## 九个责任域的 readiness 结论

| 模块 | 当前可引用基础 | Freeze 前仍缺的关键证明 | Verdict |
| --- | --- | --- | --- |
| **01 Application & Integration** | selected GitHub suite 已覆盖 Product Application boundary | Simple QA Host E2E、重复请求/响应丢失、正式 Publication、Domain invalidation + offline consumer、Delivery outcome unknown、Host version compatibility | `NOT_READY` |
| **02 Legal Domain & Work Product** | Wave-001 + PostgreSQL selected probes 已证明 mutation CAS、真实 D0 concurrency、commit 前 rollback、幂等 replay、Citation provenance、revision-level DDL apply/downgrade/re-apply | **Target AdmissionReceipt implementation**、Domain commit / Runtime Checkpoint crash E2E、receipt-absent denial、SecurityEpoch admission drift、正式 WorkProduct invalidation；完整 historical migration chain 仅在真实需要时再验证 | `NOT_READY` |
| **03 Knowledge & Evidence** | selected suite 已覆盖 Knowledge runtime-batch 与 retrieval composition 基础 | `KnowledgeGeneration → validated manifest → ServingPointer → task ReadinessDecision` Current 闭环、activation crash、security revocation、provider rebuild、representative corpus、GraphRAG query-class 对照 | `NOT_READY` |
| **04 Agent Runtime & Control** | selected suite 已覆盖 plan、interrupt、restart、replan、tool idempotency、model roles 与 P0 recovery 基础 | matching AdmissionReceipt consumer / repair、checkpoint-complete / receipt-absent denial、完整 late branch/Replan Barrier、fencing/takeover、SecurityEpoch drift、paused checkpoint/schema upgrade、Native Runtime necessity measurement | `NOT_READY` |
| **05 Capability & Skill** | selected suite 已覆盖 Capability runtime-batch contract | CapabilityVersion / ProviderBinding 的真实生命周期、task-class Qualification / Eligibility 质量证据、semantic drift、non-equivalent fallback、Research-to-Capability E2E | `NOT_READY` |
| **06 Tool Runtime & Effects** | selected suite 已覆盖 Tool runtime-batch 与 Outcome Unknown / reconcile 基础语义 | current Tool runtime-batch 仍含旧 decomposition owner metadata；另缺 durable PreparedAction / Attempt / Effect ledger、send-boundary crash、remote success/local crash、真实 remote idempotency/query、manual reconcile、Approval/Secret/Audit drift、compensation | `NOT_READY` |
| **07 Model Gateway** | strict provider-SDK / boundary gate、runtime-batch、model-role 与 cost/latency selected tests 已通过 | Role qualification、真实 Provider outage/fallback equivalence、Usage settlement、cancel race、egress/credential qualification、production credential、行为漂移回归 | `NOT_READY` |
| **08 Security & Governance** | selected suite 已覆盖有限 fail-closed、approval/security runtime contract | revocation-during-run E2E、no-egress、Approval action-hash invalidation、Secret rotation、Mandatory Audit failure、Policy Engine outage、Legal Hold / No-Recall / purge convergence、Prompt Injection gate | `NOT_READY` |
| **09 Observability & Evaluation** | selected suite 已覆盖 observability runtime contract 与部分 Eval contract | 正式 DatasetVersion、真实 task-class cases、Judge calibration、A/B/C baseline、critical failure release gate、cost/latency/recovery measurements、court telemetry policy；formal benchmark 仍 `MEASUREMENT_BLOCKED` | `NOT_READY` |

## Slice C 开始前先处理一个 Current compatibility blocker

当前 `src/backend/zuno/capability/tool_runtime/runtime_batch.py` 已经具有 `PreparedToolAction`、`ToolAttemptRecord`、`EffectReceipt`、`ReconciliationRecord`、SecurityEpoch ref 和 audit gate 等可用于 test-only fault review 的表面。但其中若干 metadata 仍使用上一代 decomposition 的 owner 编号，例如 `08 Tool Runtime`、`07 Capability / Skill`、`06 Agent Core / Planning & Control`、`04 Model Gateway`；现有 `tests/capability/test_tool_runtime_batch.py` 还主动断言这些旧字符串。

这说明两个事实需要分开：

- Outcome Unknown、Reconcile、audit-before-dispatch、cancel certainty 等行为可以继续作为 Current capability surface 测试；
- runtime-batch metadata 不能直接被当作当前 01–09 Target owner map 的证明。当前 Target 中对应责任分别是 06 Effects、05 Capability、04 Runtime、07 Model Gateway。

这个命名漂移目前没有证据表明改变了实际 Tool dispatch / Effect truth，但它会污染 Freeze Evidence 的解释。如果后续要把这些 runtime-batch objects 升级成 Current Target-aligned contract evidence，应单独处理 compatibility / nomenclature migration；因为文件位于 `src/backend`，本 review 不在 `implementation_authorization: NO` 下直接修改它。

## 后续 Evidence Slice

### Slice A — Current-head verification foundation — `VERIFIED`

GitHub-native selected gate 已建立，后续 code/test/dependency/migration 变化由它重新触发。

### Slice B — Domain ↔ Runtime crash authority — `PARTIAL / VERIFICATION-ONLY LIMIT REACHED`

**已证明：** Wave-001 Domain mutation 的真实 PostgreSQL transaction / D0 concurrency / pre-commit rollback / lost-response replay，以及 revision `20260813_57` 的 PostgreSQL apply/downgrade/re-apply。  
**实施阻塞：** Target AdmissionReceipt + Formal Admission + Runtime owner-first repair / receipt-absent denial。  
**剩余 migration 深挖：** 完整 historical chain、业务数据 backfill、在线迁移只有在真实实施需求出现时再验证，不为了 Freeze checklist 机械扩展。

### Slice C — Effects ↔ Security send boundary — `SOURCE REVIEW IN PROGRESS`

先对现有 06/08 Current surface 做 bounded source review。若现有对象已经能表达相同 action identity、Outcome Unknown、Reconcile、Approval/Audit/SecurityEpoch freshness，就只增加 fault tests；若 durable Effect truth 或 current-security enforcement 只存在于 Target/reference，不通过测试伪造实现。

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
slice_c: SOURCE_REVIEW_IN_PROGRESS
formal_benchmark: MEASUREMENT_BLOCKED
production_readiness: NOT_ESTABLISHED
```

下一步进入 Slice C 的 source/test review；任何新增 AdmissionReceipt、Formal Admission transaction、Runtime consumer、Effect ledger、Security enforcement、业务数据库结构或其他 Target implementation，都仍需要独立明确的 Implementation Authorization。

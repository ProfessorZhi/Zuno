# Module Detail Freeze Readiness Review

status: `REVIEW_COMPLETE / SLICE_A_VERIFIED / SLICE_B_PARTIAL / NO_MODULE_FROZEN`  
review_snapshot: `eca4a7ebcadbc1c964f174e3b2ce620f9ecbdf5e`  
selected_verification_snapshot: `5b51627e43b6abcd940ac63100048171fd7f460c`  
module_detail_freeze: `NOT_YET`  
implementation_authorization: `NO`

本文记录九个 Target 责任域进入 **Module Detail Freeze Review** 之前的 readiness 审查。它属于 Governance review，不拥有 Target Architecture，也不自动升级 Current Evidence。模块语义继续以 [`docs/modules/`](../modules/README.md) 及各模块 `reference.md` 为准；实现事实继续以 [`docs/evidence/`](../evidence/README.md) 为准。

这次审查只回答一个问题：**当前 Detail Design Candidate 是否已经拥有足够的实现、故障、迁移和跨 Owner 证据，可以进入冻结判断？**

结论仍然是：**0/9 模块满足进入冻结的证据条件，9/9 继续保持 `detail design candidate available`。** 九篇 Reference 已经把字段、Guard、Crash Window、Migration 和 Failure Injection 写到可审查粒度；当前阻塞主要在这些约束是否已经被 Current 代码和可复现验证证明。

## Slice A：current-head selected verification 已建立

初次 review 时，`current-test-baseline.md` 仍把旧 `1ea56a5...` 的 90-pass 记录误写成 Final HEAD Verification。本轮先把旧结果降回历史证据，再建立 GitHub-native `Current code selected verification`。

当前 selected gate 已经成为稳定基础回归面：从 `poetry.lock` 建立 Python 3.12 环境，运行 compile、Model Gateway strict boundary、Knowledge / Capability / Tool / Model Gateway / Security runtime-batch verifier，以及跨 Domain、Citation、Application、Runtime、Retrieval、Observability 与 Eval 的 selected behavior tests。

## Slice B：Domain ↔ Runtime crash authority 已获得 PostgreSQL baseline，但仍被 AdmissionReceipt 阻断

main `5b51627e43b6abcd940ac63100048171fd7f460c` 的 push run `34498613045` 在 PostgreSQL 16.15 service 上完成 `192 passed`，没有数据库 skip。当前可以证明的范围是 Wave-001 Domain mutation/version surface 的三类行为：

1. **commit 后调用方丢失响应**：D0→D1 已提交；新的 service instance 使用同一规范化输入和 idempotency identity 重放，只返回既有 committed result，不产生 D2；
2. **两个请求同时基于 D0**：真实 PostgreSQL 并发下最多一个提交 D1，另一个在读取新 aggregate head 后返回 `VERSION_CONFLICT`；
3. **commit 前故障**：已有 `before_commit` fault hook 抛错后事务不推进，新 service instance 后续仍从 D0→D1 提交。

这三条证据支持 `SqlAlchemyCanonicalDomainStore` 当前 row-lock / expected-version / idempotent replay baseline。它们没有证明 Target Formal Admission 已经落地。

Source review 同时确认：当前 `src/backend/zuno/domain/` 只有 `mutation.py`、`persistence.py` 与导出文件，没有 Target `AdmissionReceipt` implementation surface。Architecture / ADR 要求 Formal Admission 的 Domain mutation 与 matching Receipt 在同一耐久边界提交，并由 04 在 Domain commit / Checkpoint mismatch 时查询 Receipt；当前代码还不能提供这条 proof。因此 Slice B 状态是 `PARTIAL`，不能通过增加更多 mutation unit test 把它包装成 closed。

## 九个责任域的 readiness 结论

| 模块 | 当前可引用基础 | Freeze 前仍缺的关键证明 | Verdict |
| --- | --- | --- | --- |
| **01 Application & Integration** | selected GitHub suite 已覆盖 Product Application boundary | Simple QA Host E2E、重复请求/响应丢失、正式 Publication、Domain invalidation + offline consumer、Delivery outcome unknown、Host version compatibility | `NOT_READY` |
| **02 Legal Domain & Work Product** | Wave-001 + PostgreSQL selected probes 已证明 mutation CAS、真实 D0 concurrency、commit 前 rollback、幂等 replay、Citation provenance | **Target AdmissionReceipt implementation**、Domain commit / Runtime Checkpoint crash E2E、receipt-absent denial、SecurityEpoch admission drift、真实 Alembic apply/rollback、正式 WorkProduct invalidation | `NOT_READY` |
| **03 Knowledge & Evidence** | selected suite 已覆盖 Knowledge runtime-batch 与 retrieval composition 基础 | `KnowledgeGeneration → validated manifest → ServingPointer → task ReadinessDecision` Current 闭环、activation crash、security revocation、provider rebuild、representative corpus、GraphRAG query-class 对照 | `NOT_READY` |
| **04 Agent Runtime & Control** | selected suite 已覆盖 plan、interrupt、restart、replan、tool idempotency、model roles 与 P0 recovery 基础 | matching AdmissionReceipt consumer / repair、checkpoint-complete / receipt-absent denial、完整 late branch/Replan Barrier、fencing/takeover、SecurityEpoch drift、paused checkpoint/schema upgrade、Native Runtime necessity measurement | `NOT_READY` |
| **05 Capability & Skill** | selected suite 已覆盖 Capability runtime-batch contract | CapabilityVersion / ProviderBinding 的真实生命周期、task-class Qualification / Eligibility 质量证据、semantic drift、non-equivalent fallback、Research-to-Capability E2E | `NOT_READY` |
| **06 Tool Runtime & Effects** | selected suite 已覆盖 Tool runtime-batch 与 Outcome Unknown / reconcile 基础语义 | durable PreparedAction / Attempt / Effect ledger、send-boundary crash、remote success/local crash、真实 remote idempotency/query、manual reconcile、Approval/Secret/Audit drift、compensation | `NOT_READY` |
| **07 Model Gateway** | strict provider-SDK / boundary gate、runtime-batch、model-role 与 cost/latency selected tests 已通过 | Role qualification、真实 Provider outage/fallback equivalence、Usage settlement、cancel race、egress/credential qualification、production credential、行为漂移回归 | `NOT_READY` |
| **08 Security & Governance** | selected suite 已覆盖有限 fail-closed、approval/security runtime contract | revocation-during-run E2E、no-egress、Approval action-hash invalidation、Secret rotation、Mandatory Audit failure、Policy Engine outage、Legal Hold / No-Recall / purge convergence、Prompt Injection gate | `NOT_READY` |
| **09 Observability & Evaluation** | selected suite 已覆盖 observability runtime contract 与部分 Eval contract | 正式 DatasetVersion、真实 task-class cases、Judge calibration、A/B/C baseline、critical failure release gate、cost/latency/recovery measurements、court telemetry policy；formal benchmark 仍 `MEASUREMENT_BLOCKED` | `NOT_READY` |

## 为什么 PostgreSQL 通过仍然不能冻结 02 或 04

Freeze 需要的是 Target 约束能够约束后续实现，而不是“当前数据库代码有一些正确行为”。02 的 B14.8 明确要求 matching `AdmissionReceipt`、Domain commit 后 Checkpoint repair、receipt 缺失时拒绝 formal-complete、新 Evidence / SecurityEpoch / citation binding 等跨边界场景。04 也明确把 matching Receipt 当 Formal Admission-required Step 的完成证明。

当前 mutation record 可以证明一次 Wave-001 mutation 的幂等与版本结果，却没有足够语义证明 `run / PlanVersion / StepRun / proposal / admission identity → resulting DomainVersion` 这一条 Target causation。把 mutation record 重命名成 Receipt，或者在测试里用 `result_ref` 代替 Receipt，只会掩盖 Implementation Gap。

因此 02/04 的下一步已经从“多写测试”转成一个明确的授权边界：若要继续关闭 owner-first recovery，必须实现 Target AdmissionReceipt / Formal Admission transaction 与 Runtime consumer。这属于业务实现，当前 `implementation_authorization: NO` 下不执行。

## 还能继续做而不越过实现授权的 Slice B 工作

在等待实施授权前，仍有一项纯验证工作值得做：**Wave-001 Alembic migration 的真实 PostgreSQL apply / downgrade / re-apply probe**。当前 migration 明确提供 `upgrade()` / `downgrade()`，但 Existing Evidence 只有源码 contract test，没有真实 PostgreSQL apply/rollback 证据。

这项测试只运行现有 Migration，不改变业务 schema 设计，也不新增表。它可以进一步缩小 02 的 Freeze Gap；即使通过，也不会解决 AdmissionReceipt 和 02↔04 recovery。

## 后续 Evidence Slice

### Slice A — Current-head verification foundation — `VERIFIED`

GitHub-native selected gate 已建立，后续 code/test/dependency/migration 变化由它重新触发。

### Slice B — Domain ↔ Runtime crash authority — `PARTIAL`

**已证明：** Wave-001 Domain mutation 的真实 PostgreSQL transaction / D0 concurrency / pre-commit rollback / lost-response replay baseline。  
**仍可纯验证：** Wave-001 Migration apply / downgrade / re-apply。  
**实施阻塞：** Target AdmissionReceipt + Formal Admission + Runtime owner-first repair / receipt-absent denial。

### Slice C — Effects ↔ Security send boundary

固定 PreparedAction/action hash，验证 send 前授权/Approval/Audit/Secret、新旧 SecurityEpoch，send 后 timeout、remote success/local crash、remote query unavailable、manual reconciliation 和 cancel-in-flight。

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
selected_code_snapshot: 5b51627e43b6abcd940ac63100048171fd7f460c
selected_github_run: 34498613045 / 192 passed
postgresql_domain_selected_probes: PASS
slice_b: PARTIAL
admission_receipt_current_implementation: NOT_ESTABLISHED
formal_benchmark: MEASUREMENT_BLOCKED
production_readiness: NOT_ESTABLISHED
```

下一步可以继续做 Migration 的 test-only PostgreSQL probe；任何新增 AdmissionReceipt、Formal Admission transaction、Runtime consumer、业务数据库结构或其他 Target implementation，都仍需要独立明确的 Implementation Authorization。

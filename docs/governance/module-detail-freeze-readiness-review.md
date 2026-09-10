# Module Detail Freeze Readiness Review

status: `REVIEW_COMPLETE / SLICE_A_VERIFIED / NO_MODULE_FROZEN`  
review_snapshot: `eca4a7ebcadbc1c964f174e3b2ce620f9ecbdf5e`  
verification_follow_up: `4736cf4409658e43af6e129e34dadbd97a5866ad`  
module_detail_freeze: `NOT_YET`  
implementation_authorization: `NO`

本文记录九个 Target 责任域进入 **Module Detail Freeze Review** 之前的 readiness 审查。它属于 Governance review，不拥有 Target Architecture，也不自动升级 Current Evidence。模块语义继续以 [`docs/modules/`](../modules/README.md) 及各模块 `reference.md` 为准；实现事实继续以 [`docs/evidence/`](../evidence/README.md) 为准。

这次审查只回答一个问题：**当前 Detail Design Candidate 是否已经拥有足够的实现、故障、迁移和跨 Owner 证据，可以进入冻结判断？**

结论仍然是：**0/9 模块满足进入冻结的证据条件，9/9 继续保持 `detail design candidate available`。** 这不是设计失败。九篇 Reference 已经把字段、Guard、Crash Window、Migration 和 Failure Injection 写到可审查粒度；当前缺口主要在这些约束是否已经被 Current 代码和可复现验证证明。

## Slice A 已补上 current-head selected verification

初次 review 时，`current-test-baseline.md` 仍把旧 `1ea56a5...` 的 90-pass 记录误写成 Final HEAD Verification，而当前主线已经发生大量变化。本轮先把旧结果降回历史证据，再建立 GitHub-native `Current code selected verification`。

main `4736cf4409658e43af6e129e34dadbd97a5866ad` 的 push run `34497460461` 已在 GitHub runner 上成功完成 lockfile 安装、compile、Model Gateway strict boundary、五类 runtime-batch verifier 和 selected behavior suite；pytest 结果是 `189 passed, 1 skipped, 1 warning`。精确 Current Evidence 见 [`current-test-baseline.md`](../evidence/current-test-baseline.md)。

这完成了 **Slice A — Current-head verification foundation**，但没有使任何模块自动获得 Freeze 资格。唯一已知 skip 是未配置 `ZUNO_TEST_DATABASE_URL` 的 PostgreSQL integration test；Full CI、真实外部依赖、正式 benchmark 和 Production Readiness 仍未建立。

## 九个责任域的 readiness 结论

| 模块 | 当前可引用基础 | Freeze 前仍缺的关键证明 | Readiness verdict |
| --- | --- | --- | --- |
| **01 Application & Integration** | Current Runtime Baseline + current selected GitHub suite 已覆盖 Product Application boundary | Simple QA Host E2E、重复请求/响应丢失、正式 Publication、Domain invalidation + offline consumer、Delivery outcome unknown、Host contract/version compatibility | `NOT_READY` |
| **02 Legal Domain & Work Product** | Wave-001 + current selected GitHub suite 已证明一部分 Domain mutation CAS、幂等冲突、Citation provenance、SQLAlchemy contract 和 Migration contract | 完整 AdmissionReceipt 语义、真实 PostgreSQL race、commit 后 response lost、Domain commit / Checkpoint crash、SecurityEpoch 变化、Migration apply/rollback、失效传播 | `NOT_READY` |
| **03 Knowledge & Evidence** | current selected GitHub suite 已覆盖 Knowledge runtime-batch 与 retrieval composition 基础 | `KnowledgeGeneration → validated manifest → ServingPointer → task ReadinessDecision` 的 Current 闭环、concurrent activation、pointer crash、security revocation、provider rebuild、representative corpus、GraphRAG query-class 对照 | `NOT_READY` |
| **04 Agent Runtime & Control** | current selected GitHub suite 已覆盖 plan、interrupt、restart、replan、tool idempotency、model roles 与 P0 recovery 基础 | Replan Barrier 的完整在途分支验证、Domain receipt recovery E2E、controller fencing/takeover、SecurityEpoch drift、paused checkpoint/schema upgrade、Native Runtime necessity measurement | `NOT_READY` |
| **05 Capability & Skill** | current selected GitHub suite 已覆盖 Capability runtime-batch contract | 统一 CapabilityVersion / ProviderBinding、task-class Qualification / Eligibility 的真实质量证据、semantic drift、non-equivalent fallback、Research-to-Capability E2E | `NOT_READY` |
| **06 Tool Runtime & Effects** | current selected GitHub suite 已覆盖 Tool runtime-batch 与 Outcome Unknown / reconcile 基础语义 | durable PreparedAction / Attempt / Effect ledger、send-boundary crash、remote success/local crash、真实 remote idempotency/query、manual reconcile、Approval/Secret/Audit drift、compensation | `NOT_READY` |
| **07 Model Gateway** | strict provider-SDK / boundary gate、Model Gateway runtime-batch、model-role 与 cost/latency selected tests 已在 current main 通过 | Role qualification、真实 Provider outage/fallback equivalence、Usage settlement、cancel race、egress/credential qualification、production credential、行为漂移回归 | `NOT_READY` |
| **08 Security & Governance** | current selected GitHub suite 已覆盖有限 fail-closed、approval / security runtime contract | revocation-during-run E2E、no-egress、Approval action-hash invalidation、Secret rotation、Mandatory Audit failure、Policy Engine outage、Legal Hold / No-Recall / purge convergence、Prompt Injection gate | `NOT_READY` |
| **09 Observability & Evaluation** | current selected GitHub suite 已覆盖 observability runtime contract 与部分 Eval contract；历史 GraphRAG 小样本研发证据仍可引用 | 正式 DatasetVersion、真实 task-class cases、Judge calibration、A/B/C baseline、critical failure release gate、cost/latency/recovery measurements、court telemetry policy；formal benchmark 仍 `MEASUREMENT_BLOCKED` | `NOT_READY` |

## 为什么 selected verification 通过仍然不能先冻结几个模块

02、03、06、08 等 Reference 已经给出具体 B14.8 failure matrix。冻结的含义是关键语义足够稳定，可以约束实现和 Migration；selected regression 证明当前若干路径没有回归，却没有自动制造真实 PostgreSQL race、网络 send-boundary、权限撤销传播或跨 Store 生命周期证据。

04 和 06 当前已有较多运行行为基础，但它们最危险的正确性仍然跨 Owner：Domain 已提交而 Checkpoint 未写、Effect 已可能发生而本地未知、等待期间权限变化。单模块 test count 或 runtime-batch contract 不能替代这些跨边界 fault evidence。

09 更不能因为 Eval framework 和 selected Eval tests 已通过就冻结质量结论。当前 [`current-eval-baseline.md`](../evidence/current-eval-baseline.md) 继续保持 `MEASUREMENT_BLOCKED`；没有真实 dataset、sample count、baseline 和可复现 config 时，复杂机制的保留条件仍然是 Target 假设。

## 下一批 Evidence Slice 按风险依赖收敛

冻结前不应该九个模块各自开一条平行实现线。更合理的是用少量跨域 slice 同时证明多个 Owner 的边界。

### Slice A — Current-head verification foundation — VERIFIED

GitHub-native selected gate 已建立，并已有 main push success evidence。它继续作为基础 regression 面；后续每个 Freeze slice 仍要在自己的环境和 failure matrix 上增加证明。

### Slice B — Domain ↔ Runtime crash authority — NEXT

围绕最危险的窗口验证：两个 Admission 同时基于 D0；DB/process crash before commit；commit success / response lost；Domain commit success / Runtime Checkpoint missing；Checkpoint complete / matching Receipt absent；新 Evidence 先提交后旧 proposal 晚到。

这条 slice 同时决定 02 和 04 是否真的拥有可冻结的恢复边界。第一步应先把仓库现有 `ZUNO_TEST_DATABASE_URL` PostgreSQL integration test 放进 GitHub service-container 环境，证明真实 PostgreSQL 的基本 transaction / replay；随后再判断现有代码能否通过真实 concurrent D0 race 和 crash-window tests。SQLite probe 不替代 PostgreSQL race evidence。

### Slice C — Effects ↔ Security send boundary

固定 PreparedAction/action hash，验证 send 前授权/Approval/Audit/Secret、新旧 SecurityEpoch，send 后 timeout、remote success/local crash、remote query unavailable、manual reconciliation 和 cancel-in-flight。

这条 slice 同时验证 06 的现实 Effect truth与 08 的“授权只控制未来动作”边界。

### Slice D — Knowledge generation / readiness

用真实多版本材料走 `DocumentVersion → generation build → manifest validation → serving activation → task Readiness → retrieval`，注入 partial write、activation crash、late Worker、新 DocumentVersion、Readiness 后撤权和 provider rebuild。GraphRAG 只在同 query class 的 baseline 对照里决定是否保留。

### Slice E — Capability ↔ Model Gateway qualification

选一个已有专业能力作为样本，让两个 Provider 返回相同 schema，但在 semantic contract、质量、region、budget 或 failure behavior 上不同。验证 Conformance、Qualification / Eligibility、non-equivalent fallback、ProviderVersion drift、model Usage 与 paused/late result provenance。

### Slice F — Application lifecycle E2E

用一个外部 Host 走 accepted → draft/runtime complete → formal WorkProduct → publication → delivery → new-evidence invalidation → consumer offline / reconnect。Application 只组合 Owner facts；Domain、Effects、Security 仍保持自己的 Authority。

### Slice G — Evaluation baseline

在前面至少一条业务 slice 可以稳定运行后，建立冻结 dataset/config/baseline，开始 measurement。优先测 Evidence Sufficiency、Citation Correctness、Unsupported Claim、Recovery Correctness、duplicate Effect、latency、token/cost 和人工介入。GraphRAG、Reflection、Specialist 与 Native Runtime 都用 ablation / kill test 决定保留范围。

## Model Gateway gate maintenance follow-up

初次 review 发现旧 bypass verifier 会把 UTF-8 BOM 解码后的 `U+FEFF` 交给 `ast.parse(str)`，把合法 Python 文件误报成 `syntax-error` / provider bypass。PR #195 已只在 verifier 层修正该问题；main push 的 strict scan 和 boundary verification随后通过，因此此前 `runtime_engine.py` 的 provider bypass 诊断不再成立。

另外两个历史测试残留仍未纳入 current selected gate：`tests/platform/test_model_gateway.py` 仍有一条 monkeypatch 已退休 `zuno.core.models.manager` 的测试；`tests/repo/test_model_gateway_bypass.py` 仍依赖已删除 Program workspace 的 temporary allowlist。它们应在独立 repository-maintenance task 中现代化或删除，不能为了让旧测试运行而恢复 `.agent/programs/work-products/`。

## Review verdict

```text
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
freeze_ready_modules: 0/9
current_head_selected_verification: AVAILABLE @ 4736cf4409658e43af6e129e34dadbd97a5866ad
selected_github_run: 34497460461 / 189 passed, 1 skipped
postgresql_integration: BLOCKED / SKIPPED
formal_benchmark: MEASUREMENT_BLOCKED
production_readiness: NOT_ESTABLISHED
```

下一步进入 Slice B，但任何会修改业务 Runtime、数据库、Migration、Dependencies 或 Production Infrastructure 的工作仍需要独立明确的 Implementation Authorization。本 review 和 selected verification 都不提供该授权。

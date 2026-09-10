# Module Detail Freeze Readiness Review

status: `REVIEW_COMPLETE / NO_MODULE_FROZEN`  
review_snapshot: `eca4a7ebcadbc1c964f174e3b2ce620f9ecbdf5e`  
module_detail_freeze: `NOT_YET`  
implementation_authorization: `NO`

本文记录九个 Target 责任域进入 **Module Detail Freeze Review** 之前的 readiness 审查。它属于 Governance review，不拥有 Target Architecture，也不自动升级 Current Evidence。模块语义继续以 [`docs/modules/`](../modules/README.md) 及各模块 `reference.md` 为准；实现事实继续以 [`docs/evidence/`](../evidence/README.md) 为准。

这次审查只回答一个问题：**当前 Detail Design Candidate 是否已经拥有足够的实现、故障、迁移和跨 Owner 证据，可以进入冻结判断？**

结论是：**0/9 模块满足进入冻结的证据条件，9/9 继续保持 `detail design candidate available`。** 这不是设计失败。九篇 Reference 已经把字段、Guard、Crash Window、Migration 和 Failure Injection 写到可审查粒度；当前缺口主要在这些约束是否已经被 Current 代码和可复现验证证明。

## 先修正一个证据前提

[`current-test-baseline.md`](../evidence/current-test-baseline.md) 中原来的 `verified_head: 1ea56a5...` 与本次 review snapshot 不同。当前主线已经在其后经历代码、测试、文档和治理变化，因此旧的 `90 passed` 只能作为当时的历史 selected verification，不能继续称为当前 HEAD 的 Final Verification。

当前仓库的 GitHub Actions 只保留 `Architecture document set` workflow。它验证 Architecture / Project / Modules / Governance / Evidence 文档集合和对应 repository tests，不运行完整 Runtime、Domain、Knowledge、Security、Effects、Model Gateway 或真实集成测试。因而本次 Freeze readiness 不把“文档 CI 全绿”换写成“当前代码验证完成”。

## 九个责任域的 readiness 结论

| 模块 | 当前可引用基础 | Freeze 前仍缺的关键证明 | Readiness verdict |
| --- | --- | --- | --- |
| **01 Application & Integration** | Current Runtime Baseline 已说明 Product Application Owner 与 Runtime mechanics 分离 | Simple QA Host E2E、重复请求/响应丢失、正式 Publication、Domain invalidation + offline consumer、Delivery outcome unknown、Host contract/version compatibility | `NOT_READY` |
| **02 Legal Domain & Work Product** | Wave-001 已证明一部分 Domain mutation CAS、幂等冲突、Citation provenance guard 和 SQLite/SQLAlchemy contract | 完整 AdmissionReceipt 语义、真实 PostgreSQL race、commit 后 response lost、Domain commit / Checkpoint crash、SecurityEpoch 变化、Migration apply/rollback、失效传播 | `NOT_READY` |
| **03 Knowledge & Evidence** | 历史 Current 已有 ingestion、RAG / GraphRAG、异步处理与 retrieval 基础 | `KnowledgeGeneration → validated manifest → ServingPointer → task ReadinessDecision` 的 Current 闭环、concurrent activation、pointer crash、security revocation、provider rebuild、representative corpus、GraphRAG query-class 对照 | `NOT_READY` |
| **04 Agent Runtime & Control** | Current Runtime Baseline 记录 checkpoint、restart、interrupt、cancel、unknown Effect reconcile 等现有行为 | Replan Barrier、late branch acceptance、Domain receipt recovery E2E、controller fencing/takeover、SecurityEpoch drift、paused checkpoint/schema upgrade、Native Runtime necessity measurement | `NOT_READY` |
| **05 Capability & Skill** | 仓库存在 Skill / Capability / Provider 与部分 contract / test surface | 统一 CapabilityVersion / ProviderBinding、Conformance、task-class Qualification / Eligibility、semantic drift、non-equivalent fallback、Research-to-Capability E2E、质量证据 | `NOT_READY` |
| **06 Tool Runtime & Effects** | Current Runtime Baseline 保留 Outcome Unknown → Reconcile、no blind retry 的行为边界 | durable PreparedAction / Attempt / Effect ledger、send-boundary crash、remote success/local crash、真实 remote idempotency/query、manual reconcile、Approval/Secret/Audit drift、compensation | `NOT_READY` |
| **07 Model Gateway** | 当前代码存在 ModelGateway、routing / attempt / usage 等实现表面 | Role qualification、真实 Provider outage/fallback equivalence、Usage settlement、cancel race、egress/credential qualification、production credential、行为漂移回归；另有旧 bypass tests / verifier 与已退休 Program 路径发生治理漂移 | `NOT_READY` |
| **08 Security & Governance** | Current Runtime/Test 基线记录有限 fail-closed、approval binding、artifact authorization、tenant isolation | revocation-during-run E2E、no-egress、Approval action-hash invalidation、Secret rotation、Mandatory Audit failure、Policy Engine outage、Legal Hold / No-Recall / purge convergence、Prompt Injection gate | `NOT_READY` |
| **09 Observability & Evaluation** | 已有 trace / adapter / eval schema 与历史 GraphRAG 小样本研发证据 | 正式 DatasetVersion、真实 task-class cases、Judge calibration、A/B/C baseline、critical failure release gate、cost/latency/recovery measurements、court telemetry policy；当前 formal benchmark 仍 `MEASUREMENT_BLOCKED` | `NOT_READY` |

## 为什么现在不能“先冻结几个最成熟的模块”

02、03、06、08 等 Reference 已经给出非常具体的 B14.8 failure matrix。冻结的含义应当是这些关键语义足够稳定，可以约束实现和 Migration；如果最危险的 crash window、并发、权限变化或现实副作用仍只有 Target 描述，没有 Current 证据，提前标 `FROZEN` 只会把“文档写得详细”误写成“约束已经验证”。

04 和 06 当前已有较多运行行为基础，但它们最关键的正确性恰好跨 Owner：Domain 已提交而 Checkpoint 未写、Effect 已可能发生而本地未知、等待期间权限变化。单模块 unit test 数量多不能替代这些跨边界 fault evidence。

09 更不能因为已有 Eval framework 就先冻结质量结论。当前 [`current-eval-baseline.md`](../evidence/current-eval-baseline.md) 明确保持 `MEASUREMENT_BLOCKED`；没有真实 dataset、sample count、baseline 和可复现 config 时，复杂机制的保留条件仍然是 Target 假设。

## 下一批 Evidence Slice 按风险依赖收敛

冻结前不应该九个模块各自开一条平行实现线。更合理的是用少量跨域 slice 同时证明多个 Owner 的边界。

### Slice A — Current-head verification foundation

先恢复一个 GitHub-native 的 current-head code verification 入口，或形成等价的可复现 selected-suite 记录。它至少要绑定 commit SHA、测试文件集合、依赖环境、pass/skip/fail 和 blocked reason。文档 CI 与 Runtime/Domain verification 分开记录；不能再使用旧 SHA 的 pass count 作为当前 HEAD 证明。

### Slice B — Domain ↔ Runtime crash authority

围绕最危险的窗口验证：两个 Admission 同时基于 D0；DB/process crash before commit；commit success / response lost；Domain commit success / Runtime Checkpoint missing；Checkpoint complete / matching Receipt absent；新 Evidence 先提交后旧 proposal 晚到。

这条 slice 同时决定 02 和 04 是否真的拥有可冻结的恢复边界。需要真实 PostgreSQL 或能够证明同等并发/事务语义的环境；SQLite probe 不替代 PostgreSQL race evidence。

### Slice C — Effects ↔ Security send boundary

固定 PreparedAction/action hash，验证 send 前授权/Approval/Audit/Secret，新旧 SecurityEpoch，send 后 timeout、remote success/local crash、remote query unavailable、manual reconciliation 和 cancel-in-flight。

这条 slice 同时验证 06 的现实 Effect truth 与 08 的“授权只控制未来动作”边界。

### Slice D — Knowledge generation / readiness

用真实多版本材料走 `DocumentVersion → generation build → manifest validation → serving activation → task Readiness → retrieval`，注入 partial write、activation crash、late Worker、新 DocumentVersion、Readiness 后撤权和 provider rebuild。GraphRAG 只在同 query class 的 baseline 对照里决定是否保留。

### Slice E — Capability ↔ Model Gateway qualification

选一个已有专业能力作为样本，让两个 Provider 返回相同 schema，但在 semantic contract、质量、region、budget 或 failure behavior 上不同。验证 Conformance、Qualification / Eligibility、non-equivalent fallback、ProviderVersion drift、model Usage 与 paused/late result provenance。

### Slice F — Application lifecycle E2E

用一个外部 Host 走 accepted → draft/runtime complete → formal WorkProduct → publication → delivery → new-evidence invalidation → consumer offline / reconnect。Application 只组合 Owner facts；Domain、Effects、Security 仍保持自己的 Authority。

### Slice G — Evaluation baseline

在前面至少一条业务 slice 可以稳定运行后，建立冻结 dataset/config/baseline，开始 measurement。优先测 Evidence Sufficiency、Citation Correctness、Unsupported Claim、Recovery Correctness、duplicate Effect、latency、token/cost 和人工介入。GraphRAG、Reflection、Specialist 与 Native Runtime 都用 ablation / kill test 决定保留范围。

## Model Gateway 旧 gate 的处理边界

本次 source review 发现三个 repository-hygiene 问题，但它们不应被误报成业务 Runtime regression：

- `tests/platform/test_model_gateway.py` 仍 monkeypatch 已退休路径 `zuno.core.models.manager`，当前实现位于 `zuno.agent.core.models.manager`；
- `tests/repo/test_model_gateway_bypass.py` 仍读取已经随旧 Program workspace 退出 current tree 的 `.agent/programs/work-products/temporary-allowlist.yaml`；
- `verify_model_gateway_bypass.py` 使用 `read_text(encoding="utf-8") → ast.parse(str)`，遇到 UTF-8 BOM 文件会把解析失败记录成 `syntax-error`，从而产生伪 bypass inventory。

这些脚本当前也不在正式 [`verification-map`](../../.agent/references/verification-map.md) 的必跑集合中。后续若继续保留，应作为 repository/test maintenance 单独现代化；若已经完全被当前 Gateway contract tests 取代，则应删除而不是恢复旧 Program workspace。无论哪种处理，都不需要修改 07 的 Target Authority。

## Review verdict

```text
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
freeze_ready_modules: 0/9
current_head_runtime_verification: NOT_ESTABLISHED_IN_GITHUB_CI
formal_benchmark: MEASUREMENT_BLOCKED
production_readiness: NOT_ESTABLISHED
```

下一步优先完成 Slice A，重新建立 current-head 的 GitHub-native verification 事实。任何会修改业务 Runtime、数据库、Migration、Dependencies 或 Production Infrastructure 的 slice，都仍需要独立明确的 Implementation Authorization；本 review 本身不提供该授权。

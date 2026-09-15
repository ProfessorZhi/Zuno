# 当前证据入口

`docs/evidence/` 只记录今天可以由代码、Migration、Test、Trace、Eval 或真实运行结果复核的 Current 结论。它不承载历史项目叙事，也不把 Target 文档、目录存在、Mock 或设计计划写成实现或生产证据。

这层文档特别回答一句话：**“你说系统有这个能力，今天有什么工程证据？”**

## 当前保留的证据

| Evidence | 保留理由 |
| --- | --- |
| [Current Runtime Baseline](current-runtime-baseline.md) | 当前 Runtime owner、状态和失败语义的证据入口 |
| [Current Test Baseline](current-test-baseline.md) | 当前 GitHub selected code verification、PostgreSQL Domain / Wave-001 revision probes，以及 Slice C 已确认的正负边界 |
| [Current Eval Baseline](current-eval-baseline.md) | 当前评测与 Measurement Blocked 状态 |
| [Implementation Wave-001](implementation-wave-001.md) | TASK-001 / TASK-003 的有限代码、测试和窄验证证据；不是 Program closure |

Slice C 的 fault evidence 如何影响 Freeze readiness、哪些测试已经停止继续扩张，由 [`Effects ↔ Security Slice C Review`](../governance/effect-security-slice-c-review.md) 收拢。该文件属于 Governance review；底层 Current 事实仍由本目录的固定 Evidence 集合证明。

已删除的 `local-workspace-closure.md` 和 `repository-closure.md` 只是已完成 Program / 工作区收口材料，不是今天需要维护的运行证据；其提交和原始材料仍由 Git 历史保留。

## 当前边界

```text
SELECTED CODE VERIFICATION: AVAILABLE @ 18e4973365461ec939b95063c74f4a0457507e75
SELECTED GITHUB RUN: 34949985244 / 195 passed, 2 warnings
POSTGRESQL DOMAIN SELECTED PROBES: PASS
WAVE-001 REVISION POSTGRESQL APPLY/DOWNGRADE/RE-APPLY: PASS
TARGET ADMISSION RECEIPT: NOT IMPLEMENTATION-PROVEN
UNKNOWN EFFECT RESTART REPLAY: SELECTED PASS / UNKNOWN PRESERVED / NO REDISPATCH
REMOTE SUCCESS + LOCAL EFFECT RECEIPT FAILURE: FALLS BACK TO UNKNOWN / RECONCILE
RECONCILIATION CONVERGENCE: MINIMAL MANUAL/DIRECT CONCLUSIVE WRITER SELECTED-PROVEN; PROVIDER REMOTE-QUERY CONSUMER NOT PROVEN
CANCEL-IN-FLIGHT ORCHESTRATION: NOT IMPLEMENTATION-PROVEN
PRE-EFFECT SECURITY EPOCH REVOCATION: PASS ON DIAGNOSTIC BRANCH
PRE-LEASE SECRET REVOCATION: PASS ON DIAGNOSTIC BRANCH
MANDATORY AUDIT BEFORE EFFECT: TARGET VIOLATION CONFIRMED ON DIAGNOSTIC BRANCH
FORMAL ALEMBIC ENTRYPOINT: STALE IMPORT BLOCKER
PRODUCTION_READINESS: NOT_ESTABLISHED
QUALITY: not_yet_proven
FULL CI: NOT RUN / NOT ESTABLISHED
COURT QA: UNKNOWN / NOT AVAILABLE
```

Main 的 selected verification 现在绑定 `18e4973365461ec939b95063c74f4a0457507e75` / run `34949985244`。该 run 在 PostgreSQL 16.15 service 上执行 selected suite，结果为 `195 passed, 2 warnings in 12.15s`。它继续覆盖 Wave-001 Domain mutation/version 的事务、并发冲突、幂等重放和 revision `20260813_57` 的 `upgrade → downgrade → re-upgrade` DDL，并正式纳入两条 Effect PostgreSQL 回归。

Slice C 现在出现了一条完整的“负向诊断 → 实现修复 → selected regression”。历史 PR #201 / run `34559517466` 曾证明 unresolved Reconciliation 在 restart replay 时会被错误升级成 completed；AUTH-A / PR #242 把同一故障窗口收进 main selected suite。当前结果证明：第一次 Effect outcome unknown 会留下 `UNKNOWN_EFFECT + OPEN/RECONCILE`；销毁并重建 Runtime 后，用同一 action / idempotency identity replay，provider executor 不会再次调用，Runtime 仍返回 `reconcile_required / UNKNOWN_EFFECT`。

AUTH-A 同时建立了最小 conclusive convergence boundary。授权人工 assessment 只有在结论明确为 executed / not-executed 且没有 residual uncertainty 时才收敛；`UNRESOLVED` 且仍有 residual uncertainty 时继续保持 Unknown。显式 resolver 也只接受 conclusive conclusion。确认 executed 后形成 confirmed EffectReceipt，后续 replay 才能进入 completed；确认 not-executed 后形成 `NO_EFFECT / CONFIRMED_NO_EFFECT`，后续 replay 不会把它写成 completed，也不会偷偷再次 dispatch。resolver 在将 Reconciliation 标记为 `RESOLVED` 前会重新读取 exact EffectReceipt，防止唯一约束冲突被 `ON CONFLICT DO NOTHING` 吞掉以后伪造收敛。

这个结果关闭的是历史 restart-certainty defect，以及“Current 完全没有 conclusive writer”这一缺口。它没有证明 provider-specific remote-query consumer、通用 polling/backoff scheduler、完整 Target `ReconciliationReceipt` object、cancel-in-flight orchestration或真实外围 Provider 的对账协议。PR #205 / run `34560692093` 的 Mandatory Audit 负向结果也仍然成立：缺少 durable mandatory-audit proof 时，当前 send path 仍会 dispatch。

其他正向边界保持不变：PR #203 / run `34560042535` 证明 pre-send SecurityEpoch revocation fail closed；PR #207 / run `34566365522` 证明 pre-lease Secret revoke fail closed；PR #210 / run `34567699688` 证明 provider 已返回成功、但本地 EffectReceipt persistence 失败时，Gateway 会留下 `UNKNOWN_EFFECT + OPEN/RECONCILE`，而不是直接宣布 completed。故障形状与 Freeze 影响见 [`Effects ↔ Security Slice C Review`](../governance/effect-security-slice-c-review.md)。

所有需要 fresh PostgreSQL migration chain 的 Slice C 测试仍依赖测试进程临时兼容 `zuno.settings → zuno.platform.settings`，因为正式 Alembic `env.py` 仍引用已退休的 `zuno.settings`。完整 fresh-database migration chain 能在这个 test-only alias 下运行，不等于正式 Alembic entrypoint 已经 clean pass。

这个范围不能扩写成“Zuno PostgreSQL 集成已完成”“完整 Effect recovery 已完成”“自动 Reconciliation 已闭环”“cancel-in-flight 已闭环”“Security 已验证完成”“Secret rotation 已验证完成”“Mandatory Audit 已接入”或“完整 Alembic deployment path 已验证”。AUTH-A 只关闭 restart certainty defect并建立最小 conclusive convergence boundary；provider-specific remote-query consumer、Target `AdmissionReceipt`、02↔04 owner-first recovery、Mandatory Audit durability gate、完整 Secret rotation/retry、其他 Approval / Policy drift、no-egress、其他平台 PostgreSQL 路径、Redis / RabbitMQ / Object Store、真实 Provider 和外部 Host 仍各自需要证据。

当前仓库可以证明有限实现和验证范围，也可以证明若干具体失败；不能证明完整历史技术栈、真实法院质量、生产部署、用户规模、SLA、QPS、HA、No-egress、Sandbox 资格或正式外部验收。历史 Pilot 不等于 Production。

## 评审或技术面试时怎样使用 Evidence

当问题是“为什么这个项目存在、为什么不只用通用平台、项目历史和参与是什么”，先读 [`docs/project/README.md`](../project/README.md)；当问题是“为什么这样设计”，回 `docs/architecture/` 或目标 `docs/modules/`；当问题变成“这个设计现在落地了吗”，才切到 Evidence。

几个常见边界：

- 模块 Part B 写了 `AdmissionReceipt`，只能证明 Target 语义已经设计清楚；当前 PostgreSQL mutation probe 也不能把 mutation record 直接升级成最终 Receipt。
- `Current code selected verification` 通过只能证明 workflow 列出的行为，不等于 Full Project CI 通过。
- revision `20260813_57` 能真实 apply/downgrade/re-upgrade，只证明该 revision 自身 DDL 可逆，不证明真实数据 backfill 或零停机策略。
- 诊断分支失败可以证明某条 Target invariant 在对应 SHA 上不成立；后续 selected regression 可以证明同一故障窗口被修复。历史负向证据保留，不与新的 Current 状态混写。
- `Outcome Unknown` 的耐久记录本身不等于完整 recovery。AUTH-A 已证明 unresolved reconciliation 跨 restart 保持 UNKNOWN，且存在最小 conclusive manual/direct writer；provider-specific remote-query consumer 仍未证明。
- provider success 后 local EffectReceipt 写失败能够退回 Unknown，证明现有 exception/persistence-failure fallback；AUTH-A 又证明这个 Unknown 可以在 selected PostgreSQL replay 中保持 certainty 并通过 conclusive resolution 收敛。它仍不证明真实 process-crash timing 或通用 provider 自动对账。
- pre-send SecurityEpoch revocation 与 pre-lease Secret revocation 已有正向 fault evidence，不代表完整 Secret rotation/retry、Approval hash drift、Policy Engine outage 或 no-egress 已经证明。
- `security_audit_requirements` 存在，不代表 matching AuditPersistenceReceipt 已提交；#205 已证明当前 send path 会在 durable audit proof 缺失时继续 dispatch。
- Cancellation receipt / async-job primitive 存在，不等于 Runtime 已经把用户取消、provider cancel、callback race 和最终 Effect truth 接成可恢复协议。
- 正式 Alembic chain 在 test-only import alias 下能跑到 head，不等于正式 Alembic entrypoint 已修复。
- `ModelCallAttempt` 或 Tool contract 有单元测试，不等于真实 Provider / 真实外围法院系统已经完成 E2E。
- Eval Dataset schema 存在，不等于正式 benchmark 已测；zero sample 或缺 credentials 时必须保持 BLOCKED。
- Pilot 是历史项目阶段，不自动成为今天 main 的 Current runtime evidence。
- 架构设计比通用平台多出 Domain State、Readiness、Formal Admission、Effect Recovery 等语义，不等于已经测出质量 / 成本优势；优势需要 09 的正式对照测量。

## 从“设计差异”升级成“已证明优势”需要什么

例如要回答“Zuno 为什么比通用宿主更值得用于复杂法律任务”，仅有架构文档还不够。至少需要把相同任务、相同语料、相近模型和预算放进可以比较的实验，例如：

```text
A. Generic Host + Legal Skills
B. Generic Host + Zuno Legal Backend
C. Zuno Native Runtime + First-class Domain State
```

然后测量 Evidence Sufficiency、Citation Correctness、Unsupported Claim、Reviewer Acceptance、Recovery Correctness、duplicate-effect、Latency、Token、Cost 等指标。只有差异稳定、样本充分且故障路径也成立，才能把“设计优势假设”升级成“测量支持的优势”。

同样，GraphRAG、Long-term Memory、Specialist / Multi-Agent 和 Native Runtime 都需要自己的消融或 complexity kill test。

## 读取规则

- 先看对应 Evidence 的 scope、command、result 和 known gaps；
- 正向与负向 Evidence 都必须绑定具体 SHA / run / test shape，不按印象扩写；
- Source review 只能证明代码表面存在/缺失到搜索与人工核对的范围；不能把“没有搜到”泛化成仓库永远没有，只能据此保持 `NOT_IMPLEMENTATION_PROVEN`；
- 只把明确覆盖的结论称为 Current；
- 项目历史、用户回忆和产品定位回到 [`docs/project/README.md`](../project/README.md)；更严格的一句话能否采用，再核对 [`project-fact-provenance.md`](../governance/project-fact-provenance.md)；
- Red / Blue 的旧讨论只回到 [`docs/red-blue/archive/legacy/`](../red-blue/archive/legacy/README.md)，不作为 Evidence；新的 Round Findings 同样不能自动升级 Current；
- Architecture Target 和 ADR 的语义不由本目录拥有；
- 技术面试的项目级问题从 Project 的 Reviewer 章节进入；具体架构、模块或实现问题再按 Owner 继续深入。

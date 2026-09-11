# 当前证据入口

`docs/evidence/` 只记录今天可以由代码、Migration、Test、Trace、Eval 或真实运行结果复核的 Current 结论。它不承载历史项目叙事，也不把 Target 文档、目录存在、Mock 或设计计划写成实现或生产证据。

这层文档特别回答一句话：**“你说系统有这个能力，今天有什么工程证据？”**

## 当前保留的证据

| Evidence | 保留理由 |
| --- | --- |
| [Current Runtime Baseline](current-runtime-baseline.md) | 当前 Runtime owner、状态和失败语义的证据入口 |
| [Current Test Baseline](current-test-baseline.md) | 当前 GitHub selected code verification、PostgreSQL Domain / Wave-001 revision probes，以及 Slice C Effect / Audit 负向证据和 Security pre-send revocation 正向证据 |
| [Current Eval Baseline](current-eval-baseline.md) | 当前评测与 Measurement Blocked 状态 |
| [Implementation Wave-001](implementation-wave-001.md) | TASK-001 / TASK-003 的有限代码、测试和窄验证证据；不是 Program closure |

已删除的 `local-workspace-closure.md` 和 `repository-closure.md` 只是已完成 Program / 工作区收口材料，不是今天需要维护的运行证据；其提交和原始材料仍由 Git 历史保留。

## 当前边界

```text
SELECTED CODE VERIFICATION: AVAILABLE @ c817bd345c9025524c6380ef208a131277d164bd
SELECTED GITHUB RUN: 34499552197 / 193 passed
POSTGRESQL DOMAIN SELECTED PROBES: PASS
WAVE-001 REVISION POSTGRESQL APPLY/DOWNGRADE/RE-APPLY: PASS
TARGET ADMISSION RECEIPT: NOT IMPLEMENTATION-PROVEN
UNKNOWN EFFECT RESTART REPLAY: TARGET VIOLATION CONFIRMED ON DIAGNOSTIC BRANCH
PRE-EFFECT SECURITY EPOCH REVOCATION: PASS ON DIAGNOSTIC BRANCH
MANDATORY AUDIT BEFORE EFFECT: TARGET VIOLATION CONFIRMED ON DIAGNOSTIC BRANCH
FORMAL ALEMBIC ENTRYPOINT: STALE IMPORT BLOCKER
PRODUCTION_READINESS: NOT_ESTABLISHED
QUALITY: not_yet_proven
FULL CI: NOT RUN / NOT ESTABLISHED
COURT QA: UNKNOWN / NOT AVAILABLE
```

Main 的正向 selected verification 说明一组明确列出的 Domain、Citation、Application、Runtime、Knowledge、Capability、Tool、Model Gateway、Security、Observability、Retrieval 与 Eval 行为在同一个 main SHA 的 GitHub runner 上通过。对应 run 还使用 PostgreSQL 16.15 service 验证了 Wave-001 Domain mutation/version 的基本事务、并发冲突、幂等重放，以及 revision `20260813_57` 自身的 `upgrade → downgrade → re-upgrade` DDL。

Current Evidence 同时记录失败和窄范围成功的诊断结果。PR #201 / run `34559517466` 复现了 06↔04 的外部 Effect 恢复缺陷：第一次 UNKNOWN Effect 能耐久写成 `UNKNOWN_EFFECT + OPEN/RECONCILE`，重启后同一 action identity 没有二次 dispatch，但 Runtime 把仍未完成 Reconciliation 的 replay 返回成 `completed`。

PR #203 / run `34560042535` 验证了 08 的一个具体时间窗口：动作在 prepare / Approval 时仍有有效 SecurityEpoch，随后该 epoch 在真正发送前变成 `revoked`。Current Gateway 在 provider dispatch 前重新读取安全事实并 fail closed；executor 没有被调用，Attempt / ExecutionReceipt 分别保持 `FAILED / NOT_DISPATCHED` 与 `FAILED / NO_EFFECT`，没有生成 EffectReceipt 或 Reconciliation。

PR #205 / run `34560692093` 又确认了另一条独立缺陷：Security 已经创建 audit requirement，但没有任何 matching durable mandatory-audit fact 时，Current Gateway 仍调用 provider executor、写入 EffectReceipt 并返回 `completed`。这说明“必须审计”的要求与“审计已经耐久提交”的证明没有在 06 send gate 闭合。Requirement 存在不能代替 AuditPersistenceReceipt。

三条 Slice C 诊断都需要测试进程临时兼容 `zuno.settings → zuno.platform.settings`，因为正式 Alembic `env.py` 仍引用已退休的 `zuno.settings`。完整 fresh-database migration chain 能在这个 test-only alias 下运行，不等于正式 Alembic entrypoint 已经 clean pass。

这个范围不能扩写成“Zuno PostgreSQL 集成已完成”“完整 Effect recovery 已完成”“Security 已验证完成”“Mandatory Audit 已接入”或“完整 Alembic deployment path 已验证”。Target `AdmissionReceipt`、02↔04 owner-first recovery、unresolved Effect replay、Mandatory Audit durability gate、其他 Approval / Secret / Policy drift、no-egress、其他平台 PostgreSQL 路径、Redis / RabbitMQ / Object Store、真实 Provider 和外部 Host仍各自需要证据。详细正负结果见 [`current-test-baseline.md`](current-test-baseline.md)。

当前仓库可以证明有限实现和验证范围，也可以证明若干具体失败；不能证明完整历史技术栈、真实法院质量、生产部署、用户规模、SLA、QPS、HA、No-egress、Sandbox 资格或正式外部验收。历史 Pilot 不等于 Production。

## 评审或技术面试时怎样使用 Evidence

当问题是“为什么这个项目存在、为什么不只用通用平台、项目历史和参与是什么”，先读 [`docs/project/README.md`](../project/README.md)；当问题是“为什么这样设计”，回 `docs/architecture/` 或目标 `docs/modules/`；当问题变成“这个设计现在落地了吗”，才切到 Evidence。

几个常见边界：

- 模块 Part B 写了 `AdmissionReceipt`，只能证明 Target 语义已经设计清楚；当前 PostgreSQL mutation probe 也不能把 mutation record 直接升级成最终 Receipt。
- `Current code selected verification` 通过只能证明 workflow 列出的行为，不等于 Full Project CI 通过。
- revision `20260813_57` 能真实 apply/downgrade/re-apply，只证明该 revision 自身 DDL 可逆，不证明真实数据 backfill 或零停机策略。
- 诊断分支失败可以证明某条 Target invariant 当前不成立；诊断分支成功也只证明它实际注入并观察到的 fault window。
- `Outcome Unknown` 的耐久记录存在，不等于 recovery 已正确闭环；当前已经观测到 restart replay 把 unresolved reconciliation 错误升级成 completed。
- pre-send SecurityEpoch revocation 已有正向 fault evidence，不代表 Secret rotation、Approval hash drift、Policy Engine outage 或 no-egress 已经证明。
- `security_audit_requirements` 存在，不代表 matching AuditPersistenceReceipt 已提交；#205 已证明当前 send path 会在 durable audit proof 缺失时继续 dispatch。
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
- 只把明确覆盖的结论称为 Current；
- 项目历史、用户回忆和产品定位回到 [`docs/project/README.md`](../project/README.md)；更严格的一句话能否采用，再核对 [`project-fact-provenance.md`](../governance/project-fact-provenance.md)；
- Red / Blue 的旧讨论只回到 [`docs/red-blue/archive/legacy/`](../red-blue/archive/legacy/README.md)，不作为 Evidence；新的 Round Findings 同样不能自动升级 Current；
- Architecture Target 和 ADR 的语义不由本目录拥有；
- 技术面试的项目级问题从 Project 的 Reviewer 章节进入；具体架构、模块或实现问题再按 Owner 继续深入。

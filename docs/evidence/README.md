# 当前证据入口

`docs/evidence/` 只记录今天可以由代码、Migration、Test、Trace、Eval 或真实运行结果复核的 Current 结论。它不承载历史项目叙事，也不把 Target 文档、目录存在、Mock 或设计计划写成实现或生产证据。

这层文档特别回答一句话：**“你说系统有这个能力，今天有什么工程证据？”**

## 当前保留的证据

| Evidence | 保留理由 |
| --- | --- |
| [Current Runtime Baseline](current-runtime-baseline.md) | 当前 Runtime owner、状态和失败语义的证据入口 |
| [Current Test Baseline](current-test-baseline.md) | 当前测试范围、未运行项和质量边界 |
| [Current Eval Baseline](current-eval-baseline.md) | 当前评测与 Measurement Blocked 状态 |
| [Implementation Wave-001](implementation-wave-001.md) | TASK-001 / TASK-003 的有限代码、测试和窄验证证据；不是 Program closure |

已删除的 `local-workspace-closure.md` 和 `repository-closure.md` 只是已完成 Program / 工作区收口材料，不是今天需要维护的运行证据；其提交和原始材料仍由 Git 历史保留。

## 当前边界

```text
PRODUCTION_READINESS: NOT_ESTABLISHED
QUALITY: not_yet_proven
FULL CI: NOT RUN
COURT QA: UNKNOWN / NOT AVAILABLE
```

当前仓库可以证明有限实现和验证范围，不能证明完整历史技术栈、真实法院质量、生产部署、用户规模、SLA、QPS、HA、No-egress、Sandbox 资格或正式外部验收。历史 Pilot 不等于 Production。

## 评审或技术面试时怎样使用 Evidence

当问题是“为什么这个项目存在、为什么不只用通用平台、项目历史和参与是什么”，先读 [`docs/project/project.md`](../project/project.md)；当问题是“为什么这样设计”，回 `docs/architecture/` 或目标 `docs/modules/`；当问题变成“这个设计现在落地了吗”，才切到 Evidence。

几个常见边界：

- 模块 Part B 写了 `AdmissionReceipt`，只能证明 Target 语义已经设计清楚；只有代码、Migration、Test 和故障恢复证据才能证明实现可用。
- 文档 CI 通过只能证明文档、链接、Validator 和对应 focused tests 通过，不能说 Full Project CI 通过。
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
- 只把明确覆盖的结论称为 Current；
- 项目历史、用户回忆和产品定位回到 [`docs/project/project.md`](../project/project.md)；更严格的一句话能否采用，再核对 [`project-fact-provenance.md`](../governance/project-fact-provenance.md)；
- Red / Blue 讨论只回到 `docs/history/red-blue/`，不作为 Evidence；
- Architecture Target 和 ADR 的语义不由本目录拥有；
- 技术面试的项目级问题从 `project.md` 的 Reviewer 章节进入；具体架构、模块或实现问题再按 Owner 继续深入。

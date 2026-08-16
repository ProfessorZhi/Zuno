# Zuno 项目文档

`docs/` 是 Zuno 的正式项目知识入口。当前文档按“为什么有项目 → 为什么这样设计 → 每个责任域怎样工作 → 今天到底证明了什么”组织：

```text
docs/
├── README.md
├── project/                    项目级 Human-first 叙事：README + project.md
├── architecture/               总体 Target Architecture（固定四文件）
├── modules/                    九个 Target 责任域的 Deep Design V2；02 / 03 已进入 Detail Design Candidate V1
│   ├── README.md
│   ├── 01-application-integration.md
│   ├── 02-legal-domain-work-product.md
│   ├── 03-knowledge-evidence.md
│   ├── 04-agent-runtime-control.md
│   ├── 05-capability-skill.md
│   ├── 06-tool-runtime-effects.md
│   ├── 07-model-gateway.md
│   ├── 08-security-governance.md
│   └── 09-observability-evaluation.md
├── decisions/                  有效 ADR
├── governance/                 来源、Ownership、Contract 与文档规则
├── evidence/                   当前可复现证据
├── history/red-blue/           架构审查过程记录
├── operations/                 当前运维 Runbook / profile
└── terminology.md
```

## 推荐阅读顺序

第一次理解项目或准备技术面试，优先走一条连续主线：

1. [Project 主文档](./project/project.md)：项目是什么、为什么立项、为什么不只用通用平台、项目怎样发展、团队和个人参与、哪些差异已经证明以及 Reviewer 常见追问。
2. [总体架构](./architecture/architecture.md)：跨 Product、Domain、Knowledge、Capability、Runtime、Tool、Model、Security、Eval 为什么这样组织。
3. [模块架构](./modules/README.md)：通过真实任务主线理解九个责任域，再进入目标模块 Part A；需要实现级细节时再读 Part B / Part C。02 / 03 的字段、事务、Serving、Migration 和 Failure Injection 继续进入 B14.1–B14.8 Detail Freeze Candidate。
4. [有效 ADR](./decisions/README.md)：仍然影响长期设计的架构决策。
5. [Current Evidence](./evidence/README.md)：代码、测试、运行和评测到底证明了什么。
6. [Red / Blue 审查历史](./history/red-blue/README.md)：需要理解架构为何被质疑、如何收敛时再读。
7. [术语表](./terminology.md)：跨文档统一术语。

`docs/project/README.md` 只是很薄的入口，不再维护第二套项目故事。项目事实的严格来源、允许表述和 Unknown 由 [`governance/project-fact-provenance.md`](./governance/project-fact-provenance.md) 维护。

## 一套回答问题的方法

```text
为什么会有这个项目、为什么值得做？       → project/project.md
为什么今天这样设计？                   → architecture/
每个责任域内部怎样工作和恢复？         → modules/
02 / 03 字段、事务、Serving 如何冻结前细化？ → modules/02、03 的 B14.1–B14.8
现在到底实现和验证到了什么程度？       → evidence/
这项长期决策为什么被接受？             → decisions/
这句话的历史事实来源是什么？           → governance/project-fact-provenance.md
```

一个完整技术回答最好同时覆盖“现实问题是什么、为什么这样设计、系统怎样运行和失败、当前有什么证据、还有什么没有证明”，而不是只背技术栈。

## 当前文档状态

```text
overall_architecture: ROUND_02_FROZEN
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_human_narrative: DEEPENED
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 2/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
quality_proven: NO
production_readiness: NOT_ESTABLISHED
```

九篇模块已经拥有 Human-first Part A，并建立 Part B / Part C 的工程语义和跨模块一致性。02 / 03 进一步把字段语义、并发 / 版本 Guard、PostgreSQL / Serving 发布点、Crash Window、Schema Evolution 和 Failure Injection 写到 Detail Design Candidate V1；这仍不等于最终 enum、数据库 Schema、Migration、实现或 Production 资格已经冻结。

## 文档边界

- `project/` 只保留 `README.md` 和 `project.md`。`project.md` 是项目级唯一人类主叙事，负责项目来源、立项逻辑、通用平台边界、发展过程、参与事实与项目级 Reviewer 问题；它不证明 Target 已实现。
- `architecture/` 是唯一总体 Target Architecture，说明跨模块设计原则，不证明实现或生产部署。
- `modules/` 展开已经冻结的九个逻辑责任域；九篇均达到 Deep Design V2 / Cross-Module Consistency，只有 02 / 03 进一步达到 Detail Design Candidate V1。`module_detail_freeze` 仍为 `NOT_YET`，Implementation Authorization 仍为 `NO`。
- `decisions/` 只保留仍有长期约束力的 ADR，不保存一次性施工记录。
- `evidence/` 只记录当前代码、Migration、Test、Trace、Eval 和可复现运行证据。
- `operations/` 只保存当前仍需执行的运维 Runbook 或恢复 profile。
- `history/red-blue/` 只保存有长期复盘价值的原始架构审查记录；它不是架构、事实、证据或 ADR 的 Owner。
- `governance/` 保存来源、Owner、兼容 Contract 和文档规则，不替代 Human-first 正文。

`Current`、`Target`、`Future`、`History` 和 `Unknown` 必须保持区分。Project 讲得完整不代表历史细节已经全部恢复；模块写得完整不代表代码已经实现；Current 只能由代码、Migration、Test、Trace、Eval 或真实运行结果证明。
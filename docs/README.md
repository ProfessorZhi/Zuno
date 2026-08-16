# Zuno 项目文档

`docs/` 是 Zuno 的正式项目知识入口。当前文档按“为什么有项目 → 为什么这样设计 → 每个责任域怎样工作 → 今天到底证明了什么”组织：

```text
docs/
├── README.md
├── project/                    项目级 Human-first 叙事：README + project.md
├── architecture/               总体 Target Architecture（固定四文件）
├── modules/                    九个 Target 责任域：Deep Design V2 + Detail Design Candidate V1（9/9）
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

第一次理解项目或准备技术面试：

1. [Project 主文档](./project/project.md)：项目是什么、为什么立项、为什么不只用通用平台、项目怎样发展、团队和参与事实、哪些差异已经证明。
2. [总体架构](./architecture/architecture.md)：跨 Product、Domain、Knowledge、Capability、Runtime、Tool、Model、Security、Eval 为什么这样组织。
3. [模块架构](./modules/README.md)：先通过真实任务主线理解九个责任域，再读目标模块 Part A；实现级审查继续读 Part B / Part C，字段、事务、Crash Window、Migration 和 Failure Injection 读 B14.1–B14.8。
4. [有效 ADR](./decisions/README.md)：仍然影响长期设计的决策。
5. [Current Evidence](./evidence/README.md)：代码、测试、运行和评测到底证明了什么。
6. [Red / Blue 审查历史](./history/red-blue/README.md)：需要理解架构如何被质疑、如何收敛时再读。
7. [术语表](./terminology.md)：跨文档统一术语。

`docs/project/README.md` 只是导航。项目事实来源、允许表述和 Unknown 由 [`governance/project-fact-provenance.md`](./governance/project-fact-provenance.md) 管理。

## 一套回答问题的方法

```text
为什么会有这个项目、为什么值得做？      → project/project.md
为什么今天这样设计？                  → architecture/
每个责任域内部怎样工作和恢复？        → modules/
字段、Guard、事务、Crash/Migration？   → 对应 module B14.1–B14.8
现在到底实现和验证到了什么程度？      → evidence/
长期决策为什么被接受？                → decisions/
历史事实来源是什么？                  → governance/project-fact-provenance.md
```

一个完整技术回答应覆盖“现实问题、设计原因、正常与失败流程、当前证据和仍未证明的部分”，而不是只背技术栈或数据库表。

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
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
quality_proven: NO
production_readiness: NOT_ESTABLISHED
```

九篇模块都已经有 Human-first Part A、B1–B14 Engineering Reference、Part C Cross-Module Consistency，并进一步拥有 B14.1–B14.8 Detail Freeze Candidate：核心字段、Identity / Version、新鲜度、幂等、事务 / 持久化、并发、Crash Window、Schema Evolution 和 Failure Injection 都已经进入冻结前审查。

这仍然不等于最终 enum、数据库 Schema、Migration、API 或服务拓扑被冻结，更不等于代码已经实现。下一道门是 Module Detail Freeze Review；实现仍需要独立明确授权。

## 文档边界

- `project/` 只保留 `README.md` 和 `project.md`；项目故事不证明 Target 已实现。
- `architecture/` 是唯一总体 Target Architecture，固定四文件。
- `modules/` 展开九个冻结责任域；当前 9/9 为 Detail Design Candidate V1，但 `module_detail_freeze: NOT_YET`。
- `decisions/` 只保留仍有长期约束力的 ADR。
- `evidence/` 只记录 Current 代码、Migration、Test、Trace、Eval 和运行证据。
- `operations/` 保存当前 Runbook / recovery profile。
- `history/red-blue/` 保存架构审查历史，不拥有当前事实或 Target。
- `governance/` 保存来源、Owner、兼容 Contract 和文档规则，不替代 Human-first 正文。

`Current`、`Target`、`Future`、`History` 和 `Unknown` 必须区分。文档写得完整不证明实现可用；Current 只能由代码、Migration、Test、Trace、Eval 或真实运行结果证明。
# Zuno 项目文档

`docs/` 是 Zuno 的正式项目知识入口。为了让项目故事、产品定位、总体架构、模块设计和当前证据不再分散，当前树保留少数稳定入口：

```text
docs/
├── README.md
├── project/                    项目故事、立项逻辑、团队、开发过程与审查问题地图
├── architecture/               总体 Target Architecture（固定四文件）
├── modules/                    九个 Target 责任域的 Deep Design V2
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

按项目理解、架构评审或技术面试准备，建议依次阅读：

1. [项目说明](./project/README.md)：先了解 Zuno 的来源、方向和当前阶段。
2. [项目背景](./project/project-background.md)：项目为什么出现、来自什么研究和业务背景。
3. [产品定位、立项逻辑与差异化](./project/product-positioning-and-value.md)：为什么通用平台已经存在仍值得做 Zuno，哪些属于差异化设计，哪些优势仍需测量。
4. [团队与开发分工](./project/team-and-contributions.md)：团队规模、用户参与方向和个人职责边界。
5. [开发过程](./project/development-process.md)：项目如何从已有产品发展到 Demo、法院测试和 Pilot。
6. [总体架构](./architecture/architecture.md)：跨 Product、Domain、Knowledge、Capability、Runtime、Tool、Model、Security、Eval 为什么这样组织。
7. [模块架构](./modules/README.md)：先通过真实任务主线理解九个责任域，再进入模块正文。九篇均使用 Part A / B / C：Part A 面向人，Part B 给工程设计，Part C 检查跨模块一致性。
8. [项目与架构审查问题地图](./project/review-question-map.md)：当 Reviewer 或面试官按问题追问时，快速回到正确事实源。
9. [有效 ADR](./decisions/README.md)：仍然影响长期设计的架构决策。
10. [Current Evidence](./evidence/README.md)：代码、测试、运行和评测到底证明了什么。
11. [Red / Blue 审查历史](./history/red-blue/README.md)：只在需要理解架构演进理由时阅读。
12. [术语表](./terminology.md)：跨文档统一术语。

## 一套回答问题的方法

Project、Architecture、Modules、Evidence 分别回答不同问题：

```text
为什么会有这个项目？               → project/
为什么今天这样设计？               → architecture/
每个责任域内部怎样工作和恢复？     → modules/
现在到底实现和验证到了什么程度？   → evidence/
这项长期决策为什么被接受？         → decisions/
这句话的历史事实来源是什么？       → governance/project-fact-provenance.md
```

这套分工同样适用于技术面试。一个完整回答最好同时覆盖“问题是什么、为什么这样设计、系统怎样运行 / 失败、当前有什么证据、还有什么没证明”，而不是只背技术栈。

## 当前文档状态

```text
overall_architecture: ROUND_02_FROZEN
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_human_narrative: DEEPENED
module_detail_freeze: NOT_YET
implementation_authorization: NO
quality_proven: NO
production_readiness: NOT_ESTABLISHED
```

九篇模块已经拥有足够体量的 Human-first Part A，并建立 Part B / Part C 的工程语义和跨模块一致性，但仍不等于字段级 Contract、最终 enum、数据库 Schema、Migration 或 Production 资格已经冻结。

## 文档边界

- `project/` 是项目故事、产品定位和项目理解的唯一正式入口；它不证明 Target 已实现。
- `architecture/` 是唯一总体 Target Architecture，说明跨模块设计原则，不证明实现或生产部署。
- `modules/` 展开已经冻结的九个逻辑责任域；当前达到 Deep Design V2 / Cross-Module Consistency，可作为详细设计和审查基线，但仍不等于 Module Detail Freeze 或 Implementation Authorization。
- `decisions/` 只保留仍然有长期约束力的 ADR，不保存一次性施工记录。
- `evidence/` 只记录当前代码、Migration、Test、Trace、Eval 和可复现运行证据。
- `operations/` 只保存当前仍需执行的运维 Runbook 或恢复 profile。
- `history/red-blue/` 只保存有长期复盘价值的原始架构审查记录；它不是架构、事实、证据或 ADR 的 Owner。
- `governance/` 保存来源、Owner、兼容 Contract 和文档规则，不替代 Human-first 正文。

`Current`、`Target`、`Future`、`History` 和 `Unknown` 必须保持区分。模块文档写得完整不代表代码已经实现；Current 只能由代码、Migration、Test、Trace、Eval 或真实运行结果证明。

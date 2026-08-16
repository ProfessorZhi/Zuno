# Zuno 项目文档

`docs/` 是 Zuno 的正式项目知识入口。为了让项目故事、总体架构、模块设计和当前证据不再分散，当前树保留少数稳定入口：

```text
docs/
├── README.md
├── project/                    项目故事、背景、团队与开发过程
├── architecture/               总体 Target Architecture（固定四文件）
├── modules/                    九个 Target 责任域的模块 Design Baseline V1
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

## 阅读顺序

按项目阅读或面试准备，依次阅读：

1. [项目说明](./project/README.md)：先了解 Zuno 的来源、方向和当前阶段。
2. [项目背景](./project/project-background.md)：项目为什么存在、来自什么研究和业务背景。
3. [团队与开发分工](./project/team-and-contributions.md)：团队规模、用户参与方向和个人职责边界。
4. [开发过程](./project/development-process.md)：项目如何从已有产品发展到 Agent、Memory / Context、工具调用、Demo、法院测试和 Pilot。
5. [总体架构](./architecture/architecture.md)：跨 Product、Domain、Capability、Runtime、Data、Security、Eval 和部署为什么这样组织。
6. [架构视图](./architecture/architecture-views.md) 和 [HTML 展示](./architecture/architecture.html)：总体架构的图形配对，不拥有第二套事实。
7. [模块架构](./modules/README.md)：先通过三条真实任务主线理解九个责任域，再按需要进入模块正文。每篇 Part A 面向人解释问题、流程、失败和边界，Part B 给出 B1–B14 工程设计基线。
8. [有效 ADR](./decisions/README.md)：仍然影响长期设计的架构决策。
9. [Current Evidence](./evidence/README.md)：代码、测试、运行和评测到底证明了什么。
10. [Red / Blue 审查历史](./history/red-blue/README.md)：只在需要理解架构演进理由时阅读。
11. [术语表](./terminology.md)：跨文档统一术语。

## 文档边界

- `project/` 是项目故事的唯一正式入口。
- `architecture/` 是唯一总体 Target Architecture，说明跨模块设计原则，不证明实现或生产部署。
- `modules/` 只展开已经冻结的九个逻辑责任域；当前模块正文是 `design-baseline-v1`，边界、Owner、主要 Contract、状态族、失败与恢复方向已经可作为详细设计基线，但仍不等于字段级 Module Freeze、数据库冻结或 Implementation Authorization。
- `decisions/` 只保留仍然有长期约束力的 ADR，不保存一次性施工记录。
- `evidence/` 只记录当前代码、测试、Trace、Eval 和可复现运行证据。
- `operations/` 只保存当前仍需执行的运维 Runbook 或恢复 profile。
- `history/red-blue/` 只保存有长期复盘价值的原始架构审查记录；它不是架构、事实、证据或 ADR 的 Owner。
- `governance/` 保存来源、Owner、兼容 Contract 和文档规则，不替代 Human-first 正文。

`Current`、`Target`、`Future` 和 `Unknown` 必须保持区分。模块文档写得完整不代表代码已经实现；Current 只能由代码、Migration、Test、Trace、Eval 或真实运行结果证明。

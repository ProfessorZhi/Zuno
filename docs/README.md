# Zuno 项目文档

`docs/` 是 Zuno 的正式项目知识入口。为了让项目故事、架构和当前证据不再分散，当前树只保留少数稳定入口：

```text
docs/
├── README.md
├── project/
│   ├── project-background.md
│   └── development-process.md
├── architecture/
│   ├── README.md
│   ├── architecture.md
│   ├── architecture-views.md
│   └── architecture.html
├── modules/
│   └── README.md
├── decisions/
│   ├── README.md
│   └── active ADRs
├── evidence/
│   └── 当前可复现证据
├── history/
│   ├── README.md
│   └── red-blue/              架构审查过程记录
├── operations/
│   └── 当前运维 Runbook / profile
└── terminology.md
```

## 阅读顺序

按项目阅读或面试准备，依次阅读：

1. [项目背景](./project/project-background.md)：项目为什么存在、来自什么研究和业务背景、哪些历史事实仍未知。
2. [开发过程](./project/development-process.md)：项目如何从已有产品发展到 Agent、Memory/Context、工具调用、Demo、法院测试和 Pilot，以及用户实际参与边界。
3. [总体架构](./architecture/architecture.md)：跨 Product、Domain、Capability、Runtime、Data、Security、Eval 和部署为什么这样组织。
4. [架构视图](./architecture/architecture-views.md) 和 [HTML 展示](./architecture/architecture.html)：总体架构的图形配对，不拥有第二套事实。
5. [模块边界](./modules/README.md)：当前只说明模块尚未冻结，不提前制造编号模块。
6. [有效 ADR](./decisions/README.md)：仍然影响长期设计的架构决策。
7. [Current Evidence](./evidence/README.md)：代码、测试、运行和评测到底证明了什么。
8. [Red / Blue 审查历史](./history/red-blue/README.md)：只在需要理解架构演进理由时阅读。
9. [术语表](./terminology.md)：跨文档统一术语。

## 文档边界

- `project/` 是项目故事的唯一正式入口。后续用户确认历史事实时，直接更新这两个文件，不再恢复第二套 `facts/` 或确认台账。
- `architecture/` 是唯一总体 Target Architecture。它说明设计原则，不证明实现或生产部署。
- `modules/` 只有边界占位；模块数量和边界稳定后才新增模块正文。
- `decisions/` 只保留仍然有长期约束力的 ADR，不保存一次性施工记录。
- `evidence/` 只记录当前代码、测试、Trace、Eval 和可复现运行证据。
- `operations/` 只保存当前仍需执行的运维 Runbook 或恢复 profile。
- `history/red-blue/` 只保存有长期复盘价值的原始架构审查记录；它不是架构、事实、证据或 ADR 的 Owner。接受的结果只能进入总体架构或 ADR。

`Current`、`Target`、`Future` 和 `Unknown` 必须保持区分。当前代码有某个目录或类名，不代表历史项目使用过它；Target Architecture 有某项设计，也不代表已经生产完成。

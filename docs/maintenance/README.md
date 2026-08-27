# Zuno Maintenance Plane

`docs/maintenance/` 保存**如何维护 Zuno**的运行、Agent 协作和历史审查材料。它不拥有项目故事、Target Architecture、Module 设计或 Current Evidence。

维护资料回答的是：

> 人和 Agent 怎样安全地运行、修改、审查和追溯这个仓库？

## 目录

```text
docs/maintenance/
├── README.md
├── operations/                 当前仍需执行的 Runbook / recovery profile
├── agent-workflow/             人类可读的 ChatGPT / Claude Code / GitHub 工作协议
└── history/                    已发生的架构审查与历史记录
    └── red-blue/               Red / Blue Architecture Review Archive
```

## 与其他一级目录的边界

- `project/`：真实项目来源、发展、团队与个人参与、Current / Target / Unknown 的项目叙事。
- `research/`：经过来源核验的研究谱系、外部平台基线与 Research-to-Engineering 推导。
- `architecture/`：唯一总体 Target Architecture。
- `modules/`：九个责任域的 Part A / Part B / Part C。
- `decisions/`：仍有长期约束力的 ADR。
- `evidence/`：代码、Migration、Test、Trace、Eval 和运行证据。
- `governance/`：事实来源、Owner、文档标准与兼容 Contract 规则。

`maintenance/` 不能把历史讨论升级成当前事实，也不能因为某个操作手册存在就证明对应 Production 能力已经建立。

## 三类维护材料

### Operations

[`operations/`](./operations/) 保存当前仍需执行的运维流程，例如 PostgreSQL migration runbook 和基础设施 DR profile。它说明“怎么操作”，不证明生产成熟度；成熟度仍回到 `docs/evidence/`。

### Agent workflow

[`agent-workflow/`](./agent-workflow/) 是给人看的仓库协作协议：ChatGPT、Claude Code、GitHub、Red / Blue、PR 与 post-merge review 怎样协作。机器可执行路由仍在仓库根目录 [`/.agent/`](../../.agent/)；这里不复制 `.agent/system.yaml`、Program 或脚本。

### History

[`history/`](./history/) 保存已经发生的设计讨论和 Red / Blue Archive。历史材料解释“当时为什么这样判断”，但不拥有当前 Architecture Truth；正式接受的结果必须另行写入 Architecture / Module / ADR。

## 维护原则

1. 维护文档只解释流程，不制造第二套事实源。
2. Current / Target / History / Unknown 必须继续分离。
3. 一次 GitHub 修改必须以明确 base SHA 开始，以 PR CI、merge 后 main HEAD 和 post-merge reread 结束。
4. Research、历史 Round、外部平台能力都可能过期；进入正文前必须回到对应 Canonical Owner。

# Project — Zuno 为什么会出现

`docs/project/` 只讲真实项目：背景、历史、团队、个人参与、业务约束，以及哪些事实今天可以相信。这里不负责定义理想系统的完整 Target Architecture，也不把今天的设计反写成历史实现。

## Human View

第一次阅读直接进入 [`project.md`](project.md)。它应当像项目章节，而不是项目档案表：先讲智慧司法与研究工程化背景，再讲 Zuno 为什么出现、我加入时系统已经是什么状态、团队怎样协作、我实际参与了什么、项目怎样经历 Demo / Court-side Testing / Pilot，最后把这些经历留下的工程问题交给总体 Architecture。

项目叙事必须自然包含个人角色，而不是把 Ownership 当成尾部免责声明。需要始终保持三个边界：

- 项目不是 Greenfield 时，不能把已有产品和第一版系统写成个人从零实现；
- 方向级参与不能升级成整个模块或整个平台的个人 Ownership；
- 今天维护 Target Architecture，不能倒推成历史阶段就是整套架构 Owner。

## Machine View

Agent、Reviewer 或简历事实核对先读 [`reference.md`](reference.md)，再按需要进入 [`../governance/project-fact-provenance.md`](../governance/project-fact-provenance.md) 和 [`../evidence/`](../evidence/README.md)。

`reference.md` 只压缩项目 identity、milestone、个人参与、允许/不允许的 Claim 和 Unknown，不重新发明项目历史。

## Project 怎样交给 Architecture

Project 的结尾只需要完成一个交接：

```text
真实项目经历
→ 暴露长期工程问题
→ 哪些问题不能靠简单 RAG / Generic Host 自动解决
→ 进入 architecture/
```

从 `architecture/` 开始讨论的是今天接受的理想 Target。History 与 Target 相互解释，但不相互冒充。

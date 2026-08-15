# Zuno 项目说明

Zuno 是一个来自南京大学软件学院 LIPLAB 智慧司法研究与工程化背景的法律智能 Agent 平台，面向天津法院智慧平台相关场景。它希望把课题组长期积累的法律智能研究成果，整理成可以被 Agent、业务系统和法律专业人员组合使用的能力。

Zuno 是智慧法院相关体系中的一个具体产品，不是整个智慧法院项目。项目方向从一开始就包含法律智能平台、多专业 Agent 和可组合的专业能力；这代表产品意图，不代表历史版本已经完成了所有目标能力，也不代表已经正式生产上线。

## 项目故事

项目一方面来自法院侧的法律智能化需求，另一方面来自 LIPLAB 将智慧司法研究成果继续工程化、产品化的尝试。用户加入时，项目已经有代码和一个比较简单的自研前端，之后围绕 Agent、Memory / Context、Tool Calling 和法律智能能力继续开发，并经历了内部 Demo、客户侧 Demo、法院侧测试和 Pilot Validation。客户曾反馈回答质量还需要提高，但目前没有资料恢复这条反馈对应的具体根因和修复指标。

目前能够确认项目走到过 Pilot Validation，但还没有足够证据把它描述成正式生产系统。参与法院的完整名单、Pilot 的规模和环境，以及历史版本中实际完成了哪些 Agent 和能力组合，仍需要继续补充。

## 这几个文件分别看什么

- [项目背景](./project-background.md)：为什么会有 Zuno、它与 LIPLAB 和天津法院背景的关系，以及项目走到哪一步。
- [团队与开发分工](./team-and-contributions.md)：团队规模、用户何时加入、实际参与过哪些方向，以及哪些个人职责不能扩大描述。
- [开发过程](./development-process.md)：项目如何从已有产品继续开发，经过 Demo、反馈、法院侧测试进入 Pilot。

## 继续阅读

- [总体架构](../architecture/architecture.md)：当前 Target Architecture 为什么这样设计。
- [当前工程证据](../evidence/README.md)：代码、测试和可复现运行到底证明了什么。
- [Red / Blue 历史](../history/red-blue/README.md)：架构选择曾经怎样被质疑和讨论。
- [项目事实来源说明](../governance/project-fact-provenance.md)：给 Reviewer 和 Agent 使用的来源与表述边界。

## 阅读原则

Project 文档讲项目背景、开发经历和目前能够恢复的历史事实；Architecture 文档讲 Target；Evidence 文档证明当前仓库和运行状态。三者各自负责自己的问题，不用当前代码或 Target 设计补写历史。

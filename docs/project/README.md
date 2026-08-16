# Zuno 项目说明

Zuno 是一个来自南京大学软件学院 LIPLAB 智慧司法研究与工程化背景的法律智能 Agent 平台，面向天津法院智慧平台相关场景。它希望把课题组长期积累的法律智能研究成果，整理成可以被 Agent、业务系统和法律专业人员组合使用的能力。

Zuno 是智慧法院相关体系中的一个具体产品，不是整个智慧法院项目。项目方向从一开始就包含法律智能平台、多专业 Agent 和可组合的专业能力；这代表产品意图，不代表历史版本已经完成了所有目标能力，也不代表已经正式生产上线。

## 项目故事

项目一方面来自法院侧的法律智能化需求，另一方面来自 LIPLAB 将智慧司法研究成果继续工程化、产品化的尝试。用户加入时，项目已经有代码和一个比较简单的自研前端，之后围绕 Agent、Memory / Context、Tool Calling 和法律智能能力继续开发，并经历了内部 Demo、客户侧 Demo、法院侧测试和 Pilot Validation。客户曾反馈回答质量还需要提高，但目前没有资料恢复这条反馈对应的具体根因和修复指标。

目前能够确认项目走到过 Pilot Validation，但还没有足够证据把它描述成正式生产系统。参与法院的完整名单、Pilot 的规模和环境，以及历史版本中实际完成了哪些 Agent 和能力组合，仍需要继续补充。

## 先回答四个最重要的问题

### 为什么会有 Zuno？

历史来源见[项目背景](./project-background.md)：法院侧法律智能化需求和 LIPLAB 长期智慧司法研究工程化共同构成项目起点。

### 为什么已经有通用大模型平台，还值得单独做 Zuno？

见[产品定位、立项逻辑与差异化](./product-positioning-and-value.md)。核心不是重复建设 UI、工作流或基础 RAG，而是判断哪些法律业务语义必须由项目自己长期负责：材料版本、知识就绪、正式证据、人工决定、正式工作成果、失效传播、现实副作用恢复和法律质量评测。

这篇文档同时明确：这些是**差异化设计和价值假设**，没有正式 A/B / Benchmark 时不能直接说成“已经全面优于通用平台”。

### 系统为什么最后会长成今天这套九模块架构？

先读[总体架构 Part A](../architecture/architecture.md)，再读[模块架构入口](../modules/README.md)。总体架构讲跨模块工作链，模块 Part A 分别讲每个责任域为什么存在、正常怎样工作、失败怎样恢复。

### 哪些东西今天真的已经实现和证明了？

只看 [`docs/evidence/`](../evidence/README.md)。项目历史、Target 架构和 Current 工程证据是三条不同的事实线，不能互相代替。

## 这几个文件分别看什么

- [项目背景](./project-background.md)：为什么会有 Zuno、它与 LIPLAB 和天津法院背景的关系，以及项目走到哪一步。
- [产品定位、立项逻辑与差异化](./product-positioning-and-value.md)：为什么这个项目值得存在，通用 Agent 宿主已经解决什么，Zuno 还要自己拥有什么，以及这些差异怎样被证明或被淘汰。
- [团队与开发分工](./team-and-contributions.md)：团队规模、用户何时加入、实际参与过哪些方向，以及哪些个人职责不能扩大描述。
- [开发过程](./development-process.md)：项目如何从已有产品继续开发，经过 Demo、反馈、法院侧测试进入 Pilot。
- [项目与架构审查问题地图](./review-question-map.md)：把产品、RAG、Agent、领域状态、工具、安全、评测、Current 实现和个人贡献等高频追问路由到权威文档。

## 按不同目的阅读

### 第一次了解项目

```text
README
→ 项目背景
→ 产品定位与立项逻辑
→ 总体架构 Part A
→ 模块 README
```

### 准备系统设计 / 架构评审

```text
产品定位与立项逻辑
→ 总体架构 Part A / Part B
→ 模块 README
→ 目标模块 Part A
→ 目标模块 Part B / Part C
→ ADR
→ Evidence
```

### 准备技术面试或项目复盘

先读[项目与架构审查问题地图](./review-question-map.md)。它不是答案副本，而是告诉你一个问题应该回到 Project、Architecture、Module 还是 Evidence，避免把 Target、Current 和个人历史贡献混在一起。

### 核对一句话能不能说

读[项目事实来源说明](../governance/project-fact-provenance.md)。里面已经把项目来源、法院背景、团队规模、用户参与方向、Demo / Pilot、Production 状态、通用平台差异化等拆成事实台账，并明确哪些是已确认事实、Target 假设和 Unknown。

## 继续阅读

- [总体架构](../architecture/architecture.md)：当前 Target Architecture 为什么这样设计。
- [九模块架构](../modules/README.md)：九个责任域怎样协作、怎样失败和恢复。
- [当前工程证据](../evidence/README.md)：代码、测试和可复现运行到底证明了什么。
- [有效 ADR](../decisions/README.md)：关键长期架构取舍。
- [Red / Blue 历史](../history/red-blue/README.md)：架构选择曾经怎样被质疑和讨论。
- [项目事实来源说明](../governance/project-fact-provenance.md)：给 Reviewer 和 Agent 使用的来源与表述边界。

## 阅读原则

Project 文档讲项目背景、产品定位、开发经历和目前能够恢复的历史事实；Architecture 文档讲 Target；Modules 文档讲九个责任域的详细 Target 设计；Evidence 文档证明当前仓库和运行状态。

面试和评审中也遵守同一原则：**先说事实，再说设计，再说证据和缺口。** 不用今天的架构补写历史，不用过去的 Pilot 证明今天实现已经完成，也不用“架构完整”推导“Production Ready”。

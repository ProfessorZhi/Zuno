# Zuno Project Knowledge Canonical Set

`docs/project/` 是 Zuno 项目知识的统一正式入口。它把“项目事实上是什么”“整体为什么这样设计”和“技术域具体怎么工作”分开，避免用 Target Architecture 替真实经历回答问题。

## 三层信息架构

| 目录 | 核心问题 | 内容边界 |
|---|---|---|
| [`facts/`](facts/README.md) | What actually happened? | 项目背景、用户、团队、开发过程、实际技术、交付和 Unknown |
| [`architecture/`](architecture/README.md) | Why is the system designed this way? | 产品定位、业务流程、领域模型、总体 Target、全局 Contract 和架构取舍 |
| [`modules/`](modules/README.md) | How exactly does it work? | 11 个技术域的实现级设计、状态、失败、接口和验证边界 |

## 如何按问题读取

```text
“当时到底是什么情况？”
  → facts/

“为什么要做这个系统，为什么不是 WorkBuddy / RAGFlow？”
  → facts/ + architecture/ + ../decisions/ + ../evidence/

“为什么需要 Graph / Memory / Agent？”
  → architecture/ + modules/03 或 modules/05/06

“模型是 API 还是私有部署？GPU 谁负责？”
  → facts/technology-reality.md
     + modules/04-model-gateway.md
     + modules/11-infrastructure.md

“Graph 实际上线了吗？”
  → facts/delivery-and-usage.md + ../status/ + ../evidence/

“这个是你做的吗？”
  → facts/team-and-ownership.md
```

## 与其他 `docs/` 目录的关系

```text
docs/project/
  项目是什么、为什么这样设计、技术如何工作

docs/decisions/
docs/status/
docs/evidence/
docs/governance/
  正式决策、当前状态、可复现证据和仓库治理
```

这些目录不互相复制事实。`facts/` 可以引用 Status/Evidence，但不能把没有证据的上线、用户量、团队人数、模型部署或指标写成事实；`architecture/` 和 `modules/` 也不能反向证明历史发生过。

## 状态标签

项目事实统一区分：

```text
[USER_CONFIRMED]
[REPO_EVIDENCE]
[TARGET_ACCEPTED]
[BLUE_PROPOSAL]
[UNKNOWN]
```

重建置信度与真相状态分开。南京大学、导师、法院、合作方或公开项目资料只能证明周边背景，不能自动证明它们就是 Zuno 的历史来源、客户、用户或部署规模。

红队、蓝队和未来 Skill 的项目输入都从这里开始，再按问题进入 `architecture/`、`modules/`、`decisions/`、`status/` 和 `evidence/`。红蓝过程记录保存在 `project-red-blue/sessions/`，不覆盖本目录的正式事实。

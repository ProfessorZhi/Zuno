# Zuno Project Knowledge Canonical Set

`docs/project/` 是项目知识唯一正式入口。本轮重构不再维护“11 个模块必须永久存在”的前提，也不把历史事实、当前仓库证据和 Target 架构混在同一层。

Active canonical project layers are `docs/project/history/`, `docs/project/status/`, and `docs/project/architecture/`.

## Canonical Questions

| 区域 | 唯一问题 | Owner |
| --- | --- | --- |
| [`docs/project/history/`](history/README.md) | 历史项目发生了什么，哪些仍未知？ | Project History Owner |
| [`docs/project/status/`](status/README.md) | 当前仓库、Target 和 Production Readiness 分别被什么证明？ | Status / Evidence Owner |
| [`docs/project/architecture/`](architecture/README.md) | Product、Domain、Logical Capability、Physical Service/Deployment 如何形成一个跨层闭环？ | Cross-cutting Architecture Owner |

ADR、治理和可复现证据分别由 `docs/decisions/`、`docs/governance/` 和 `docs/evidence/` 负责。`project-reconstruction-lab/` 维护调查、记忆恢复、Red/Blue、候选和会话材料，不拥有正式 Canonical Truth。

## 新入口结构

```text
docs/project/
├─ README.md
├─ history/
│  ├─ README.md
│  ├─ project-background.md
│  ├─ requirements-and-workflows.md
│  ├─ team-and-ownership.md
│  ├─ development-history.md
│  ├─ incidents-and-improvements.md
│  ├─ delivery-and-usage.md
│  └─ technology-history.md
├─ status/
│  ├─ README.md
│  ├─ current-reality.md
│  ├─ target-status.md
│  └─ production-readiness.md
└─ architecture/
   ├─ README.md
   ├─ architecture.md
   ├─ architecture-views.md
   └─ architecture.html
```

最终服务数量、逻辑能力数量和未来专题拆分本轮都不冻结：`FINAL_MODULE_COUNT: NOT_DECIDED`。这里的目录分层回答阅读问题，不把目录、服务、进程、容器、数据库和团队强制一一对应。

## Reading paths

```text
Product reader: history/background → architecture → status/target → evidence
Agent engineer: architecture → decisions/governance → status → code/evidence
Knowledge engineer: history/requirements → architecture → status → eval evidence
Backend/SRE: architecture → status/current → governance → evidence → deployment decisions
Interviewer: history/team → history/development → current-reality → architecture → incidents
```

## 状态模型

- `Current`：代码、Migration、Test、Trace、Eval 或真实运行证据已证明。
- `Target`：已接受的设计方向，不表示实现完成。
- `Hypothesis`：需要 Benchmark、Spike、Security Evidence 或 User Validation。
- `Future`：长期可选，不是当前 Blocker。
- `History`：历史项目事实、UNKNOWN 和被替换的组织方式。

历史文档中的用户确认、部分回忆、仓库局部证据和公开背景必须保留其证据边界。当前仓库不是完整历史项目；论文公开成果也不能自动升级为产品实现。

## 与旧结构的关系

`11 Logical Modules + 1 Architecture` 是上一阶段的 History/Superseded 组织方式。旧事实、专题和模块原稿保存在 [`../history/superseded-document-taxonomy/README.md`](../history/superseded-document-taxonomy/README.md)，只用于审计和考古，不是当前路由。后续若要重建专题或改变架构，必须经过新的 Red/Blue 和明确的 Canonical Decision。

当前入口不改变 Python-only / Microservice 等既有 Owner Target Constraint，也不证明 Native Runtime、Graph、Memory Provider、Multi-Agent 或具体服务数量已经带来收益。相关命题仍需 A/B/C Benchmark、Kill Test、失败恢复和安全证据。

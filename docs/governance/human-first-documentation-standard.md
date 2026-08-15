# Human-first 文档标准

本文约束 Zuno 的文档写作方式，不改变项目事实、Target Architecture、模块边界或历史记录。它把面向人的解释文档与面向工程和 Agent 的证明材料分开，避免所有文档都变成同一种状态表或 Prompt。

## 两类文档

Human-first 文档首先服务新工程师、开发者、架构师、技术负责人、项目合作人员和人类 Reviewer：

- `docs/project/`：项目从哪里来、谁参与、怎样发展；
- `docs/architecture/`：今天认为系统应该怎样组织，以及为什么；
- `docs/modules/`：已冻结责任域内部怎样工作；
- `docs/history/`：设计为什么后来变成今天这样。

Engineering / Agent-first 文档主要服务 Codex、Validator、Reviewer、Operator 和证据核验：

- `docs/evidence/`：代码、测试、Trace、Eval 和运行证据；
- `docs/operations/`：Runbook、部署和恢复操作；
- `docs/governance/`：来源、Owner、Contract、写作规则和 Validator 约束；
- `docs/decisions/`：长期有效的 ADR；
- `.agent/`：路由、自动化和机器上下文。

原则是：Human documents explain，Engineering documents prove，Governance documents constrain。各层通过链接互相查找，不复制另一层的完整内容。

## Human-first 的写法

人打开文档的第一屏应该先知道“这是什么、解决什么问题、现在进行到哪里”。标题后优先使用两三段自然语言，不要让一长串 `status`、编号、Contract 或状态码挡住入口。机器需要的元信息可以放在 HTML comment、front matter 或“当前状态”小节中。

先讲问题和业务场景，再介绍正式术语。例如先说明 Agent 的候选结论为什么不能直接成为案件正式结果，再解释实现层的 Admission、Version 或 Receipt。英文专有名词保留必要的名称，普通概念尽量使用中文，并在第一次出现时给出中英文对照。

表格和 Mermaid 只用来帮助理解关系。表格前要有解释；一张图只表达一个核心关系，优先保留 5–12 个节点。字段级 Contract、完整状态机、错误类型和验证命令应链接到 Governance、Evidence、Decision 或模块工程参考，而不是全部堆在入口文档。

## 四类文档的分工

Project 讲历史和项目事实，不把 Target 设计写成过去已经实现的能力。Architecture 讲总体 Target，不因为 Red Concern 或当前目录存在就自动冻结模块。Modules 只有在模块分解闸门打开后才建立详细正文。History 保留原始问答和演进依据，不成为 Canonical Architecture。

Human-first 不等于营销，不等于删除不确定性，也不等于降低技术严谨性。文档不能添加“行业领先”“生产级”“全面覆盖”等没有证据的宣传；也不能把未知内容改写成确定事实。需要精确来源时链接 Governance，需要当前实现证明时链接 Evidence，需要长期决定时链接 ADR。

## 当前状态与历史保护

`Current`、`Target`、`Future` 和尚未恢复的历史信息必须继续区分。Round Archive 的 Red Question、Blue Answer、Red Review、Reflection 和 Main Judgment 是 append-only 历史，不能为了可读性润色、缩写或重排；可读性通过 README 和摘要解决。

模块 README 可以解释候选边界和开放问题，但不能把候选写成冻结模块。逻辑模块也不自动等于进程、容器、数据库、Worker 或团队；物理部署需要自己的证据门槛。

## 验证原则

Validator 适合检查入口存在、链接有效、目录边界、Raw Archive 未被删除、模块闸门关闭时没有模块正文，以及 Current / Target / History 的路由没有混淆。不要用“每篇必须有几个标题”或“每段不能超过多少字”冒充可读性证明；人类阅读审查仍然是必要步骤。

## Part A / Part B Model

Architecture 和未来的 Module Design 使用同一套设计、两种表达：

```text
ONE DESIGN
TWO REPRESENTATIONS
```

Part A 是完整的人类技术叙事，不是摘要、Executive Abstract 或删掉几个 Contract 的简化规格。Part B 是同一套设计的工程参考，把 Part A 已经解释清楚的内容落实成可以实现、测试、恢复和审查的精确规则。

Project 和 History 不强制拆成 Part A / Part B。Project 本身就是人类项目叙事；History 的 README 和摘要是人类解释层，Raw Q/A/R 是审计记录。这个模型主要适用于总体 Architecture 和未来 Module Design。

### Part A — Human Narrative

Part A 面向新加入项目的工程师、后端和 AI 工程师、架构师、Tech Lead、人类 Reviewer、面试阅读者和合作开发者。读者只看 Part A，也应该能够回答：这个设计为什么存在、解决什么问题、正常情况下如何工作、责任为什么分开、失败后怎么办、为什么这样取舍，以及哪些能力仍可删除、替换或外置。

Part A 的默认顺序是：

```text
实际问题
  → 具体场景
  → 系统行为
  → 设计理由
  → 正式术语
```

先讲问题和场景，再引入状态名、Contract 或边界名。第一屏应该是标题和 2–5 段自然中文；机器 metadata 可以放进 HTML comment、front matter 或弱化的“当前状态”小节，但不能占据主要阅读空间。

关键机制优先通过场景解释。例如，用户询问合同第 8 条的违约责任时，先说明系统如何确认合同范围和权限、等待材料处理完成、找到原文、生成带引用的答案并检查依据；随后再说明这些步骤在工程上对应 Scope、Authorization、Knowledge Readiness、Retrieval 和 Final Gate。

Part A 的失败说明采用“场景 → 判断 → 系统响应 → 为什么”的顺序：模型临时不可用且原计划仍成立时 Retry；Tool Schema 已变化使原计划假设失效时 Replan；外部请求超时且现实世界结果不明时 Reconcile。完整状态枚举放在 Part B。

Part A 的推荐骨架是：

1. Zuno 是什么；
2. 为什么需要它；
3. 什么任务应该保持简单；
4. 一个复杂任务如何完成；
5. 外部副作用任务为什么不同；
6. 系统里有哪些不同种类的状态；
7. 各责任边界如何协作；
8. 任务失败以后怎么办；
9. 安全、审批、人工审核与审计；
10. 哪些能力自己拥有、哪些可以复用；
11. 当前还没有确定什么。

### Part B — Engineering / Agent Reference

Part B 面向 Codex、Agent implementation session、Reviewer、Test author、Maintainer 和 Architecture automation。它可以使用 Contract、Object、State、Enum、Requirement ID、Ownership、Retry Policy、Recovery Rule、Idempotency、Security Gate、Persistence、Schema、Migration 和 Test Evidence，但不重新讲一遍项目故事。

Part B 的推荐骨架是：

1. Scope and Global Invariants；
2. Responsibility / Ownership Map；
3. Cross-boundary Contracts；
4. Domain / Control Objects；
5. State Machines；
6. Retry / Replan / Reconcile；
7. Failure Semantics；
8. Security / Approval / Audit；
9. Recovery and Idempotency；
10. Persistence Boundaries；
11. Observability / Evaluation；
12. Current / Target / Gap；
13. Evidence / Verification；
14. Code / Database / Migration Constraints。

Part B 不能偷偷新增 Part A 没有表达过的重大 Architecture Decision。如果工程规格发现必须增加新的语义边界，应回到 Architecture Discussion、ADR 或 Main Judgment，而不是把决定藏在 Reference 中。

### A → B Semantic Mapping

Part A 解释 Why 和 Behavior，Part B 精确化 State、Contract、Owner、Transition、Failure 和 Recovery；两者必须描述同一个设计。

例如，Part A 可以说：外部系统调用超时后，如果无法确认请求是否执行，系统不能直接重试，因为重复操作可能再次改变外部世界。对应的 Part B 可以写成：

```text
ToolAttempt.state = OUTCOME_UNKNOWN

OUTCOME_UNKNOWN
  → RECONCILING
  → SUCCEEDED
  → NOT_EXECUTED
  → MANUAL_RECONCILIATION

Blind Retry: FORBIDDEN
```

再如，Part A 可以说明 Agent 的分析只是候选结果，经过必要检查和人工审核后才进入正式案件结果；Part B 才定义：

```text
Proposal
  → EligibilityCheck
  → HumanDecision when required
  → Admission
  → AdmissionReceipt
  → Canonical Version
```

如果 A 与 B 无法保持一致，应暂停 Reference 的实现工作，回到架构讨论，而不是选择性相信其中一层。

### Architecture Document Template

总体 Architecture 的正式文档建议使用以下层次：

```text
# Zuno 总体架构

## Part A — Architecture Narrative
  解释问题、场景、流程、边界、失败、取舍和未决事项

## Part B — Engineering / Agent Reference
  记录跨层不变量、Owner、Contract、状态、恢复、安全和证据
```

Part A 必须先于 Part B，且两部分都不能为空。Part B 的跨边界 Contract 只记录真正跨责任域的接口，不把单模块内部 class、helper、private DTO 或数据库字段自动升级为全局 Contract。

### Module Document Template

模块分解闸门打开后，每个 Module 文档统一采用：

```text
# <Module Name>

## Part A — Human Narrative
  1. 为什么需要这个模块
  2. 一个实际业务场景
  3. 它负责什么、不负责什么
  4. 它在整体流程里的位置
  5. 正常情况下怎么工作
  6. 它保存什么状态
  7. 出问题以后怎么办
  8. 它如何与其他责任域协作
  9. 为什么值得成为独立模块
  10. 当前、目标与缺口

## Part B — Engineering / Agent Reference
  Scope / Ownership
  Inputs / Outputs
  Cross-boundary Contracts
  Domain Objects / Data Objects
  State Machines
  Failure / Retry / Replan / Reconcile
  Recovery / Idempotency
  Security / Persistence / Observability
  Provider / Build-Buy Boundary
  Current / Target / Gap
  Tests / Evidence
  Code / Database / Migration Constraints
```

模块文档必须回答为什么它值得成为独立模块，而不是 Library、Provider、Worker、Cross-cutting Concern、Platform Responsibility 或已有模块的一部分。逻辑模块不自动等于进程、Container、Database、Worker 或 Team。

### B3 Cross-boundary Contract Format

B3 只记录真正跨责任边界的 Contract。每个 Contract 至少包含以下字段；某项不适用时写 `N/A` 并说明原因：

```text
### <Contract Name>

Purpose
Producer
Consumer
Authoritative Owner
Input / Output
Versioning
Validation
Failure Semantics
Idempotency / Replay
Security Requirements
Persistence Requirement
Observability Requirement
Evidence
```

示例中的 `AdmissionReceipt`、`ToolAttempt` 或其他名称只是格式示例，不自动成为当前 Architecture 或 Module 的新 Contract。字段级内部实现应留在模块 Reference、Governance 或代码文档中。

### Human Review Checklist

Part A 发布前，Reviewer 应人工回答：

1. 不读 Part B，能否理解这个设计？
2. 第一屏像技术文档，还是像 Prompt / YAML？
3. 是否先出现问题和场景，再出现正式术语？
4. 是否有一段正文被大写状态码连续打断？
5. 是否有一句话塞入五个以上普通英文架构名词？
6. Mermaid 是否真的帮助理解一个关系？
7. 表格是否在替代解释？
8. Failure 是否通过真实场景解释？
9. 是否解释了为什么，而不只是列出必须怎样？
10. 是否把 Target 写成 Current？
11. 是否把 Review Concern 写成 Accepted Decision？
12. 是否必须读 Governance 才能理解正文？

如果第 12 项为“是”，Part A 需要继续重写或补充链接说明。

### Part B Review Checklist

Part B 发布前，Reviewer 应确认：

1. 每个跨边界事实是否有唯一 Owner；
2. Contract 的 Producer / Consumer 是否明确；
3. State transition 是否明确；
4. Retry、Replan、Reconcile 是否区分；
5. Recovery 是否有 durable anchor；
6. Idempotency 是否说明；
7. Security Gate 是否说明；
8. Telemetry 与 durable audit 是否区分；
9. Current / Target 是否有证据边界；
10. Test / Completion Evidence 是否明确；
11. 是否出现 Part A 完全没有表达过的新 Architecture Decision。

若第 11 项为“是”，不能静默提交，必须返回 Architecture Review。

## 维护边界

当前 Round 02 尚未完成时，Writing Standard 只能冻结文档表达规则，不能授权修改 Architecture Semantic、回答 Follow-up、冻结 Module Candidate 或创建 Module 文档。接受的架构语义仍须经过 Main Judgment、独立 Architecture Revision 或 ADR。

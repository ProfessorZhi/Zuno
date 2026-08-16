# Human-first 文档标准

本文约束 Zuno 的文档写作方式，不改变项目事实、Target Architecture（目标架构）、模块边界或历史记录。目标是让人类读者先理解系统为什么这样设计，再让工程人员和 Agent 从同一套设计中读取精确 Contract（契约）、状态、失败和恢复规则。

核心原则只有一句：

```text
ONE DESIGN
TWO REPRESENTATIONS
```

同一套设计有两种表达：Part A 面向人解释“为什么和怎样工作”，Part B 面向实现和审查精确说明“谁拥有、什么状态、怎样失败、怎样恢复”。两部分不能各自发展成两套架构。

## 文档体系的分工

Human-first（人类优先）文档：

- `docs/project/`：项目从哪里来、谁参与、怎样发展；
- `docs/architecture/`：总体 Target 架构今天为什么这样组织；
- `docs/modules/`：九个已冻结责任域内部怎样工作；
- `docs/history/red-blue/`：架构曾被怎样质疑、回答和裁决。

Engineering / Agent-first（工程 / Agent 优先）文档：

- `docs/evidence/`：代码、Migration、Test、Trace、Eval 和运行证据；
- `docs/operations/`：Runbook、部署和恢复操作；
- `docs/governance/`：来源、Ownership、文档规则和验证约束；
- `docs/decisions/`：长期有效的 ADR；
- `.agent/`：路由、自动化、Program 和机器上下文。

原则是：**Human documents explain；Engineering documents prove；Governance documents constrain。** 各层通过链接互相定位，不复制另一层的完整正文。

## Current、Target、Future、History 不能混写

- **Current**：只有代码、Migration、测试、Trace、Eval 或真实运行证据能证明。
- **Target**：已经接受或正在设计的目标语义，不代表实现存在。
- **Future**：长期可选能力，尚不进入当前 Target 基线。
- **History**：被替换的旧设计、Red / Blue 原始记录或考古信息。
- **Unknown / Gap**：当前没有充分证据或尚未闭合的事实与设计问题。

文档写得完整不等于模块实现完成；模块 Design Baseline（设计基线）也不等于 Module Detail Freeze（模块细节冻结）或 Implementation Authorization（实现授权）。Pilot 不等于 Production。

## Part A — Human Narrative（人类技术叙事）

Part A 不是摘要，也不是把 Part B 删除几个字段后的“简化版”。读者只看 Part A，也应该能回答：

- 这个设计解决什么真实问题；
- 一个正常业务场景怎样完成；
- 为什么责任要分开；
- 系统保存什么长期事实，什么只是临时派生；
- 失败以后怎样判断 Retry（重试）、Replan（重规划）、Reconcile（对账）或人工处理；
- 为什么某些复杂能力可以删除、复用或外置；
- 哪些内容仍然只是 Target 或 Gap。

### Part A 的默认叙事顺序

```text
实际问题
→ 具体场景
→ 系统行为
→ 失败场景
→ 设计理由
→ 正式术语
→ 当前 / 目标 / 缺口
```

先解释“用户遇到了什么问题”，再引入状态名、Contract 名或框架名。不要让读者先背术语再反推系统为什么存在。

例如，不要先写：

```text
ReadinessDecision = PARTIAL
```

而应该先说明：100 份材料只处理完 98 份，剩余 2 份正好是完整分析必须使用的关键附件，因此系统不能把结果伪装成覆盖全部材料；随后再说明工程上把这种判断表达为 ReadinessDecision（知识就绪判断）的 PARTIAL / BLOCKED 语义。

### 中文优先规则

Part A 首先是一篇中文技术架构文档，而不是英文架构名词清单。

1. 普通概念如果用中文没有信息损失，直接使用中文。
2. 确实需要保留代码名、论文名、框架名或正式 Contract 名时，第一次出现使用 `English（中文）`。
3. 第一次解释以后，正文优先使用中文；正式标识只在需要和 Part B 对齐时再次出现。
4. 不写一串没有必要的 “scope / state / owner / lifecycle / provider” 来代替中文解释。
5. 标题优先中文；模块正式名称可以保留 `English（中文）` 形式。

例如：`Knowledge Readiness（知识就绪判断）`、`Domain State（领域状态）`、`AdmissionReceipt（正式准入回执）`。如果删除英文后语义完全不受影响，就删除英文。

### 第一屏应该是什么样

标题后优先放 2–5 段自然中文，先回答“它是什么、解决什么问题、现在是什么状态”。机器 metadata 放 HTML comment、front matter 或弱化的状态区，不让 YAML、状态码、Contract 清单挡住正文。

### 场景和失败怎样写

失败采用：

```text
场景
→ 判断发生了什么
→ 系统立即怎么处理
→ 为什么不能用另一种恢复方式
```

例如：

- 模型临时 503，计划仍然正确 → Retry；
- Tool Schema 已变化，原计划假设失效 → Replan；
- 外部 POST 超时，现实世界结果未知 → Reconcile，禁止盲 Retry；
- Domain commit 已成功但 Checkpoint 失败 → 读取 AdmissionReceipt 修复 Runtime；
- 100 份材料只覆盖 40 份 → 缩小 Scope、等待或拒绝，不静默输出完整范围结论。

### 表格和 Mermaid

图和表只是解释工具，不是正文替代品。

- 一张 Mermaid 优先表达一个核心关系，通常 5–12 个节点；
- 表格前先用自然语言解释为什么需要比较；
- 不用一张 40 行 Ownership 表替代对关键边界的解释；
- 状态机太细时放 Part B，Part A 只保留读者理解行为所需的主干。

## Part B — Engineering / Agent Reference（工程 / Agent 参考）

Part B 面向 Codex、Agent implementation session、Reviewer、Test Author、Maintainer 和 Architecture automation。它把 Part A 已解释清楚的语义精确化为 Owner、Contract、状态、失败、恢复、安全、持久化和证据要求。

Part B 可以使用英文正式标识，但不能偷偷增加 Part A 没解释过的重大 Architecture Decision（架构决策）。如果工程规格发现必须增加新的长期语义，应先回到总体架构、模块讨论或 ADR。

### 总体架构 Part B

总体 `docs/architecture/architecture.md` 当前采用跨层 B1–B14 结构，负责全局不变量、九个责任域、真正跨模块 Contract、跨 Store 恢复和总体 Current / Target / Gap。总体架构不冻结单模块内部字段、表和完整 enum。

### 模块 Part B：当前统一结构

九个 `docs/modules/0X-*.md` 当前统一采用以下十四个主题：

```text
B1  Scope / Global Invariants
B2  Responsibility / Ownership
B3  Upstream / Downstream
B4  Authoritative Facts / Core Objects
B5  Cross-boundary Contracts
B6  Normal Flow
B7  State / Lifecycle
B8  Failure Taxonomy
B9  Retry / Replan / Reconcile / Recovery / Idempotency
B10 Security / Approval / Audit
B11 Persistence / Transaction Boundaries
B12 Observability / Evaluation
B13 Current / Target / Gap / Evidence
B14 Code / Database / Migration Constraints
```

这套结构是当前 Module Design Baseline V1（模块设计基线 V1）的正式模板。治理文档、Validator 和模块 README 必须使用同一套编号，不能一处把 Cross-boundary Contracts 写成 B3，另一处又写成 B5。

### B5 Cross-boundary Contract Format

模块中的 B5 只记录真正跨责任边界的 Contract，不把内部 helper、private DTO、ORM class 或数据库字段升级成全局接口。

每个需要详细化的 Contract 至少说明：

```text
Purpose
Producer
Consumer
Authoritative Owner
Input / Output semantic boundary
Versioning
Validation
Failure Semantics
Idempotency / Replay
Security Requirements
Persistence Requirement
Observability Requirement
Evidence
```

某项确实不适用时可以写 `N/A` 并说明原因。字段级 schema 只有在模块详细设计明确需要时才冻结。

### A → B Semantic Mapping

Part A 解释 Why 和 Behavior，Part B 精确化 Owner、State、Contract、Transition、Failure 和 Recovery。两者描述的是同一个设计。

示例一：

Part A：外部系统调用超时后，如果不知道现实世界是否已经执行，就不能直接重试，因为可能重复产生副作用。

Part B：

```text
ToolAttempt = OUTCOME_UNKNOWN
→ Reconcile
→ CONFIRMED / NOT_EXECUTED / MANUAL_RECONCILIATION
Blind Retry: FORBIDDEN
```

示例二：

Part A：检索找到的一段材料只是证据候选，只有经过正式领域准入以后才成为长期业务 Evidence。

Part B：

```text
EvidenceCandidate   owner = 03 Knowledge & Evidence
Evidence            owner = 02 Legal Domain & Work Product
```

示例三：

Part A：一代知识索引已经构建完成，不代表所有任务都能使用它。

Part B：

```text
KnowledgeGeneration lifecycle
!=
task-level ReadinessDecision
```

如果 Part A 和 Part B 无法保持一致，应停止实现或 Reference 深化，先解决 Architecture Gap。

## 模块文档模板

每篇模块文档至少回答以下问题，但不要求 Part A 机械使用相同标题：

```text
# <Module Name>

## Part A — Human Narrative
  为什么需要这个模块
  一个真实业务场景
  正常情况下怎样工作
  它拥有什么长期事实 / 派生事实
  与邻近模块怎样分工
  典型失败怎样处理
  为什么值得独立成为责任域
  当前 / 目标 / 缺口

## Part B — Engineering / Agent Reference
  B1–B14 当前统一结构
```

逻辑模块不自动等于进程、容器、数据库、Worker、Network Service 或 Team。是否拆服务由 ADR-0012 的证据门控制。

## 跨文档一致性规则

整个架构文档体系必须遵守以下优先关系：

1. `docs/architecture/architecture.md`：当前总体 Target 的整合表达；
2. 后续 accepted ADR：对具体长期决策提供约束和显式 supersession；
3. `docs/modules/`：只能细化总体架构和 ADR 已接受的模块内语义；
4. `docs/evidence/`：只证明 Current，不改变 Target；
5. `docs/history/`：解释为什么，不重新拥有当前语义。

如果一个较早 ADR 的宽泛措辞后来被 ADR-0013 / ADR-0014 细化，按后续显式裁决解释；不能同时保留两个互斥 Owner。发现真正无法通过 supersession 解释的冲突时，记录 Architecture Gap，而不是在某篇模块里自行选择一个版本。

同一个事实只允许一个 Authoritative Owner。常见例子：

- DocumentVersion / formal Evidence / Finding / WorkProduct → 02；
- KnowledgeGeneration / ReadinessDecision / EvidenceCandidate / CitationLineage → 03；
- PlanVersion / StepRun / Checkpoint → 04；
- Tool Effect / ReconciliationReceipt → 06；
- Authorization / Approval / Effective Lifecycle Policy → 08；
- Telemetry / Eval projection → 09。

## Human Review Checklist

Part A 发布前，人类 Reviewer 至少检查：

1. 不读 Part B，能否理解这个设计？
2. 第一屏像技术文档，还是像 Prompt / YAML / 状态码说明？
3. 是否先出现问题和场景，再出现正式术语？
4. 普通概念是否优先使用中文？必要英文首次出现是否有中文解释？
5. 是否存在一句话塞入大量英文架构名词却没有增加信息？
6. 是否解释“为什么”，而不只是列“必须怎样”？
7. 正常流程和至少一个关键失败路径是否可理解？
8. Mermaid / 表格是否真的帮助理解，而不是替代正文？
9. 是否把 Target 写成 Current？
10. 是否把 Review Concern 写成 Accepted Decision？
11. 是否必须先读 Governance 才能理解正文？如果是，Part A 还不合格。
12. 与总体架构、相邻模块和术语表是否使用同一 Owner / 状态含义？

可读性仍需要人工审查；Validator 不能靠“每段多少字”“有几个标题”自动证明文档好读。

## Part B Review Checklist

Part B 发布前至少确认：

1. 每个跨边界事实是否有唯一 Owner；
2. Producer / Consumer 是否明确；
3. State / lifecycle 是否和 Part A 行为一致；
4. Retry、Replan、Reconcile 是否区分；
5. Recovery 是否有 durable anchor；
6. Idempotency 是否说明；
7. Security Gate、Approval、HumanDecision 是否没有混为一谈；
8. Telemetry 与 durable audit 是否分离；
9. Persistence / transaction boundary 是否说明；
10. Current / Target / Gap 是否有 Evidence 链接；
11. 是否没有用类名、目录或 Target 文档冒充实现证据；
12. 是否没有因为九个逻辑模块而默认建立九个微服务。

## History 保护

Red / Blue Archive 的 Question、Answer、Review、Reflection 和 Main Judgment 是历史审计记录。为了可读性可以完善 README 和摘要，但不得回头重写原始 Q/A/R 来让今天的架构显得更一致。

当前 Target 的一致性通过总体架构、ADR supersession、模块设计、术语表和 Validator 来维护；History 只保留过程。

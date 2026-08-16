# Human-first 文档标准

本文约束 Zuno 的文档写作方式，不改变项目事实、Target Architecture（目标架构）、九个责任域、ADR 或历史记录。目标是让人类读者先理解系统为什么这样设计，再让工程人员和 Agent 从同一套设计中读取精确 Contract（契约）、状态、失败和恢复规则，并用跨模块一致性视角检查相邻责任域有没有对同一个事实给出两套答案。

核心原则是：

```text
ONE DESIGN
THREE COORDINATED VIEWS
```

对九篇模块文档，同一套设计现在有三个协调视角：Part A 面向人解释“为什么和怎样工作”；Part B 面向实现和审查精确说明“谁拥有、什么状态、怎样失败、怎样恢复”；Part C 不创造第三套架构，只检查这个模块放回九模块整体以后，完成证明、因果版本、新鲜度、取消、晚到结果和恢复顺序是否仍然与相邻模块一致。

总体 `docs/architecture/architecture.md` 继续使用自身的 Part A + Part B 总体架构结构；Part C 是当前九篇模块文档的跨模块一致性层，不要求把总体架构机械改成同样版式。

## 文档体系的分工

Human-first（人类优先）文档：

- `docs/project/`：项目从哪里来、谁参与、怎样发展；
- `docs/architecture/`：总体 Target 架构今天为什么这样组织；
- `docs/modules/`：九个已冻结责任域内部怎样工作，以及放回整体以后怎样保持一致；
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

文档写得完整不等于模块实现完成；Module Design Baseline（模块设计基线）和 Deep Design（深化设计）也不等于 Module Detail Freeze（模块细节冻结）或 Implementation Authorization（实现授权）。Pilot 不等于 Production。

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
3. 第一次解释以后，正文优先使用中文；正式标识只在需要和 Part B / Part C 对齐时再次出现。
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

这套结构仍是 Module Design Baseline V1（模块设计基线 V1）的正式 B1–B14 模板；当前九篇模块已在这套模板上继续达到 Deep Design V2 / Cross-Module Consistency。治理文档、Validator 和模块 README 必须使用同一套编号。

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

## Part C — Cross-Module Consistency（跨模块一致性）

Part C 是九篇模块文档当前新增的**一致性审查视角**。它不拥有新的业务事实，不新增第十个模块，不替代总体架构和 ADR，也不把未接受的新 Contract 偷偷写进模块正文。

它只强制每个模块回答四类跨边界问题：

```text
C1 Completion Proof / Non-proof
   这个模块什么事实才真正证明“完成”？哪些邻近模块 success 明确不能替代？

C2 Causation / Version / Freshness Bindings
   这个事实绑定哪些 run / plan / document / capability / tool / policy / domain 版本？
   哪些变化以后旧结果不得静默复用？

C3 Cancellation / Late Result / Staleness Rules
   cancel 到底停止什么、不撤销什么？
   晚到结果在什么条件下可接受、丢弃、复核或触发 Replan / Reconcile？

C4 Recovery Order / Consistency Tests
   崩溃以后先读哪个 Owner 的 durable fact，再修复哪些 projection？
   哪些 fault-injection / E2E 场景能证明相邻模块没有互相冒充事实？
```

Part C 关注的是**同一个设计在跨模块故障下还能否自洽**。如果 C1–C4 暴露出两个模块都声称拥有同一事实、同一个 `completed` 被解释成两种业务含义、取消语义互相冲突、恢复顺序形成循环依赖，必须记录 Architecture Gap 并回到总体架构 / ADR / 模块设计解决；不能通过改 Validator 字符串掩盖。

### Part C 的几个固定审查原则

1. **Completion proof 必须按 Owner 分层。** `HTTP 200`、`Checkpoint completed`、`Provider success`、`Trace exported` 不能自动升级成相邻模块的更强业务成功。
2. **Cancellation 不是全局回滚。** Run cancel 不撤销已经提交的 Domain transaction、已经确认的现实 Effect 或已经产生的 Model Usage。
3. **Late result 必须重新验收。** 旧 Plan / 旧材料 / 旧权限下计算成功，不代表当前仍然有资格进入新 Plan 或 Domain。
4. **Idempotency namespace 分离。** request、step、capability invocation、effect、admission、delivery、eval run 等使用各自语义身份，通过 causation refs 关联，不能用一个万能 key。
5. **恢复先找 Authoritative Owner Fact。** Checkpoint、cache、trace、dashboard 和 projection 都不能覆盖 AdmissionReceipt、EffectReceipt、AuthorizationDecision 等更强 durable fact。
6. **Correlation 不成为安全或业务权威。** 跨模块只传播最小 opaque identity（不透明身份）；敏感业务字段和 Secret 不为了日志方便进入普通 Trace context / Baggage。

### Part C 不应该写什么

- 不重复整篇 Part B；
- 不新增尚未在总体架构 / ADR 接受的一级对象、模块或状态机；
- 不把测试计划伪装成 Current；
- 不因为一致性检查需要一个字段，就提前冻结数据库 schema；
- 不把“所有模块都带同一个 correlation id”写成分布式事务或全局幂等机制。

## A → B → C Semantic Mapping

Part A 解释 Why 和 Behavior；Part B 精确化 Owner、State、Contract、Transition、Failure 和 Recovery；Part C 检查这些语义跨越模块以后，完成证明、版本、新鲜度、取消和恢复是否仍然成立。三者描述的是同一个设计。

示例一：

Part A：外部系统调用超时后，如果不知道现实世界是否已经执行，就不能直接重试，因为可能重复产生副作用。

Part B：

```text
ToolAttempt = OUTCOME_UNKNOWN
→ Reconcile
→ CONFIRMED / NOT_EXECUTED / MANUAL_RECONCILIATION
Blind Retry: FORBIDDEN
```

Part C：Runtime 即使已经取消旧 Plan，也不能把已发出的未知 Effect 当作“未执行”；06 仍要按 action identity / external correlation 完成 Reconcile，04 再根据 Receipt 修复控制状态。

示例二：

Part A：检索找到的一段材料只是证据候选，只有经过正式领域准入以后才成为长期业务 Evidence。

Part B：

```text
EvidenceCandidate   owner = 03 Knowledge & Evidence
Evidence            owner = 02 Legal Domain & Work Product
```

Part C：旧 KnowledgeGeneration 的 EvidenceCandidate 晚到时，即使检索本身成功，也要重新校验 DocumentVersion / Scope / Security / expected DomainVersion；不能因为旧候选“已经算完”就直接 Formal Admit。

示例三：

Part A：一代知识索引已经构建完成，不代表所有任务都能使用它。

Part B：

```text
KnowledgeGeneration lifecycle
!=
task-level ReadinessDecision
```

Part C：ingestion 被取消或部分 index write 成功时，03 不能把 generation 静默激活；即使 generation 已 serving，SecurityEpoch 或 task requirement 变化后也必须重新计算 Readiness。

如果 Part A 和 Part B 无法保持一致，应停止实现或 Reference 深化，先解决 Architecture Gap；如果 Part B 和 Part C 暴露出跨模块语义冲突，同样先解决 Architecture Gap。

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

## Part C — Cross-Module Consistency
  C1 Completion Proof / Non-proof
  C2 Causation / Version / Freshness Bindings
  C3 Cancellation / Late Result / Staleness Rules
  C4 Recovery Order / Consistency Tests
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
- Capability identity / Eligibility / professional Proposal → 05；
- Tool Effect / ReconciliationReceipt → 06；
- ModelRoutingDecision / ModelCallAttempt / Usage → 07；
- Authorization / Approval / Effective Lifecycle Policy → 08；
- Telemetry / Eval projection → 09；
- Publication / Delivery / Consumer Ack Observation → 01。

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

## Part C Review Checklist

Part C 发布前至少确认：

1. 是否明确本模块真正的 completion proof，以及哪些 success 明确不是证明；
2. 每个关键跨边界结果是否能追到 causation / version / freshness refs；
3. Cancel 是否只停止它有权停止的未来工作，没有伪造全局 rollback；
4. Late result 是否有重新验收条件，而不是一律接受或一律丢弃；
5. 不同模块的 idempotency identity 是否分开；
6. Recovery 是否先读取对应 Owner durable fact，再修复 Runtime / Delivery / Telemetry projection；
7. SecurityEpoch / Authorization / Approval 等安全新鲜度是否在新的受保护操作前重新检查；
8. 现实 Effect 即使来自旧 Plan，也没有因为 branch stale 被错误否认；
9. Trace / correlation 是否只用于定位，没有成为业务成功、安全许可或幂等权威；
10. Consistency Tests 是否至少覆盖一个崩溃窗口、一个版本漂移、一个取消 / 晚到和一个权限变化场景。

## History 保护

Red / Blue Archive 的 Question、Answer、Review、Reflection 和 Main Judgment 是历史审计记录。为了可读性可以完善 README 和摘要，但不得回头重写原始 Q/A/R 来让今天的架构显得更一致。

当前 Target 的一致性通过总体架构、ADR supersession、模块设计、Part C 一致性审查、术语表和 Validator 来维护；History 只保留过程。
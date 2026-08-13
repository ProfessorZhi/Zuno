# ZUNO-RED-BLUE-WORKFLOW-V3.1.1

## 目的

V3.1.1 保留 V3.1 的 100Q、逐题评分、Delta、Canonical Sync 和不可变归档，但把文档质量门和
Canonical Rewrite 规则正式化：
Canonical Owner 文档必须同时解释为什么这样设计，以及工程上怎样实现。

```text
Part-A / Part-B Baseline Audit
→ Narrative / Contract Structural Audit
→ SECTION_REWRITE or FULL_PART_REWRITE
→ Red 100Q
→ Blue Answer
→ Red Score
→ Blue Decision + document_impact
→ Architecture Delta
→ Part-A / Part-B Canonical Sync
→ Quality / Completeness / Governance Verification
→ Immutable Round Archive
→ Review Package
```

## Canonical 文档双层契约

每个 Canonical Owner 文档必须在同一个文件中、且只能包含以下两个顶层正文部分：

- `Part A — Architecture Narrative`：Problem、业务场景、边界、职责、上下游、Happy Path、主要失败、取舍和删除出口；
- `Part B — Detailed Architecture Specification`：Contract、Input/Output、State/Version、Failure、Retry/Recovery、Idempotency、Security、Observability、Ownership、Test/Evidence/Gap。

Part A 解释 WHY/WHAT/BIG PICTURE，Part B 定义 HOW EXACTLY。Required Concerns 不是 Required
Headings；不同专题可以使用不同叙事结构。两部分不能完整复制同一状态机；Part A 可以引用
Part B 的 Contract 名称，但不代替精确状态转换。Part B 之后不得出现第三套旧正文或 Part-A
subsection。

不得创建 `*-human.md`、`*-spec.md` 或第二套 Canonical Architecture。Round、Delta、Question
和过程性 changelog 只能留在 `project-reconstruction-lab/sessions/`、Delta 或 Decision Trace。

## 文档质量门

每个 Canonical Owner 文档独立评分：

| Part A 维度 | 权重 |
|---|---:|
| Problem clarity | 15 |
| Business scenario | 15 |
| Narrative coherence | 15 |
| Boundary clarity | 15 |
| Ownership clarity | 10 |
| Architecture reasoning | 10 |
| Failure story | 10 |
| Alternative / tradeoff | 5 |
| Current/Target separation | 5 |

Part A 必须达到 `85/100`；`90/100` 标记为 STRONG；Part B 必须达到 `85/100`。分数是 Blue/Red/ChatGPT 的文档审查判断，
不是 Runtime 质量或 Production Readiness 证据。Verifier 只检查确定性结构和反模式，不能假装理解
叙事质量。

## Canonical Rewrite Contract

每个 Delta 必须声明 `canonical_sync_mode`：`SECTION_REWRITE`、`FULL_PART_REWRITE`、
`NO_CHANGE` 或 `ESCALATION`。默认禁止 `APPEND`。若改变核心概念、服务边界、Owner、Runtime、
Security、Memory、Graph 或 Eval，至少使用 `SECTION_REWRITE`，通常使用 `FULL_PART_REWRITE`。
同步顺序必须是：Identify Owner → Identify document_impact → Rewrite affected section → Remove
superseded wording → Check narrative coherence → Check Contract consistency。

## Round-003 Decision Contract

每个 Blue Decision 除 V3 字段外必须记录：

```text
document_impact: PART_A | PART_B | BOTH | NONE
part_a_change_required: YES | NO
part_b_change_required: YES | NO
canonical_owner_doc: docs/project/...
```

`BOTH` 是复杂架构决策的默认检查项。若 Decision 改变服务边界、Runtime、Memory、Tool Effect、
Security、GraphRAG、Database Ownership 或 Eval 方法，必须明确说明 Part A 的概念变化和 Part B
的 Contract 变化。

## Sync 与事实边界

Canonical Sync 只能吸收稳定 Target 结论，不把 Round changelog 写回正文，不升级 Current、Fact、
Implemented、Verified、Measured 或 Production Proven。每个 Sync 必须保存 Before/After SHA、
Question/Decision/Delta trace、文档影响和移除的过程性文本。

若出现重大原则、Active ADR、安全信任边界或事实变化，使用 `ADR_ESCALATION` 或 `USER_GATE_ESCALATION`；
不能用 AUTO_APPLY 绕过审查。

## 完成条件

```text
100 Questions + 100 Answers + 100 Scores + 100 Decisions
+ every Decision has document_impact
+ Part-A >= 85 and Part-B >= 85 for every Owner doc
+ no Round changelog in Canonical docs
+ exactly one Part A and one Part B, with Part A before Part B and no legacy body after Part B
+ Delta/Sync trace complete
+ no Current/Fact/Production promotion
```

`DOC_QUALITY_COMPLETE` 不等于 `PRODUCTION_READY`。质量门失败时 Round 必须是
`DOC_QUALITY_REPAIR_REQUIRED`，不能为了完成 100Q 强行关闭。

V3.1.1 的结构归一化可以在不启动新 100Q 的情况下执行；历史 Round Session 保持 immutable，
Round-004 仍须保持 READY_NOT_STARTED，直到归一化后的 Part A 经人工审查。

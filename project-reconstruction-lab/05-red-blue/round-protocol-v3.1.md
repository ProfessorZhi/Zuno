# ZUNO-RED-BLUE-WORKFLOW-V3.1

## 目的

V3.1 保留 V3 的 100Q、逐题评分、Delta、Canonical Sync 和不可变归档，但新增一个文档质量门：
Canonical Owner 文档必须同时解释为什么这样设计，以及工程上怎样实现。

```text
Part-A / Part-B Baseline Audit
→ Part-A Narrative Repair
→ Part-B Contract Repair
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

每个 Canonical Owner 文档必须在同一个文件中包含：

- `Part A — Architecture Narrative`：Problem、业务场景、边界、职责、上下游、Happy Path、主要失败、取舍和删除出口；
- `Part B — Detailed Architecture Specification`：Contract、Input/Output、State/Version、Failure、Retry/Recovery、Idempotency、Security、Observability、Ownership、Test/Evidence/Gap。

Part A 解释 WHY/WHAT/BIG PICTURE，Part B 定义 HOW EXACTLY。两部分不能完整复制同一状态机；
Part A 可以引用 Part B 的 Contract 名称，但不代替精确状态转换。

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

Part A 必须达到 `80/100`；Part B 必须达到 `85/100`。分数是 Blue/Red/ChatGPT 的文档审查判断，
不是 Runtime 质量或 Production Readiness 证据。Verifier 只检查确定性结构和反模式，不能假装理解
叙事质量。

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
+ Part-A >= 80 and Part-B >= 85 for every Owner doc
+ no Round changelog in Canonical docs
+ Delta/Sync trace complete
+ no Current/Fact/Production promotion
```

`DOC_QUALITY_COMPLETE` 不等于 `PRODUCTION_READY`。质量门失败时 Round 必须是
`DOC_QUALITY_REPAIR_REQUIRED`，不能为了完成 100Q 强行关闭。

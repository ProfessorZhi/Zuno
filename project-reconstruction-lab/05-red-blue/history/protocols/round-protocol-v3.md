# ZUNO-RED-BLUE-WORKFLOW-V3

## 目的

V3 把一轮 Red/Blue 从“问答报告”变成可回放的架构变更流水线：

```text
Canonical Snapshot
→ Red 100Q
→ Blue 100 Answers
→ Red 100 Scores
→ Blue 100 Decisions
→ Architecture Delta Consolidation
→ Automatic Canonical Sync
→ Completeness / Governance Verification
→ Immutable Round Archive
→ ChatGPT Review Package
→ Next Round Ready
```

Red、Blue 和独立 Review 的职责必须分开。Red 可以提出攻击和评分；Blue 负责回答、承认弱点
和做最终 Architecture Disposition；ChatGPT Review 不修改本轮历史。

## 固定 Round Contract

- 每轮恰好 `Q001..Q100`；11+1 Review Lens 配额由 `manifest.yaml` 声明并由 verifier 重算。
- 每题必须存在 Question、Blue Answer、Red Score 和 Blue Decision；字段不能用 `N/A` 省略。
- 新颖度至少 70%；回归问题最多 30%，且必须标记 `NOVEL` 或 `REGRESSION`。
- Red Score 为 0–5；Raw、Normalized、Lens Score 只能由 verifier 计算。
- 每个 Architecture Delta 必须回链 Question IDs；每个 AUTO_APPLY Delta 必须有 Canonical Doc 变更。
- Current、事实和 Production 状态不得因 Blue 决定自动升级。

## 11+1 Review Lens

11+1 是审查视角，不是服务数、目录数或旧模块复活许可。Canonical Owner 仍由新 taxonomy
决定；一个 Lens 可以映射多个 Owner 文档，但一个 Contract 只能有一个 Owner 文档。

## Red / Blue / Sync Gate

```text
Red Attack
→ Blue Answer
→ Red Score
→ Blue Decision
→ Delta
→ AUTO_APPLY / ESCALATION
```

`AUTO_APPLY` 只允许澄清、Contract refinement、状态/失败/Owner/Provider 抽象、Eval 或
Reversal refinement，并且不能违反已批准的 Python-only、Microservice Target、Single Controller、
Domain-vs-Runtime State、Security Trust Boundary 或 Provider 可替换原则。

改变这些基本原则、推翻 Active ADR、取消 Microservice、允许 Model 直接提交 Canonical State、
引入重大基础设施或改变安全信任边界，必须进入 `ADR_ESCALATION` 或 `USER_GATE_ESCALATION`，
只能留在 Lab Candidate。

## Necessary Complexity

Red 攻击实现方式、服务数量、数据库数量、Provider、Framework 和部署形态，但不能通过删除
真实的 Legal Domain State、复杂 Agent Run、Evidence、Review、Security、Side Effect、Recovery、
Human Review 或 Court QA 来制造伪简单。Blue 必须证明每项保留复杂度的独立责任、故障域、资源
隔离或可测收益；否则使用 `SIMPLIFY`、`EXTERNALIZE`、`DEFER` 或 `DELETE`。

## Immutability and traceability

Round 文件在 Closure 后视为不可变历史。后续错误使用 Errata/Correction，不无痕改写 Question、
Answer、Score 或 Decision。每次 Canonical Sync 必须保存：Canonical Before SHA、After SHA、
Question IDs、Decision IDs、Delta IDs 和 Changed Canonical Files。

## Round status

```text
COMPLETE
  = 100Q + 100 Answers + 100 Scores + 100 Decisions
  + Delta/Sync/Verification/Review Package
  + no unresolved workflow integrity error
```

`COMPLETE` 不等于 Production Ready。若出现新的 A-P0，下一轮为
`BLOCKED_BY_ARCHITECTURE_REPAIR`；否则下一轮为 `READY_NOT_STARTED`。

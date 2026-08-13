# ZUNO-RED-BLUE-WORKFLOW-V4

## 目的与状态

V4 是 Round-006 以后 Architecture Review 的执行协议。它解决的是评审过程的上下文污染、
线程角色混淆、Artifact 交接和外部验收问题，不是新的产品 Runtime，也不改变历史 Round-001
至 Round-005 的记录。

```text
status: workflow-governance-target
architecture_review: independent-track
implementation_verification: independent-track
round-006: READY_FOR_FRESH_RED_THREAD / NOT_STARTED
chatgpt_verdict: required-before-closure
```

V3/V3.1/V3.1.3 的历史会话保持 immutable。V4 不把历史会话 retroactively 转换为 Fresh
Context 或 Dual Thread。

## 核心不变量

1. 每轮建立两个全新的逻辑 Session：`<round>-RED` 与 `<round>-BLUE`，不得默认复用上轮
   对话记忆。
2. Red 是 Challenger 和 Round Judge，只写当前 Session 的攻击与评分 Artifact，不写
   Canonical Architecture、Facts 或 ADR。
3. Blue 是唯一 Canonical Writer，读取固定 Snapshot、Facts、ADR、Governance 和冻结后的
   Red Questions，才能修改 Canonical。
4. 两个 Thread 只能通过仓库 Artifact 交接，不能复制聊天上下文或 hidden reasoning。
5. Red Questions 冻结后才允许 Blue 防守；Blue 不能改题，Counter Review 不能篡改原题。
6. ChatGPT 是外部 Architecture Auditor。没有用户提供的 Verdict Artifact，Codex/verifier
   不得写 `ACCEPT`、`ACCEPT_WITH_DEBT` 或 `CHATGPT_REVIEW = PASS`。
7. Round 在外部 Verdict 前只能是 `WAITING_FOR_CHATGPT_REVIEW`，不能标记 `CLOSED` 或
   `COMPLETE`。
8. Architecture Review 不等待 Implementation Evidence 完成；Architecture PASS 不升级
   `IMPLEMENTED`、`VERIFIED`、`MEASURED` 或 `PRODUCTION_PROVEN`。
9. Facts、Current/Target/History 和 Architecture State 仍使用各自状态模型，不能互相代签。
10. Canonical Sync 使用 `SECTION_REWRITE`、`FULL_PART_REWRITE`、`NO_CHANGE` 或
    `ESCALATION`，禁止 `APPEND`。

## Round 生命周期

```text
PREPARING
  → RED_ATTACK
  → RED_QUESTIONS_FROZEN
  → BLUE_DEFENSE
  → BLUE_CANONICAL_SYNC
  → RED_COUNTER_REVIEW
  → WAITING_FOR_CHATGPT_REVIEW
  → CHATGPT_REPAIR_REQUIRED / CLOSED / BLOCKED_BY_USER_GATE
```

`CLOSED` 只允许在 Verdict 为 `ACCEPT` 或 `ACCEPT_WITH_DEBT`、用户提供的
`reviewed_final_sha` 与 Blue Final SHA 一致、且两个 Session 都已关闭时出现。

## Round Artifact Contract

每轮目录位于 `project-reconstruction-lab/sessions/<round-id>/`，至少包括：

```text
manifest.yaml
canonical-snapshot.yaml
context-packets/red-context.md
context-packets/blue-context.md
context-packets/red-judge-context.md
red-questions.md
blue-answers.md
blue-decisions.md
architecture-deltas.md
canonical-sync-record.md
red-counter-review.md
scorecard.md
gap-register.md
chatgpt-review-package.md
chatgpt-verdict.md       # 外部用户提供前只能是占位文件
round-report.md
```

`canonical-snapshot.yaml` 至少包含 `round_id`、`base_sha`、Canonical 文件及其 SHA、Fact
Baseline、Active ADR、Governance、Architecture State、Maturity State、Fixed Constraints 和
生成时间。Red 与 Blue 的 Context Packet 必须引用同一个 Snapshot SHA 和 Base SHA。

## Context Packet 边界

- `red-context.md` 只给 Canonical、Facts、ADR、Governance、Current Status、Fixed Constraints
  和 previous-round question index；index 只能有 Question ID、Lens、Topic、Disposition。
- `blue-context.md` 额外给本轮 `red-questions.md`，但不给上轮 Blue/Red reasoning。
- `red-judge-context.md` 只给原始 Snapshot、Red Questions、Blue Answers/Decisions、Delta、
  Canonical Diff、Final Owner Docs 和 Escalations；不得加入 hidden scratchpad。

如果 Fresh Blue 不能仅凭这些材料解释核心设计，必须记为 `CANONICAL_DOCUMENTATION_GAP`，
不能用旧聊天记忆补洞。

## 逐题与评分契约

默认每轮 100 题，仍采用 11+1 Lens；100 是 Review Budget，不是质量 KPI。Red 初评和 Counter
Review 分离：Counter Review 每题记录 `DEFENSE_SCORE` 0–5 与 `POST_SYNC_STATUS`，并同时核对
Blue Answer、Decision 和最终 Canonical。Canonical 没吸收的回答不能得到 Closure 级高分。

允许的 Decision 为：`KEEP`、`CLARIFY`、`REFINE`、`SPLIT`、`MERGE`、`REPLACE`、`DELETE`、
`DEFER`、`FACT_RECOVERY`、`IMPLEMENTATION_GAP`、`MEASUREMENT_GAP`、`EXTERNAL_GAP`、
`ADR_ESCALATION`、`USER_GATE_ESCALATION`。

## 双轨与实现反馈

```text
TRACK A — ARCHITECTURE EVOLUTION
Fresh Red → Frozen Questions → Blue Canonical Sync → Red Counter → ChatGPT Audit

TRACK B — IMPLEMENTATION EVIDENCE
Implementation → Fault Test → Evidence Review → Counter Retest

Track A ↔ Canonical Architecture / Architecture Delta ↔ Track B
```

Track B 的缺失不能阻塞尚未开始的 Architecture Round；Track A 的分数也不能证明实现已完成。
实现发现 Target Contract 不可实现时，必须形成 Architecture Feedback Finding，进入下一轮
Red 的优先攻击项。

## Session 与工作树

Red/Blue Session ID 必须不同且以 Round 绑定。Red 默认只读 checkout 或完全不写 Git；Blue
使用可写 worktree/branch，并拥有唯一 Canonical 写权限。若当前环境没有可靠 Codex Thread
API，只生成 Prompt、Manifest、Context Packet 和人工启动指引，不伪造 Session 已启动。

## 外部验收

Round 的 `chatgpt-review-package.md` 是交给外部 Auditor 的输入，不是验收结果。Verdict
Artifact 必须包含：`round_id`、`reviewed_final_sha`、`verdict`、`blocking_findings`、
`nonblocking_debt`、`required_blue_repairs`、`next_round_focus`、`review_timestamp`，并由
用户提供。有效 Verdict 只有：`ACCEPT`、`ACCEPT_WITH_DEBT`、`BLUE_REPAIR_REQUIRED`、
`ROUND_REPLAY_REQUIRED`、`USER_GATE_REQUIRED`。

## 验证入口

```powershell
python tools/scripts/verify_red_blue_workflow_v4.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4-BOOTSTRAP
python tools/scripts/verify_red_blue_workflow_v4.py --round project-reconstruction-lab/sessions/<round-id>
```

该 verifier 只验证 Artifact Contract 和状态不变量，不启动 Thread、不生成问题、不修改
Canonical，也不代签 ChatGPT。

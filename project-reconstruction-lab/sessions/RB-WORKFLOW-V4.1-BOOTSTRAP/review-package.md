# V4.1 Conceptual Architecture Workflow Bootstrap Review Package

## 基线

```text
BASE_SHA: ad45bd07758fd4a6b3224fa1c90e4987fb4b06e7
FINAL_SHA: RECORDED_IN_FINAL_HANDOFF
workflow: ZUNO-RED-BLUE-WORKFLOW-V4.1
```

## 本轮范围

只改造 Workflow、Governance、Lab、Prompt Templates、Context/Session Contract、Orchestrator
手工操作说明、Verifier、Routing 和 Workflow Tests。没有执行 Round-006，没有修改 Canonical
Architecture 内容、业务 Runtime、UI、Schema、Migration、Dependencies、Production Infra、Facts 或 ADR。

## V4.1 关键语义

- Architecture Round 是 Conceptual Architecture Review，默认不读业务实现代码。
- Canonical Part A 是 Architecture Knowledge Source；Fresh Blue 的冷启动解释失败优先记录
  `CANONICAL_PART_A_GAP`。
- Part A 使用 `CONCEPT_FIRST → TERM_SECOND → CONTRACT_LAST`；Part B 承担精确实现 Contract。
- Blue 不以“代码当前如此”作为架构理由，只能在 Candidate Branch/Worktree 写 Canonical。
- Main Thread 是唯一 Integration Authority；只有 ChatGPT `ACCEPT` 或 `ACCEPT_WITH_DEBT` 才能 merge。
- Human Writing Verifier 只报告 warning，不能自动宣布 Human Writing PASS。

V4.1 Addendum 还要求 Main Thread 每轮生成 `interview-calibration-packet.md`。它从外部面试材料
中只提炼 Deep-Dive Chain、Why/Why-Not、Failure、Counterfactual、Constraint、Tradeoff 和
Reversal 的提问行为；只进入 Red Context，Blue 不读取。Round-006 默认是 12–18 条连续 Chain、
恰好 100Q，并额外记录 `INTERVIEW_DEPTH` 与 `INTERVIEW_EXPLAINABILITY`。

## 双轨状态

| Track | 状态 |
| --- | --- |
| Architecture Evolution | `ROUND-006 READY_FOR_FRESH_RED_THREAD / NOT_STARTED` |
| Implementation Evidence | `Wave-001 WAITING_FOR_RED_COUNTER_RETEST` |

Wave-001 不再阻塞 Architecture Review；Architecture Review 也不把 Target 或分数升级为
Implemented、Verified、Measured 或 Production Proven。

## Round-006 readiness

```text
red_session_id: NOT_CREATED
blue_session_id: NOT_CREATED
candidate_branch: NOT_CREATED
main_merge: NOT_ALLOWED
chatgpt_verdict: NOT_PROVIDED
```

## 外部验收

本包等待独立 ChatGPT External Auditor。没有用户提供的有效 Verdict，不能填写有效
`chatgpt-verdict.md`，当前状态为 `WAITING_FOR_CHATGPT_REVIEW`；不能启动或关闭 Round-006，也不能 merge Candidate。

## 未执行

未执行完整 CI、真实 Codex Thread 创建/关闭 API、Round-006、业务 Runtime、法院 QA、Benchmark、
Fault Injection、HA、Production 或真实 Main Merge。Production Readiness 仍为 `NOT_ESTABLISHED`。

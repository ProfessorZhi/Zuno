# User Feedback — rb-2026-09-15-formal-019

## Carry-forward constraints

- Automated Red/Blue uses `BATCH_DUEL`; the user does not role-play the candidate question by question.
- Formal loop is two committed 100-question / 100-answer waves with Red Wave 2 driven by Blue Wave 1 observable answers.
- Red Final remains blind to Blue architecture notes and canonical Zuno truth.
- Resume must stay in the user's real one-page application register: project context, technical stack, about 4–6 strong technical stories; avoid suspicious headline metrics and avoid turning the resume into an evidence memo.
- Each resume bullet should be independently interviewable and preserve personal ownership boundaries.
- Current architecture is a baseline, not a protected answer. Single Agent, Multi-Agent, Supervisor/Specialist, Subgraph, Generic Host and Native Runtime are candidates that must earn their complexity.
- User's first-party interview records take priority over public interview posts for Red behavior calibration.
- Chat checkpoint should stay concise: give only the artifact produced by the current stage, not a full index of all round files.
- Simulated Resume may be shown in full in chat.
- Red / Blue 100-question or 100-answer batches should show only a small set of representative high-information excerpts in chat, with the complete batch available through one direct GitHub document link.

## Latest execution direction

2026-09-15: user approved the simulated resume by replying `继续`. Resume is frozen for this round and Red Wave 1 may proceed.

The archived PR #236 remains `INVALID_WORKFLOW_CALIBRATION`; its verdict/findings are not formal inputs.

## 2026-10-07 — 收口决定与下一轮主指令

用户批准本轮 improvement ledger，并对三项 deferred 给出决定：

- `IMP-019-07` **DEFERRED** —— direct route 不值得单独吃一条简历 headline，并入 Tool/MCP 的 routing / binding hardening 故事；Red 仍可追 route boundary。
- `IMP-019-08` **APPROVED_FOR_NEXT_ROUND**（Red Skill）—— 问历史时不能因为当时没有今天的 `EffectReceipt` 就把历史实现判成「错误」；应问当时具备什么能力、有什么风险、后来为什么演进。
- `IMP-019-09` **APPROVED_FOR_NEXT_ROUND**（Blue Skill）—— Blue 第一层回答默认 20–60 秒口语；先用 30 秒把事情讲明白再被追到底，比第一答讲五分钟更可信。

`IMP-019-05`：接受「冻结协议 + `MEASUREMENT_BLOCKED`」的处置，**不允许**为了让项目更好看而制造 GraphRAG 数字；协议本身不是 Evidence。

用户同时给出下一阶段的自主治理主指令，已固化为 [`docs/governance/interview-acceptance-standard.md`](../../../governance/interview-acceptance-standard.md)（`main@c7971a7c`，PR #278）。要点：

- 优化「任何强 Claim 都能被追到 History / 个人 Ownership / 代码 / 失败窗口 / Evidence / Unknown」，而不是优化「看起来真实」。
- Red 不再生成 100 个独立知识点，而是约 8–12 条 **Interview Thread**，**跨题保持状态并回钩**前面说过的数字 / 函数 / Ownership / Unknown。
- 新增 **Architecture Interview Acceptance** 循环：closed-book Red 只读 `docs/project/` + `docs/architecture/architecture.md` + resume，先重建 mental model 再盘问。
- Blue Candidate 第一层 20–60 秒；Finding 严格路由，**不允许用 Architecture change 修 Candidate 的表达失败**。
- 下一轮必须从最新 `main` HEAD 固定 `zuno_base_sha` 并做 base-alignment；已在 main 解决的 Finding 不得重新当成新 Architecture Gap。

本轮 verdict 保持不变；上述决定均为 `NEXT_ROUND_ONLY`。


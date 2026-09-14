# Zuno Red / Blue Runtime

`.agent/red-blue/` 是机器运行中心；长期方法、行为证据、工作区和归档入口在 `docs/red-blue/`。

本目录拥有 active Round state、执行协议、Red Interview Skill、Blue Candidate Skill、评价规则和模板。它不拥有 Project History、Target Architecture、Module Truth、Current Evidence 或真实简历正文。

## GitHub-first

正式 Round 中，GitHub 是阶段、batch wave 和可选 live turn 之间唯一耐久交接面：

```text
Round branch HEAD
→ read declared inputs
→ run one stage / wave / turn
→ write artifact + manifest + transcript
→ commit
→ next actor re-read new HEAD
```

聊天上下文和未提交草稿不能直接跨阶段成为正式输入。

## 两个闭环

### Interview Loop

自动 Round 默认：

```text
Frozen Resume
→ Frozen Red Plan
→ RED_WAVE_1 batch
→ BLUE_WAVE_1 batch
→ RED_WAVE_2 based on Blue Wave 1
→ BLUE_WAVE_2 batch
→ Red Evaluation
```

用户不逐题扮演候选人。Wave 2 必须在 Blue Wave 1 commit 后生成；100 问 Pressure Suite 只做离线覆盖，不是 100 题必答卷。

只有用户明确要求真人逐题模拟时才使用：

```text
LIVE_INTERVIEW
→ RED_TURN commit
→ BLUE_TURN commit
→ DYNAMIC_FOLLOWUP
→ ...
```

### Improvement Loop

```text
Red Evaluation
→ Blue Architecture Reflection
→ Resume Builder / Red Skill / Blue Skill / Harness Retrospective
→ Improvement Ledger
→ USER_IMPROVEMENT_REVIEW
→ approved NEXT_ROUND_ONLY changes
→ Next Resume Candidate
→ next Round
```

一个 failure 必须先归因，再决定改哪一层。Red 问得差不能直接变成 Architecture Gap；Blue 有材料但讲不清，也不能直接删 Resume Claim。

## 角色边界

### Resume Builder

读取固定 base SHA 的 canonical docs / Evidence + 简历风格，生成真实可投递的 `01_simulated_resume.md`。

### Red

读取 Frozen Resume、岗位 / JD、pinned `attack-model.md`，以及执行模式允许的既有 observable answers。Red 不读 Zuno docs / source / Evidence。

Batch Duel 中 Wave 1 从 Resume/Plan 选高信息量问题；Wave 2 只在 Blue Wave 1 之后读取其实际答案，再生成 targeted follow-up。

### Blue

读取已经提交的 Red wave/question、此前 observable answers、pinned `defense-model.md` 和固定 base SHA 的允许 canonical sources。

Blue Skill 规定“怎么回答”；canonical sources 规定“什么可以说”。Blue 应区分 Historical Ownership、Current Architecture、Target Design 和 Fundamentals。

### Red Evaluation

只依据 Frozen Resume、实际 Batch/Live Q&A 与 Attack Skill 判断面试表现，不拿 Zuno docs 当隐藏答案。

### Blue Reflection

重新读取 canonical Zuno sources，判断问题到底在 Resume、Narrative、Docs、Architecture、Implementation、Evidence、Ownership、Fundamentals，还是根本不需要 Zuno Change。

### Workflow Retrospective

必须分别审：

```text
Resume Builder
Red Skill
Blue Skill
Harness
```

### Improvement Synthesizer

把所有 finding 收敛进 `09_improvement_ledger.md`，给出唯一 primary owner、拟议改动、风险和下一轮复测条件。

## Skill pinning

每轮开始固定：

```text
attack-model.md version
defense-model.md version
judge.md version
protocol.md version
```

轮末改 Skill 只能 `NEXT_ROUND_ONLY`，不能回头重算当前轮 verdict。

## 隔离模式与执行模式分开

角色隔离：

```text
CHATGPT_AUTO -> LOGICAL_GITHUB_MEDIATED
AGENT_AUTO   -> PHYSICAL_CONTEXT_ISOLATION（仅独立 context 时）
```

面试执行：

```text
BATCH_DUEL      -> 自动 Round 默认
LIVE_INTERVIEW  -> 用户显式要求逐题真人模拟时使用
```

两类维度正交：严格 blind 的 AGENT_AUTO 同样可以运行 Batch Duel。

## Agent topology 的处理

Single Agent、Subgraph、parallel worker、Specialist Agent、Supervisor/Persistent Multi-Agent 都属于可替换 execution topology，不自动拥有新的业务 Authority。

Red 可以攻击“什么时候应该拆 Multi-Agent”；Blue Reflection 只有在现有 Owner/State/Recovery 无法承载时才建议 Architecture Revision。否则优先把 topology 当 measurement-gated Runtime/Application strategy。

## 机器目录

```text
.agent/red-blue/
├── README.md
├── current.md
├── protocol.md
├── attack-model.md
├── defense-model.md
├── judge.md
└── templates/
    ├── round.md
    └── turn.md
```

## Round Artifacts

```text
00_manifest.yaml
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
04_red_evaluation.md
05_blue_architecture_reflection.md
06_workflow_retrospective.md
07_user_feedback.md
08_session_transcript.md
09_improvement_ledger.md
10_next_resume_candidate.md
```

Batch Duel 中 `02_red_questions.md` 收敛 Plan/Pressure Suite/Red Waves，`03_blue_answers.md` 收敛 Blue Waves；Live Interview 中 `03_blue_answers.md` 是 Live Interview Exchange Ledger。

`10_next_resume_candidate.md` 是下一轮候选输入，不得覆盖本轮 Frozen Resume。下一轮从新 main HEAD 重新校验并再次经过 USER_RESUME_REVIEW。

Round 关闭前整个 workspace 归档。完整状态机见 `protocol.md`，评价和归因规则见 `judge.md`。

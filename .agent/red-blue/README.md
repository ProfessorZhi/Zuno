# Zuno Red / Blue Runtime

`.agent/red-blue/` 是机器运行中心；长期方法、行为证据、工作区和归档入口在 `docs/red-blue/`。

本目录拥有 active Round state、执行协议、Red Interview Skill、Blue Candidate Skill、评价规则和模板。它不拥有 Project History、Target Architecture、Module Truth、Current Evidence 或真实简历正文。

## GitHub-first

正式 Round 中，GitHub 是阶段和 live turn 之间唯一耐久交接面：

```text
Round branch HEAD
→ read declared inputs
→ run one stage / one turn
→ write artifact + manifest + transcript
→ commit
→ next actor re-read new HEAD
```

聊天上下文和未提交草稿不能直接跨阶段成为正式输入。

## 两个循环

Red / Blue 运行分成两个闭环。

### Interview Loop

```text
Frozen Resume
→ Frozen Red Plan
→ Red asks one question
→ commit
→ Blue answers
→ commit
→ Red reads answer and follows up
→ ...
→ Red Evaluation
```

Pressure Suite 仍有 100 问，但只做离线 coverage；真实现场必须 answer-driven。

### Improvement Loop

```text
Red Evaluation
→ Blue Architecture Reflection
→ Resume Builder / Red Skill / Blue Skill / Harness Retrospective
→ Improvement Ledger
→ USER_IMPROVEMENT_REVIEW
→ approved changes
→ Next Resume Candidate
→ next Round
```

一个 failure 必须先归因，再决定改哪一层。Red 问得差不能直接变成 Architecture Gap；Blue 有材料但讲不清，也不能直接删 Resume Claim。

## 角色边界

### Resume Builder

读取固定 base SHA 的 canonical docs / Evidence + 简历风格，生成真实可投递的 `01_simulated_resume.md`。

### Red

读取 Frozen Resume、岗位 / JD、pinned `attack-model.md`、已发生的 observable exchanges。Red 不读 Zuno docs / source / Evidence。

### Blue

读取当前已经提交的 Red question、此前 exchanges、pinned `defense-model.md` 和固定 base SHA 的允许 Zuno canonical sources。

Blue Skill 规定“怎么回答”；canonical sources 规定“什么可以说”。

### Red Evaluation

只依据 Frozen Resume、实际 Q/A 与 Attack Skill 判断面试表现，不拿 Zuno docs 当隐藏答案。

### Blue Reflection

重新读取 canonical Zuno sources，判断问题到底在 Resume、Narrative、Docs、Architecture、Implementation、Evidence、Ownership、Fundamentals 还是根本不需要 Zuno Change。

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

每轮开始时固定：

```text
attack-model.md version
defense-model.md version
judge.md version
protocol.md version
```

轮末允许改 Skill，但只能 `NEXT_ROUND_ONLY`，不能回头重算当前轮 verdict。

## 模式

`CHATGPT_AUTO`：`LOGICAL_GITHUB_MEDIATED`，不能证明物理 blind。

`AGENT_AUTO`：角色真正使用独立 context 时可声明 `PHYSICAL_CONTEXT_ISOLATION`。

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

`03_blue_answers.md` 是 Live Interview Exchange Ledger，不再是批量答案。

`10_next_resume_candidate.md` 是下一轮候选输入，不得覆盖本轮 Frozen Resume。下一轮从新 main HEAD 重新校验并再次经过 USER_RESUME_REVIEW。

Round 关闭前整个 workspace 原样归档。完整状态机见 `protocol.md`，评价和归因规则见 `judge.md`。
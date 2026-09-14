# Red / Blue Rounds

本目录保存已经关闭的 `CHATGPT_AUTO` / `AGENT_AUTO` Round。Round 是面试模拟与改进历史，不拥有 Project History、Target Architecture、Current Evidence 或真实 Resume Truth。

## 当前正式格式

从 iterative closed-loop protocol 起，每轮固定为：

```text
<round-id>/
├── 00_manifest.yaml
├── 01_simulated_resume.md
├── 02_red_questions.md
├── 03_blue_answers.md
├── 04_red_evaluation.md
├── 05_blue_architecture_reflection.md
├── 06_workflow_retrospective.md
├── 07_user_feedback.md
├── 08_session_transcript.md
├── 09_improvement_ledger.md
└── 10_next_resume_candidate.md
```

一轮对应一版固定 `zuno_base_sha`、Frozen Resume、pinned Red Skill 和 pinned Blue Skill。轮末修改 Skill / Docs / Architecture 只标记 `NEXT_ROUND_ONLY`，不能回头重写这一轮的 verdict。

各文件分别回答：

- `01`：这一轮面试真正看到的 Frozen Resume；
- `02`：Red 的 Interview Plan + Pressure Suite；
- `03`：真实发生的 Red ↔ Blue Q/A exchanges；
- `04`：只站在面试官视角，候选人是否可信；
- `05`：结合 canonical sources，断点属于 Resume / Narrative / Docs / Architecture / Implementation / Evidence / Ownership / Fundamentals 中哪一类；
- `06`：Resume Builder、Red Skill、Blue Skill、Harness 各自哪里需要改；
- `07`：用户反馈；
- `08`：完整可观察 workflow transition；
- `09`：每个 finding 的 primary owner、拟议改动、风险和下一轮复测条件；
- `10`：吸收已批准改进后的下一轮简历候选稿。

## Round 间关系

下一轮不是在旧目录追加第二批题，而是：

```text
上一轮 archive / merge
→ 新 main HEAD
→ 读取上一轮 09 Improvement Ledger + 10 Next Resume Candidate
→ 重新读取最新 canonical truth
→ 重新 Build / Review / Freeze Resume
→ 新 Round
```

这样可以明确回答“上一轮究竟改了什么，这一轮是在复测什么”。

## 旧格式 Round

旧协议 Round 原样保留，不为了新格式改写历史。缺少 `09` / `10` 不表示历史文件损坏，只表示它们运行在旧工作流下。

特别是 `rb-2026-09-13-zuno-interview-batch-013` 采用了 Red 可提前读取 Zuno 项目材料的旧方法，已被后续 methodology supersede；只能用于研究旧方法的问题，不能作为 resume-first blind Red 的通过证据。

更早的 manual / early automated Round 继续留在 [`../archive/legacy/`](../archive/legacy/README.md)。
# Red / Blue Rounds

本目录保存已经关闭的 `CHATGPT_AUTO` / `AGENT_AUTO` Round。Round 是面试模拟与改进历史，不拥有 Project History、Target Architecture、Current Evidence 或真实 Resume Truth。

## 当前正式格式

正式 BATCH_DUEL Round 保留十一份 core artifact：

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

并额外保存两轮 batch 的关键中间证据：

```text
03_blue_architecture_notes.md
04_red_wave2_review_and_questions.md
04_blue_wave2_answers.md
04_blue_wave2_architecture_notes.md
09_round_report.md
```

一轮对应一版固定 `zuno_base_sha`、Frozen Resume、pinned Red Skill、pinned Blue Skill 和 pinned Judge/Protocol。轮末修改 Skill / Docs / Architecture 只标记 `NEXT_ROUND_ONLY`，不能回头重写这一轮的 verdict。

## 一轮怎样读

推荐按因果顺序：

```text
01 Frozen Resume
→ 02 Red Wave 1：100 题
→ 03 Blue Wave 1：100 答
→ 03 Blue Wave 1 sealed architecture notes
→ 04 Red Wave 2：先评价 Blue 1，再 100 题追杀
→ 04 Blue Wave 2：100 答
→ 04 Blue Wave 2 sealed architecture notes
→ 04 Red Final Evaluation
→ 05 Blue Final Architecture Reflection
→ 06 Workflow Retrospective
→ 09 Improvement Ledger / Round Report
→ 10 Next Resume Candidate
```

`03_blue_architecture_notes.md` 和 `04_blue_wave2_architecture_notes.md` 是对 Red 封存的 Reviewer 记录。它们只能用于最终 Blue Reflection，不能作为 Red 2 或 Red Final 的隐藏答案。

## 各文件回答什么

- `01`：这一轮真正攻击的 Frozen Resume；
- `02`：Red Wave 1 的 100 问；
- `03`：Blue Wave 1 的 100 答；
- `04_red_wave2...`：对 Blue 1 的 blind evaluation + 100 个针对性追问；
- `04_blue_wave2...`：Blue 2 的 100 答；
- `04_red_evaluation`：只站在面试官视角，两轮后候选人是否可信；
- `05`：结合 canonical sources，判断真实系统缺陷；
- `06`：审 Resume Builder、Red Thinking、Blue Candidate、Blue Architecture、Harness；
- `07`：用户反馈；
- `08`：完整可观察 workflow transition；
- `09`：每个 finding 的 primary owner、改动风险和下一轮复测；
- `09_round_report`：给用户看的完整轮末汇报；
- `10`：吸收已批准改进后的下一轮简历候选稿。

## Round 间关系

下一轮不是在旧目录追加第三波题，而是：

```text
上一轮 archive / merge
→ 新 main HEAD
→ 读取上一轮 Improvement Ledger + Next Resume Candidate
→ 重新读取最新 canonical truth
→ 重新 Build / Review / Freeze Resume
→ 新 Round
```

架构如果在上一轮被批准修改，下一轮必须使用修改后的新 main 重新攻击，不能回头用新架构给旧 Round 重新打分。

## INVALID / calibration Round

如果 Harness 本身错误，例如：

- Red / Blue firewall 破坏；
- 批次顺序错误；
- 用户被错误要求逐题扮演 Candidate；
- 同一轮混用互相冲突的协议；

该 Round 应标记：

```text
counts_as_formal_round: false
state: INVALID_CALIBRATION
```

它可以保留为工作流研究材料，但 verdict / Architecture finding / Improvement Ledger 不得进入下一轮正式输入。

`rb-2026-09-14-iterative-018` 即属于这类校准样本，归档说明位于 `docs/red-blue/archive/calibration/`。

## 旧格式 Round

旧协议 Round 原样保留，不为了新格式改写历史。缺少新 batch artifact 不表示历史文件损坏，只表示它们运行在旧工作流下。

特别是 `rb-2026-09-13-zuno-interview-batch-013` 采用了 Red 可提前读取 Zuno 项目材料的旧方法，已被后续 methodology supersede；只能用于研究旧方法的问题，不能作为 resume-first blind Red 的通过证据。

更早的 manual / early automated Round 继续留在 [`../archive/legacy/`](../archive/legacy/README.md)。
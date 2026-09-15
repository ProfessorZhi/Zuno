# Red / Blue Active Workspace

这里保存**正在执行的一轮** Red / Blue 模拟。长期历史进入 [`../rounds/`](../rounds/README.md)。

## Active Round 以 GitHub 为运行容器

正式 Round 从固定 `main` SHA 创建独立 branch：

```text
red-blue/<round-id>
```

并创建 `docs/red-blue/workspace/<round-id>/`。Draft PR 是活动 Round 的 GitHub 入口，`main` 不保存半完成 workspace。

## 默认执行模式：BATCH_DUEL

自动 Round 不要求用户逐题回答。主线是：

```text
Resume
→ Red Wave 1：100 题
→ Blue Wave 1：100 答 + sealed architecture notes
→ Red Wave 2：评价 Blue 1 + 100 targeted follow-ups
→ Blue Wave 2：100 答 + sealed architecture notes
→ Red Final Evaluation
→ Blue Final Architecture Reflection
→ Controller Retrospective
→ Improvement Ledger + Round Report
→ User Improvement Gate
→ approved changes
→ Next Resume Candidate
```

每个 Wave 完成以后，聊天默认只返回该批 GitHub 文档链接。

## Core Artifacts

为了历史兼容，一轮继续保留十一份 core artifact：

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

BATCH_DUEL 另外要求：

```text
03_blue_architecture_notes.md
04_red_wave2_review_and_questions.md
04_blue_wave2_answers.md
04_blue_wave2_architecture_notes.md
09_round_report.md
```

## GitHub 是 stage 交接面

```text
读取 live Round branch HEAD
→ 核对 manifest stage / allowlist
→ 当前 actor 只执行一个 stage
→ 更新 artifact + manifest + transcript
→ commit
→ 下一个 actor 重新读取 HEAD
```

## Resume-first

`01_simulated_resume.md` 先由用户 review，再冻结。Red 只能读取 Frozen Resume、岗位 / JD、pinned Red Skill 和模型通用知识。

Resume bullet 优先表达真实工程问题和技术决策，不以框架名、模块名或漂亮数字代替贡献。

## Red Wave 1

`02_red_questions.md` 保存恰好 100 个问题。

它们从 Frozen Resume 产生，覆盖 Ownership、实现、failure、Evidence、Build/Buy、Fundamentals 和 architecture alternatives。Red 不读 canonical Zuno docs。

## Blue Wave 1

`03_blue_answers.md` 对第一批 100 题逐题回答。

同时生成 `03_blue_architecture_notes.md`，但这个文件对 Red 封存。它只给最终 Blue Architecture Reflection 使用。

## Red Wave 2

`04_red_wave2_review_and_questions.md` 先评价 Blue 1 的实际回答，再生成新的恰好 100 个 targeted follow-ups。

Red 2 只能看到：Resume、Red 1、Blue 1 answers、Attack Skill。它看不到 `03_blue_architecture_notes.md`。

## Blue Wave 2

`04_blue_wave2_answers.md` 对 Red 2 的 100 题逐题回答。

Candidate answer generation 不读取 Wave 1 architecture notes。回答结束后另外生成 `04_blue_wave2_architecture_notes.md`。

## Red Final / Blue Final

`04_red_evaluation.md` 继续 blind，只根据两轮可观察 Q/A 评价候选人。

`05_blue_architecture_reflection.md` 才读取 canonical sources 与两次 sealed notes，判断真实缺陷属于 Resume、Narrative、Docs、Architecture、Implementation、Evidence、Ownership、Fundamentals 还是 No Change。

## Workflow Retrospective

`06_workflow_retrospective.md` 必须审：

```text
Resume Builder
Red Thinking Framework
Blue Candidate Framework
Blue Architecture Framework
Harness
```

不能只审候选人，也不能只审当前架构。

## Round Report 与 Improvement Ledger

`09_improvement_ledger.md` 为每条 finding 指定 primary owner。

`09_round_report.md` 面向用户解释：Red 1 打了什么、Blue 1 暴露什么、Red 2 怎么追、Blue 2 是否顶住、真正架构缺陷是什么、Red/Blue/Harness 自身哪里有问题、下一轮要怎么改。

用户批准前不能因为一次模拟信号直接修改 canonical Zuno Truth。

## NEXT_ROUND_ONLY

批准的 Skill / Harness / Docs / Architecture 变更可以在 Round branch 后半段落地，但只对下一轮生效。本轮 Frozen Resume、pinned Skill 和 Evaluation 不回头改写。

## 下一版简历

完成批准的改进并验证后，Resume Builder 生成 `10_next_resume_candidate.md`。下一轮从新 main HEAD 重新校验，并再次进入 USER_RESUME_REVIEW。

未解决的 Implementation / Evidence / Ownership gap 不能因为写进 candidate 就升级成事实。

## LIVE_INTERVIEW

如果用户明确要求真人逐题模拟，可以切换 `LIVE_INTERVIEW`，继续使用 Red question commit → Blue answer commit → Red follow-up 的真实交替。它不是自动架构校准默认模式。

`CHATGPT_AUTO` 使用 `LOGICAL_GITHUB_MEDIATED`；`AGENT_AUTO` 在角色真正使用独立 context 时可以声明 `PHYSICAL_CONTEXT_ISOLATION`。

## 关闭一轮

完成 Improvement Gate、应用或明确 defer 改进、构建 Next Resume Candidate 后，才把 workspace 原样移动到 `docs/red-blue/rounds/<round-id>/`。Required CI 通过后 merge。

坏问题、弱回答、用户批评、被拒绝的改进和未解决 blocker 都必须保留。
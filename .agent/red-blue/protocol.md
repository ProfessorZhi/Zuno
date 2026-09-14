# Red / Blue Execution Protocol

本协议定义 Zuno Red / Blue 的机器执行规则。长期方法见 `docs/red-blue/README.md`。

## 目标

Red / Blue 不再是一轮问完就归档的面试脚本，而是一条持续收敛的工程闭环：

```text
当前 Zuno Truth
→ 模拟简历
→ Red ↔ Blue 真实交替面试
→ Red 判断候选人表现
→ Blue 对照证据判断项目 / 文档 / 架构缺口
→ 复盘 Red Skill / Blue Skill / Resume Builder / Harness
→ Improvement Ledger 分类并决定改哪里
→ 用户批准可执行改进
→ 应用改进
→ 生成下一轮 Resume Candidate
→ merge
→ 下一轮
```

Round 的目的不是让 Blue “答赢”，而是让 Resume、Red、Blue、文档、架构与证据在多轮压力下逐步变得更可信。

Red / Blue 产物不拥有 Project History、Target Architecture、Module Truth、Current Evidence 或 Personal Ownership。正式事实始终回到 canonical owner。

## GitHub 是运行时状态总线

每个 stage / live turn 都遵守：

```text
read Round branch HEAD
→ verify stage + allowlist
→ read declared inputs
→ run one stage or one turn
→ write artifact + manifest + transcript
→ commit
→ next actor re-read new HEAD
```

GitHub commit 是 commit barrier。聊天摘要、角色临时文本和未提交草稿不能跨阶段成为正式输入。

正式 Round 从固定 `main@zuno_base_sha` 创建独立 branch + Draft PR：

```text
red-blue/<round-id>
docs/red-blue/workspace/<round-id>/
```

当前 Round 的评价只针对它冻结时的 Resume、Skill 与 `zuno_base_sha`。轮末即使修改 Skill / Docs，也不能回头重写本轮 verdict；这些改动只对下一轮生效。

## 生命周期

```text
ROUND_INIT
→ BUILD_SIMULATED_RESUME
→ USER_RESUME_REVIEW
   ├─ APPROVE → FREEZE_RESUME
   ├─ REQUEST_REVISION → RESUME_REVISION → USER_RESUME_REVIEW
   └─ ABORT → CLOSE / SUPERSEDE
→ RED_QUESTIONS
→ USER_RED_REVIEW
   ├─ APPROVE → FREEZE_RED_QUESTIONS
   ├─ REQUEST_REVISION → RED_REVISION → USER_RED_REVIEW
   └─ ABORT → CLOSE / SUPERSEDE
→ LIVE_INTERVIEW
   ├─ RED_TURN → commit question
   ├─ BLUE_TURN → commit answer
   ├─ RED_TURN → commit follow-up
   ├─ BLUE_TURN → commit answer
   └─ ... until stop condition
→ RED_EVALUATION
→ BLUE_ARCHITECTURE_REFLECTION
→ WORKFLOW_RETROSPECTIVE
→ IMPROVEMENT_SYNTHESIS
→ USER_IMPROVEMENT_REVIEW
   ├─ APPROVE / PARTIAL_APPROVE → APPLY_IMPROVEMENTS
   ├─ REQUEST_REVISION → IMPROVEMENT_REVISION
   └─ DEFER → record reason
→ BUILD_NEXT_RESUME_CANDIDATE
→ USER_FEEDBACK_CAPTURE
→ CLOSE_AND_ARCHIVE
→ merge Round PR
→ next Round from new main HEAD
```

默认校准 Round 要求三个用户 Gate：Resume、Red Plan、Improvement。后两个 Gate 解决不同问题：`USER_RED_REVIEW` 防止坏面试器攻击 Blue；`USER_IMPROVEMENT_REVIEW` 防止一次面试误判直接改坏 canonical docs / Skill。

## Resume Builder

Resume Builder 从固定 base SHA 读取 Project、Architecture、Modules、Evidence、selected provenance 和用户简历风格，生成 `01_simulated_resume.md`。

模拟简历必须像真实投递材料，不像 Evidence memo。默认 1 行项目简介、1 行技术栈、约 4–6 条高价值贡献。数量不是硬目标；优先保留能表达真实工程矛盾、个人动作、技术决策和可信结果的 bullet。

一条高质量 bullet 更接近：

```text
真实问题 → 本人动作 / 技术决策 → 机制 → 可验证结果
```

事实边界仍强制：Pilot ≠ Production；团队工作 ≠ Personal Ownership；Target ≠ Current；small smoke ≠ formal benchmark。

当用户修改冻结 Resume 时，基于旧 Resume 的 Red Plan 自动 `INVALIDATED_BY_RESUME_CHANGE`。

## Red Plan 与 PRESSURE_SUITE

Red 正式输入只有：

```text
frozen 01_simulated_resume.md
target role / JD / stage
pinned .agent/red-blue/attack-model.md
model general knowledge
```

Red 不读取 Zuno docs / source / Evidence / Blue hidden answer key。

`02_red_questions.md` 保存 Interview Threads、6–10 个 Spoken Seeds、Follow-up Policy、Branch Examples 和 100-question `PRESSURE_SUITE`。Pressure Suite 只做离线覆盖，不是现场脚本。

## LIVE_INTERVIEW：真正 Red → Blue → Red → Blue

现场面试禁止批量预生成后续问题。

### RED_TURN

Red 每个 turn 读取：

```text
frozen Resume
frozen Red Plan
pinned attack-model.md
03_blue_answers.md 中已发生的 observable exchanges
当前时间 / thread state
```

Red 不能读取 Zuno canonical docs。它根据 Blue 上一答里的一个高信息增益 handle，生成 **一个主要意图** 的下一个问题。

Red question 先提交，Blue 才允许回答。

### BLUE_TURN

Blue 每个 turn 读取：

```text
frozen Resume
当前已经提交的 interviewer question
此前 observable exchanges
pinned defense-model.md
manifest 固定允许的 Zuno canonical docs / Evidence @ zuno_base_sha
```

Blue 不读取未来 Red question、Red Evaluation 或本轮尚未产生的 retrospective。

Blue 回答提交以后，下一次 Red 必须重新读取新的 branch HEAD。

`03_blue_answers.md` 因此是 **Live Interview Exchange Ledger**，按顺序保存真正发生的 Q/A，而不是一次性批量作答文件。

### Stop condition

Red 可以在以下任一条件结束 Live Interview：

- time budget 用尽；
- 已获得足够 hire/no-hire signal；
- 当前 thread 信息增益耗尽且剩余时间不足；
- Kill Switch 已证明关键 Claim 无法建立；
- 预设的最小有效 thread 数已经完成。

结束原因要写入 exchange ledger / transcript。

## Blue Candidate Skill

Blue 回答行为由固定版本 `.agent/red-blue/defense-model.md` 约束。它负责“怎么像真实候选人回答”，canonical docs / Evidence 负责“什么事实可以说”。

Blue Skill 与 Red Skill 一样必须在 Round Init pin version。本轮末修改 Skill，只影响下一轮。

## Red Evaluation

Live Interview 结束后，Red Evaluation 读取冻结 Resume、Red Plan、实际 Q/A 和 pinned attack-model，不读取 Zuno docs。

它判断：候选人是否可信、Ownership 是否成立、实现是否足够深、Failure / Build-Buy / Evidence / Fundamentals 是否经得住追问，以及哪些 Resume Claim 值得保留。

Red Evaluation 可以说“作为面试官我不信”，不能宣布 Zuno Architecture Truth。

## Blue Architecture Reflection

Blue Reflection 再把 Red 信号放回 canonical Zuno sources，区分：

```text
SIMULATED_RESUME_GAP
NARRATIVE_GAP
DOC_GAP
ARCHITECTURE_GAP
IMPLEMENTATION_GAP
EVIDENCE_GAP
OWNERSHIP_GAP
FUNDAMENTAL_GAP
NO_ZUNO_CHANGE
```

只有 Owner、Authority、State、Contract、Recovery、Security 或 Build/Buy 因果本身不成立时，才建议 Architecture Revision。

## Workflow Retrospective：同时审 Red 和 Blue

`06_workflow_retrospective.md` 必须分别评价：

### Resume Builder

- 是否选到了真正有技术含量的问题，而不是功能清单；
- 是否过度包装数字；
- 是否把个人贡献压得过弱或写得过强。

### Red Skill

- Seed 是否自然；
- Follow-up 是否真的从上一答产生；
- 是否追到实现 / failure / evidence；
- 是否过早使用隐藏答案视角；
- 是否像 Reviewer checklist 或 AI 原子化提问。

### Blue Skill

- 是否先直接回答再展开；
- Ownership 是否清楚；
- 是否会把技术名词还原成工程问题与机制；
- 是否会诚实处理 Unknown / small-sample / Target-only；
- 是否回答太像文档、过度引用或过度防御；
- 面试官继续追一层时，是否还有真实实现深度。

### Harness

- commit handoff 是否正确；
- Red / Blue firewall 是否被破坏；
- turn 粒度是否真实；
- stage / gate 是否产生无意义摩擦；
- Pressure Suite 是否被误当现场脚本。

Workflow Retrospective 不能修改本轮答案或本轮 verdict。

## Improvement Ledger：每个问题必须有 Owner

`09_improvement_ledger.md` 汇总 Red Evaluation、Blue Reflection、Workflow Retrospective 和用户反馈。每条 finding 只能路由到一个 primary class，必要时附 secondary class：

```text
RESUME_GAP
RED_SKILL_GAP
BLUE_SKILL_GAP
HARNESS_GAP
NARRATIVE_GAP
DOC_GAP
ARCHITECTURE_GAP
IMPLEMENTATION_GAP
EVIDENCE_GAP
OWNERSHIP_GAP
FUNDAMENTAL_GAP
NO_CHANGE
```

每条至少记录：

```text
signal
root_cause
primary_class
owner
proposed_change
evidence_needed
risk_if_changed
status: APPLY | DEFER | REJECT | NEEDS_OWNER_DECISION
next_round_retest
```

归因原则：

- Red 问得差 → 优先 `RED_SKILL_GAP / HARNESS_GAP`，不能怪 Architecture；
- Blue 明明有材料却讲不清 → `BLUE_SKILL_GAP / NARRATIVE_GAP`；
- Resume 本身 claim 不好 → `RESUME_GAP`；
- Docs 缺少已存在机制解释 → `DOC_GAP`；
- Target 设计本身不成立 → `ARCHITECTURE_GAP`；
- 没实现 → `IMPLEMENTATION_GAP`；
- 有实现但没有 test / trace / benchmark → `EVIDENCE_GAP`；
- 个人归属不清 → `OWNERSHIP_GAP`；
- 纯基础薄弱 → `FUNDAMENTAL_GAP`。

## USER_IMPROVEMENT_REVIEW 与 Apply

Improvement Ledger 完成后，默认进入用户 Gate。只有用户批准的条目才能在 Round 后半段修改 Skill、Harness、Docs 或 Architecture。

Architecture 修改仍必须满足 Architecture Owner / ADR 规则；Implementation 工作不能因为面试暴露而伪装成文档修复。

应用阶段可以修改当前 Round branch，但有两个硬约束：

1. 本轮 evaluation / reflection 永远引用原 `zuno_base_sha` 和 pinned Skill versions；
2. post-round changes 标记 `NEXT_ROUND_ONLY`，不得回头重新计算本轮 PASS/FAIL。

## 下一版简历与下一轮

批准的改进应用后，Resume Builder 从 **post-improvement branch HEAD** 重新构建 `10_next_resume_candidate.md`。

它只能使用已经成立的事实：

- Resume wording fix 可以立即进入；
- 已批准并落地的 Docs / Skill 改进可以影响下一轮表达 / 行为；
- 未实现的 Architecture Target 不能写成 Current；
- IMPLEMENTATION / EVIDENCE / OWNERSHIP 缺口未解决时，相关 Resume Claim 必须保持原边界或降级。

Round merge 到 main 后，下一 Round 从新的 exact `main` HEAD 开始，并把 `10_next_resume_candidate.md` 作为 Resume Builder 的候选输入之一重新校验。下一 Round 仍需要 `USER_RESUME_REVIEW`；不能因为上一轮已经生成 candidate 就跳过事实复核。

## Context Firewall

### CHATGPT_AUTO

```text
firewall_strength: LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

同一 ChatGPT 对话不能证明物理遗忘。严格 blind Red 验收必须用 `AGENT_AUTO`。

### AGENT_AUTO

```text
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

## 固定 Round Artifacts

```text
00_manifest.yaml
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md              # live Q/A exchange ledger
04_red_evaluation.md
05_blue_architecture_reflection.md
06_workflow_retrospective.md    # Resume + Red Skill + Blue Skill + Harness
07_user_feedback.md
08_session_transcript.md
09_improvement_ledger.md
10_next_resume_candidate.md
```

所有 artifact 只保存 observable role I/O、GitHub refs、classification、decision 和用户 intervention；不保存或伪造模型私有 chain-of-thought。
# Red / Blue Execution Protocol

本协议定义 Zuno Red / Blue 的机器执行规则。长期方法见 `docs/red-blue/README.md`。

## 目标

正式 Round 先把当前 Zuno docs / Evidence 压缩成一份模拟简历，再让 Red 从简历 Claim 出发提问。Red / Blue 产生面试压力、回答、评价和改进建议，不拥有 Project、Architecture、Module 或 Current Truth。

## GitHub 是运行时状态总线

GitHub 不是事后日志。阶段之间只通过已经提交的 Round artifact 交接：

```text
read Round branch HEAD
→ verify stage + allowlist
→ read declared inputs
→ run one stage
→ write artifact + manifest + transcript
→ commit
→ next stage re-read new HEAD
```

每个箭头都是 `commit barrier`。聊天摘要、角色临时文本和未提交草稿不能跨阶段成为正式输入。

### Round branch / PR

正式 Round 从固定 `main@zuno_base_sha` 创建：

```text
red-blue/<round-id>
docs/red-blue/workspace/<round-id>/
Draft PR -> main
```

Round 期间所有阶段提交进入同一个 branch / Draft PR。关闭前把 workspace 原样移入 `docs/red-blue/rounds/<round-id>/`，恢复 `.agent/red-blue/current.md` 为 no-active，CI 通过后 merge，再重新读取 exact `main` HEAD。

### Stage transaction

每阶段至少持久化：

```text
本阶段 artifact
00_manifest.yaml 的 stage state
08_session_transcript.md 的 observable I/O / transition / GitHub refs
```

manifest 使用 `last_consumed_head_sha` 表示最近完成阶段实际读取的输入 HEAD；当前 branch HEAD 必须从 GitHub ref 实时读取，不再用容易误解的 `stage_head_sha` 同时表达输入与输出。

Round Init 必须把启动前已经知道、且会影响本轮的问题质量或流程约束写进 `07_user_feedback.md`。Round 运行中新的用户反馈也必须先写入 `07_user_feedback.md` 与 transcript 并提交，再影响后续阶段。

## 生命周期

```text
ROUND_INIT
→ BUILD_SIMULATED_RESUME
→ FREEZE_RESUME
→ RED_QUESTIONS
→ USER_RED_REVIEW
   ├─ APPROVE → FREEZE_RED_QUESTIONS → BLUE_ANSWERS
   ├─ REQUEST_REVISION → RED_REVISION → USER_RED_REVIEW
   └─ ABORT → CLOSE / SUPERSEDE
→ RED_EVALUATION
→ BLUE_ARCHITECTURE_REFLECTION
→ WORKFLOW_RETROSPECTIVE
→ USER_FEEDBACK_CAPTURE
→ CLOSE_AND_ARCHIVE
```

`USER_RED_REVIEW` 是可配置门。工作流校准期默认 `REQUIRED`；成熟自动回归可以显式设为 `OPTIONAL` 或 `SKIP`。只要本轮 manifest 声明 `REQUIRED`，Blue 在 Red questions 被用户批准并冻结前不得执行。

Red 修订不创建第二批题单。`02_red_questions.md` 在同一个 Round 内更新，旧版本由 Git commit history 保留；每次修订都必须重新提交并回到 `USER_RED_REVIEW`。

## Question Suite 与真实面试路径

默认总压力集仍为 `100` 问，但不把 100 问伪装成一场 45–60 分钟面试会逐题问完。

默认结构：

```text
question_count: 100
primary_path_target: 30
reserve_target: 70
```

- `PRIMARY_PATH`：默认 25–40 问，构成真实一面主路径。
- `RESERVE_FOLLOWUP`：只有主路径答案触发时才进入。
- `KILL_SWITCH`：当某个高风险 Claim 的 Ownership / mechanism 无法成立时，停止在该 Claim 上继续堆同义深挖，记录 credibility break 后切到下一条 Claim。

真实执行优先走 Primary Path；Reserve 用于条件追问、复测和压力覆盖。

## Resume Builder

Resume Builder 从固定 `zuno_base_sha` 读取 Project、Architecture、Modules、Evidence、选定 provenance 和已有简历风格，生成并提交 `01_simulated_resume.md`。

它必须区分实现成果、Target 架构设计、团队研究背景与个人 Ownership；Pilot 不写成 Production，没有测量不制造数字。

## Red — Interviewer

Red 的正式输入：

```text
01_simulated_resume.md
00_manifest.yaml 中的目标岗位 / JD / 面试轮次
.agent/red-blue/attack-model.md
模型通用知识
```

### 禁止输入

Red 不把以下内容作为正式出题依据：

```text
docs/project/
docs/architecture/
docs/modules/
docs/evidence/
docs/decisions/
docs/governance/
Zuno 源码 / PR / commit diff
resume build notes / source trace
prior Blue answers
```

Red 开始前必须从 Round branch HEAD 重新读取允许输入。`02_red_questions.md` 不能直接消费 Resume Builder 在聊天中形成但未提交的中间信息。

问题围绕最高风险的 3–6 条 Resume Claim 建立攻击链，并执行 `.agent/red-blue/attack-model.md` 中的 Claim 取证、Ownership、Build / Buy / Extend / Defer、实现细节、故障反例、Evidence、基础下钻和删除条件。

对于简历中直接写出算法名、函数名、Schema、test artifact 或精确指标的 Claim，Primary Path 必须尽早安排 Ownership / mechanism probe，不能先花大量问题讨论宏观架构。

## USER_RED_REVIEW

Red 提交 `02_red_questions.md` 后，如果 `red_review_gate=REQUIRED`，Controller 必须进入等待用户审查状态，并把 Red 第一轮产物交给用户。

用户结果只允许：

```text
APPROVE
REQUEST_REVISION
ABORT
```

`REQUEST_REVISION` 时，把用户反馈先提交到 `07_user_feedback.md` / transcript。Red Revision 的正式输入只能是原 Red allowlist + 当前 `02_red_questions.md` + 与 Red 质量直接相关的已提交用户反馈；仍不得读取 Zuno docs。

只有 `APPROVE` 后，manifest 才把 `red_questions_status` 改成 `FROZEN`，Blue 才能开始。

## Blue — Candidate / Documentation Reader

`02_red_questions.md` 已冻结后，Blue 从新的 GitHub HEAD 读取：

```text
01_simulated_resume.md
02_red_questions.md
manifest 固定的 Zuno source refs / allowlist
```

再按 `zuno_base_sha` 读取允许的 canonical docs / Evidence。Blue 在生成 `03_blue_answers.md` 前不读取 Red Evaluation。

回答必须区分 History / Current / Target / Unknown / Personal Ownership / Team / Framework Capability。没有来源时明确说未证明。

## Red Evaluation

`03_blue_answers.md` 提交后，Red Evaluation 从 GitHub HEAD 读取冻结简历、冻结题单、Blue answers 与 Attack Skill。它不把 Zuno docs 作为正式评价输入。

它评价回答是否像真正做过、实现是否具体、Ownership 是否可信、替代方案 / 故障 / 基础是否经得住追问，以及简历 Claim 是否值得保留。输出 `04_red_evaluation.md`。

## Blue Architecture Reflection

`04_red_evaluation.md` 提交后，Blue Reflection 重新结合固定 Zuno docs，把断点分类为：

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

只有设计因果、Owner、Authority、State、Recovery、Security、Contract 或 Build/Buy 本身不成立时，才建议 Architecture Revision。

## Workflow Retrospective

`WORKFLOW_RETROSPECTIVE` 读取全轮已提交 artifact、Red Skill 和 `07_user_feedback.md`，专门审判 Red 与 Harness：问题有没有技术含量、是否重复、Primary Path 是否像真实面试、Kill Switch 是否有效、是否攻击重复造轮子、是否自然下钻基础，以及用户为什么认为问题好或差。

## Context Firewall

两种模式都必须经过 GitHub `commit → re-read`，但保证不同。

### CHATGPT_AUTO

```text
firewall_strength: LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

同一个 ChatGPT 对话无法证明物理遗忘。如果某轮要把 **blind Red** 当作正式验收结论，必须用 `AGENT_AUTO` 重跑。

### AGENT_AUTO

```text
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

独立 context 负责信息隔离；GitHub state bus 负责过程边界。两者不能互相替代。

## 固定 Round 文件

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
```

所有模式只保存 observable role I/O、GitHub ref / commit、Controller transition 和 user intervention；不要求也不伪造模型私有 chain-of-thought。

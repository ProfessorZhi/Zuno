# Red / Blue Execution Protocol

本协议定义 Zuno Red / Blue 的机器执行规则。长期方法见 `docs/red-blue/README.md`。

## 目标

正式 Round 先把当前 Zuno docs / Evidence 压缩成一份模拟简历，再让 Red 从简历 Claim 出发提问。Red / Blue 产生的是面试压力、回答、评价和改进建议，不拥有 Project、Architecture、Module 或 Current Truth。

## GitHub 是运行时状态总线

GitHub 不是 Round 结束后的旁路日志。阶段之间只通过已经提交的 Round artifact 交接：

```text
read Round branch HEAD
→ verify current stage + allowlist
→ read declared inputs
→ run one stage
→ write artifact + manifest state + 08_session_transcript.md
→ commit
→ next stage re-read the new HEAD
```

每个箭头都是 `commit barrier`。聊天摘要、角色临时文本和未提交草稿都不能直接跨阶段成为输入。

### Round branch / PR

正式 Round 从固定 `main@zuno_base_sha` 创建：

```text
red-blue/<round-id>
docs/red-blue/workspace/<round-id>/
Draft PR -> main
```

Round 期间所有阶段提交进入同一个 branch / Draft PR。关闭前把 workspace 原样移入 `docs/red-blue/rounds/<round-id>/`，恢复 `.agent/red-blue/current.md` 为 no-active，CI 通过后合并并重新读取 exact `main` HEAD。

### Stage transaction

每阶段至少持久化：

```text
本阶段 artifact
00_manifest.yaml 的 stage state
08_session_transcript.md 的 observable I/O / transition / GitHub ref
```

会影响当前 Round 的用户反馈先写入 `07_user_feedback.md` 和 `08_session_transcript.md`，提交以后再继续。

## 生命周期

```text
ROUND_INIT
→ BUILD_SIMULATED_RESUME
→ FREEZE_RESUME
→ RED_QUESTIONS
→ BLUE_ANSWERS
→ RED_EVALUATION
→ BLUE_ARCHITECTURE_REFLECTION
→ WORKFLOW_RETROSPECTIVE
→ USER_FEEDBACK_CAPTURE
→ CLOSE_AND_ARCHIVE
```

默认一轮一批 `100` 问。修复后复测必须创建新 Round 和新模拟简历。

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

Red 阶段开始前必须从 Round branch HEAD 重新读取允许输入。`02_red_questions.md` 不能直接消费 Resume Builder 在聊天中形成但未提交的中间信息。

问题围绕最高风险的 3–6 条 Resume Claim 建立攻击链，执行 `.agent/red-blue/attack-model.md` 中的精品思维、全链路追踪、Ownership、Build / Buy / Extend / Defer、故障反例、Evidence 和基础下钻。

## Blue — Candidate / Documentation Reader

`02_red_questions.md` 提交后，Blue 从 GitHub HEAD 读取：

```text
01_simulated_resume.md
02_red_questions.md
manifest 固定的 Zuno source refs / allowlist
```

再按 `zuno_base_sha` 读取允许的 canonical docs / Evidence。Blue 在生成 `03_blue_answers.md` 前不读取 Red Evaluation。

回答必须区分 History / Current / Target / Unknown / Personal Ownership / Team / Framework Capability。没有来源时明确说未证明。

## Red Evaluation

`03_blue_answers.md` 提交后，Red Evaluation 从 GitHub HEAD 读取：

```text
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
.agent/red-blue/attack-model.md
```

它评价回答是否像真正做过、实现是否具体、Ownership 是否可信、替代方案 / 故障 / 基础是否经得住追问，以及简历 Claim 是否值得保留。它不拥有 Architecture Truth。

输出 `04_red_evaluation.md`。

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

输出 `05_blue_architecture_reflection.md`。

## Workflow Retrospective

`WORKFLOW_RETROSPECTIVE` 读取全轮已提交 artifact、Red Skill 和 `07_user_feedback.md`，专门审判 Red 与 Harness：问题有没有技术含量、是否重复、是否真的全链路、是否攻击重复造轮子、是否自然下钻基础，以及用户为什么认为问题好或差。

输出 `06_workflow_retrospective.md`。

## Context Firewall

两种模式都必须经过 GitHub `commit → re-read`，但保证不同。

### CHATGPT_AUTO

单个 ChatGPT 对话负责 Controller 和各阶段。它提供：

```text
firewall_strength: LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

GitHub 让阶段状态可审计、可恢复，并禁止直接用未提交聊天状态 handoff；但同一对话无法证明模型已经物理遗忘 Resume Builder 先前看到的 Zuno docs。

如果某轮要把 **blind Red** 当作正式验收结论，必须用 `AGENT_AUTO` 重跑。

### AGENT_AUTO

Resume Builder、Red、Blue、Red Evaluation、Blue Reflection、Workflow Retrospective 使用独立 context，并继续执行完全相同的 GitHub stage transaction：

```text
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

物理 context 隔离负责角色信息边界；GitHub state bus 负责过程边界。两者不能互相替代。

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

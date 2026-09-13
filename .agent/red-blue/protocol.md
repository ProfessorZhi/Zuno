# Red / Blue Execution Protocol

本协议定义 Zuno Red / Blue 的机器执行规则。长期方法见 `docs/red-blue/README.md`。

## 目标

正式 Round 先把当前 Zuno docs / Evidence 压缩成一份**像真实候选人会投出去的模拟简历**，再让 Red 从简历出发模拟真实面试。Red / Blue 产生面试压力、回答、评价和改进建议，不拥有 Project、Architecture、Module 或 Current Truth。

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

每阶段至少持久化本阶段 artifact、`00_manifest.yaml` state 与 `08_session_transcript.md` observable I/O / transition / GitHub refs。

manifest 使用 `last_consumed_head_sha` 表示最近完成阶段实际读取的输入 HEAD；当前 branch HEAD 从 GitHub live ref 获取。

Round Init 必须把启动前已经知道、且会影响本轮的问题质量或流程约束写进 `07_user_feedback.md`。Round 中新的用户反馈也先提交，再影响后续阶段。

## 生命周期

```text
ROUND_INIT
→ BUILD_SIMULATED_RESUME
→ USER_RESUME_REVIEW
   ├─ APPROVE → FREEZE_RESUME → RED_QUESTIONS
   ├─ REQUEST_REVISION → RESUME_REVISION → USER_RESUME_REVIEW
   └─ ABORT → CLOSE / SUPERSEDE
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

工作流校准期默认同时要求 `USER_RESUME_REVIEW` 与 `USER_RED_REVIEW`。模拟简历没过用户检查，Red 不得开始；Red plan 没过用户检查，Blue 不得开始。

## Resume Builder：写简历，不写证据报告

Resume Builder 从固定 `zuno_base_sha` 读取 Project、Architecture、Modules、Evidence、选定 provenance 和用户已有简历风格，生成并提交 `01_simulated_resume.md`。

它必须先服从**真实简历的阅读节奏**，再服从证据完整性：证据边界要保留，但通过精准措辞压缩进简历，而不是把 Evidence memo 原样塞进 bullet。

默认写法：

```text
项目名称 + 时间
1 行项目简介
1 行技术栈
4–5 条核心 bullet
```

每条 bullet 只承载一个主要故事：

```text
问题 / 动作 / 关键技术 / 可证明结果
```

通常控制在目标模板中的 1–2 行。中文项目简历的软目标可参考约 45–90 个字符一条；英文术语、函数名较多时允许更长，但不能出现一条 bullet 像一段技术文档。

### Resume style rules

优先：

- 使用候选人已有真实简历的版式、句长、动词和信息密度作为第一参考；
- 项目开头一句讲场景，不先堆框架名；
- bullet 用动词开头，说明自己做了什么；
- 有真实数字时保留最有区分度的一两个数字；
- 具体技术名只保留会影响筛选或能引出高质量面试的部分；
- 对小样本、Pilot、参与范围等边界，用限定词本身表达，例如“5 条 HotpotQA smoke”“参与”“Pilot Validation”，而不是在 bullet 末尾追加一整句免责声明。

避免：

- `Current / Target / Evidence / Unknown` 这类文档标签进入简历；
- 一条 bullet 同时解释背景、四个算法、三个指标、限制条件和下一步；
- 把 PR 号、内部 Contract 名、对象名当作价值本身；
- 中英文术语连续堆叠到读者必须逐词解码；
- 为了“证据诚实”写出“不能证明……、不扩写为……”这种 Reviewer 语言；
- 为了显得技术深而列出超过实际面试价值的内部实现清单。

事实边界仍然强制：实现成果、Target 架构设计、团队研究背景与个人 Ownership 必须分开；Pilot 不写成 Production，没有测量不制造数字。

## USER_RESUME_REVIEW

当 `resume_review_gate=REQUIRED`，Resume Builder 第一次提交 `01_simulated_resume.md` 后进入用户审查。

用户结果：

```text
APPROVE
REQUEST_REVISION
ABORT
```

人工 Review 重点检查：

- 它像不像真正的一页求职简历，而不是证据摘要；
- 项目简介和 bullet 能不能 10–20 秒扫懂；
- 单条 bullet 有没有超过正常简历的信息负荷；
- 技术关键词是否服务于贡献，而不是堆名词；
- 量化是否真实、必要、可解释；
- Personal Ownership / Pilot / small-sample 等边界是否被自然保留。

`APPROVE` 后才把 `resume_status` 改成 `FROZEN`。Red 只能读取冻结版本。

如果用户要求修改模拟简历，旧版本留在 Git history；修改后必须重新走 `USER_RESUME_REVIEW`。已经基于旧简历生成的 Red plan 自动失效，不得继续进入 Blue。

## Pressure Suite 与 Live Interview 必须分开

默认保留 `100` 问 `PRESSURE_SUITE`，它用于离线覆盖和 retrospective，不是一场 45–60 分钟面试的脚本。

Live Interview：

```text
LIVE_INTERVIEW_SEEDS: 6-10
DYNAMIC_FOLLOWUP: REQUIRED
ONE_QUESTION_ONE_INTENT: REQUIRED
PRESSURE_SUITE: 100
```

不预写固定 30 问 `PRIMARY_PATH`。Red 先准备少量自然 Seed，让候选人自己暴露技术主线；后续问题必须在上一答出现以后，从候选人刚说出的技术、数字、困难、选择、Ownership 或 bad case 中选择信息增益最高的 handle。

`KILL_SWITCH` 属于 Controller policy：当某个 Claim 连续无法建立 Ownership / mechanism，停止在该线程继续堆无效追问并自然换题。它不作为面试官口头话术出现。

一场面试可以深挖一个项目很久，也可以迅速换线程；不要求平均覆盖所有 Resume Claim。

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

Red 开始前从 Round branch HEAD 重新读取允许输入。`02_red_questions.md` 不能消费 Resume Builder 未提交的聊天中间信息。

Red 依照 `.agent/red-blue/attack-model.md` 建立 Interview Threads、Seed Questions、answer-driven Follow-up Policy 和 Pressure Suite。Claim 取证、Ownership、Build / Buy / Extend / Defer、实现、故障、Evidence、基础下钻和删除条件仍然重要，但它们是 interviewer mental map，不应被拼成每一道复合长问。

## USER_RED_REVIEW

Red 提交 `02_red_questions.md` 后，如果 `red_review_gate=REQUIRED`，Controller 进入用户审查状态。

用户结果：

```text
APPROVE
REQUEST_REVISION
ABORT
```

`REQUEST_REVISION` 时先提交用户反馈。Red Revision 可以读取原 Red allowlist、当前 Red plan 与 Red 质量反馈；仍不得读取 Zuno docs。

只有 `APPROVE` 后，manifest 才把 `red_questions_status` 改成 `FROZEN`，Blue 才能开始。

人工 Review 优先检查：Seed 是否自然；如果候选人按某种方式回答，下一问是否真的会跟着变；有没有把 rubric 写成问句；有没有无信息增益的原子化追问。

## Blue — Candidate / Documentation Reader

`02_red_questions.md` 已冻结后，Blue 从新的 GitHub HEAD 读取冻结简历、冻结 Red plan 和 manifest 固定 Zuno source refs / allowlist，再按 `zuno_base_sha` 读取允许的 canonical docs / Evidence。Blue 在生成 `03_blue_answers.md` 前不读取 Red Evaluation。

回答必须区分 History / Current / Target / Unknown / Personal Ownership / Team / Framework Capability。没有来源时明确说未证明。

## Red Evaluation

`03_blue_answers.md` 提交后，Red Evaluation 从 GitHub HEAD 读取冻结简历、实际提问 / 回答记录与 Attack Skill，不把 Zuno docs 作为正式评价输入。

它评价候选人是否像真正做过、是否能落到实现、Ownership 是否可信、替代方案 / 故障 / 基础是否经得住追问，以及简历 Claim 是否值得保留。

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

`WORKFLOW_RETROSPECTIVE` 读取全轮已提交 artifact、Red Skill 和 `07_user_feedback.md`，专门审判 Resume Builder、Red 与 Harness：模拟简历是否像真正求职材料，面试是不是 answer-driven，有没有机器式 checklist，是否无意义原子化，以及用户为什么认为它像或不像真实流程。

## Context Firewall

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

# Red / Blue Execution Protocol

本协议定义 Zuno Red / Blue 的机器执行规则。长期方法说明见 `docs/red-blue/README.md`。

## 目标

Red / Blue 模拟真实技术面试，而不是让 Red 直接审阅 Zuno 仓库。

每一轮先由 Resume Builder 根据当前 Zuno canonical docs、Current Evidence 和已有简历风格生成一份**本轮模拟简历**。模拟简历冻结以后，Red 的业务输入只允许来自模拟简历、目标岗位 / JD、`attack-model.md` 和模型通用知识；Red 不以 Zuno Project / Architecture / Modules / Evidence 作为出题依据。

Blue 才负责使用 Zuno 文档回答 Red 的问题。这样一轮同时验证两个问题：

1. 一名真实面试官只凭简历，会怎样攻击这个项目；
2. 当前 Zuno 文档是否足以支撑候选人回答这些攻击。

Round 本身不修改 Architecture、Resume、Red Skill 或实现。修复属于 Round 之后的独立任务。

## GitHub 是运行时状态总线，不是旁路日志

所有正式 Round 都是 **GitHub-mediated state machine**。

同一个 ChatGPT 对话、独立 Agent、人工 intervention 都不能通过“聊天里刚刚看过什么”直接完成阶段交接。阶段之间只通过 GitHub 上已经提交的 Round 状态和 artifact 交接：

```text
read branch HEAD
→ verify current stage + allowlist
→ read only declared stage inputs from that HEAD
→ produce one stage output
→ write artifact + manifest state + observable transcript
→ commit stage transaction
→ advance only after the commit exists
→ next stage re-read the new branch HEAD
```

GitHub commit 是阶段边界。未提交的草稿、聊天摘要、上一角色临时输出、Controller 私有笔记都不是下一阶段输入。

### Round branch / PR

正式 Round 启动时：

```text
main@<zuno_base_sha>
→ create red-blue/<round-id> branch
→ create docs/red-blue/workspace/<round-id>/
→ initialize 00_manifest.yaml + 08_session_transcript.md
→ set .agent/red-blue/current.md to active on the Round branch
→ open a Draft PR to main
```

Draft PR 是这一轮在 GitHub 上的可观察运行入口。Round 进行期间所有 stage commit 都进入同一 Round branch / PR。

关闭时先在 Round branch 完成最后一次状态转换：

```text
workspace/<round-id>/
→ rounds/<round-id>/
.agent/red-blue/current.md → no-active
PR draft → ready
required CI → pass
merge
→ reread exact main HEAD
```

因此 `main` 不需要保存半完成的 active workspace；活动过程由 Draft PR/branch 承载，关闭后只把完整归档合入 `main`。

### Stage transaction

每个阶段至少要更新三类内容：

1. 本阶段目标 artifact；
2. `00_manifest.yaml` 中的 stage state / input HEAD / completed flag；
3. `08_session_transcript.md` 中的 observable role I/O、Controller transition 和工具事件摘要。

如果用户在阶段之间给出会改变流程、问题质量判断或约束的反馈，还必须先更新：

```text
07_user_feedback.md
08_session_transcript.md
```

并提交后才能继续下一阶段。

不要求保存模型私有 chain-of-thought，也不得伪造它。需要保存的是**可观察输入、可观察输出、GitHub ref/commit、阶段转换和用户 intervention**。

## 一轮的固定生命周期

一轮就是一个完整文件夹，不在同一轮中继续生成第二批问题。默认 Red 一次生成 `100` 个高信息量问题，后续复测创建新的 Round。

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

每个箭头都是 GitHub commit barrier。禁止在 Round 结束时仅凭聊天摘要重建过程。

## 角色

### Controller / Resume Builder

Controller 负责：

- 固定 `zuno_base_sha`、Round branch、Draft PR、mode、岗位和 Round id；
- 从 GitHub 固定 ref 读取当前 Zuno canonical docs、Current Evidence 和既有简历风格；
- 根据**当前文档真正可以承担的成果**生成模拟简历；
- 严格区分“实现成果”“架构设计 / 复盘成果”“团队研究背景”和“个人 Ownership”；
- 把 Target 设计写成“参与设计 / 梳理 / 提出”，不能伪装成已实现；
- 提交并冻结 `01_simulated_resume.md`；
- 推进 manifest state，并维护 observable transcript。

Controller 不替 Red 出标准答案，也不替 Blue 美化回答。

### Red — Interviewer

Red 的业务输入 allowlist：

```text
01_simulated_resume.md
00_manifest.yaml 中的目标岗位 / JD / 面试轮次
.agent/red-blue/attack-model.md
模型通用知识
必要时由用户明确批准的通用生态事实
```

Red 的业务输入 denylist：

```text
docs/project/
docs/architecture/
docs/modules/
docs/evidence/
docs/decisions/
docs/governance/
Zuno 源码 / PR / commit diff
Blue source trace
历史 Round 的 Blue 标准答案
本轮模拟简历的生成笔记
```

Red 阶段开始前，Controller 必须从当前 Round branch HEAD 重新读取上述 allowlist。`02_red_questions.md` 不得直接消费 Resume Builder 在聊天中形成但未提交的中间信息。

Red 默认一次生成 100 个问题。问题应围绕简历最值得攻击的 3–6 条 Claim 形成若干连续深挖链，而不是 100 个随机八股。

### Blue — Candidate / Documentation Reader

Blue 从当前 Round branch HEAD 读取：

```text
01_simulated_resume.md
02_red_questions.md
00_manifest.yaml 中固定的 Zuno source refs / allowlist
```

再按 manifest 中固定的 Zuno base SHA 读取 canonical docs / Evidence。Blue 不读取尚未产生的 `04_red_evaluation.md` 或 workflow retrospective。

Blue 对问题逐题回答，并诚实区分：

```text
History
Current
Target
Unknown
Personal Ownership
Team / Advisor / Framework Capability
```

没有来源时可以明确回答“不知道 / 文档未证明”，不能用模型常识补 Zuno 项目事实。

### Red Evaluation — Interviewer Verdict

完成 Blue 回答并提交以后，Red Evaluation 从 GitHub HEAD 重新读取：

```text
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
.agent/red-blue/attack-model.md
```

它不读取 Zuno canonical docs。它评价的是：作为真实面试官，这个回答是否可信、具体、有技术深度，是否暴露新的追问空间，以及简历 Claim 是否经得住面试。

`04_red_evaluation.md` 至少记录：

- 每条高风险 Claim 的评价；
- 最危险的回答断点；
- 实现 / 架构 / Ownership / Evidence / 基础能力追问是否经得住；
- 哪些答案像背文档而不像真正做过；
- 30 秒 / 90 秒 / 3 分钟可讲性；
- 是否建议进入下一轮 retest。

Red Evaluation 不能因为不知道 Zuno docs 就宣布 Architecture Truth；它只表达 interviewer verdict。

### Blue Architecture Reflection

Blue Reflection 在 `04_red_evaluation.md` 已提交以后，从 GitHub HEAD 读取全部面试 artifact，并按固定 Zuno base SHA 重新读取 canonical docs / evidence。

它把断点路由到：

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

只有 Owner / Authority / State / Recovery / Security / Contract / Build-Buy 因果本身不成立时，才建议 Architecture Revision。面试官追到一个未恢复历史字段，不等于架构需要增加对象。

### Workflow Retrospective

`06_workflow_retrospective.md` 专门审查**红队和整个 Harness 本身**。

它从 GitHub HEAD 读取：

- 本轮所有已提交可观察产物；
- `attack-model.md`；
- `07_user_feedback.md`；
- 必要时明确选择的历史 workflow retrospective。

它必须回答：

- Red 的问题有没有技术含量；
- 是否真正从简历 Claim 出发；
- 是否做到精品问题而不是凑数；
- 是否存在大量语义重复；
- 是否覆盖完整工程链路；
- Build / Buy / Extend / Defer 是否真的被攻击；
- 是否能从项目自然下钻到网络、并发、数据库、Agent/RAG 等基础；
- 是否出现知道 Zuno 答案后反向出题的污染；
- 用户认为“问题太烂”的具体原因是什么；
- 下一轮应该怎样调整 Red Skill / question budget / persona。

Workflow Retrospective 可以提出修改 `attack-model.md` 或协议的建议，但 Round 内不自动修改它们。

## Context Firewall：两种模式的保证不同

### CHATGPT_AUTO

`CHATGPT_AUTO` 在同一个 ChatGPT 对话中运行。它必须遵守 GitHub stage transaction 与 commit-then-reread，但**同一对话无法提供真正的物理上下文遗忘**。如果 Resume Builder 在同一对话中读过 Zuno docs，模型底层上下文仍然可能保留这些信息。

所以 `CHATGPT_AUTO` 的保证必须诚实标记为：

```text
firewall_strength: LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

它适合：

- 快速验证模拟简历是否能产生有价值的攻击面；
- 检查 Red Skill 的问题质量；
- 验证 Blue 文档回答链路；
- 通过 GitHub 获得完整、可恢复、可审计的单对话过程。

它不能单独证明“Red 从未接触过 Zuno 文档”。如果某轮要把 **blind Red** 当作正式验收结论，必须用 `AGENT_AUTO` 重跑。

### AGENT_AUTO

`AGENT_AUTO` 使用独立 Resume Builder、Red、Blue、Red Evaluation、Blue Reflection、Workflow Retrospective context，并继续使用同一 GitHub stage state machine。

其目标保证为：

```text
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

Red context 只注入 GitHub 上 allowlist 文件，不注入 Zuno docs。独立 Agent 也不能跳过 GitHub transaction；物理隔离解决信息泄漏，GitHub state bus 解决过程可审计与恢复，两者承担不同责任。

## 模拟简历规则

模拟简历不是当前真实求职简历的自动覆盖，而是本轮的**攻击界面**。

生成时遵循：

1. 结构和措辞参考用户现有简历风格；
2. 只写当前 Zuno docs / Evidence 可以负责的事实或 Target 设计成果；
3. Target 架构成果必须用“参与设计 / 梳理 / 建立边界”等措辞；
4. 个人实现只写有 Personal Ownership 证据的内容；
5. 团队 / LIPLAB 研究写成背景或团队资产，不转成本人实现；
6. 不制造用户数、QPS、准确率、生产稳定性等未证明数字；
7. 简历应足够有吸引力，不能因为怕被问就退化成没有技术 Claim 的流水账。

## Red 问题质量门

默认 100 问，但每题都要通过以下门槛：

```text
Resume-grounded       是否明确攻击简历上的 Claim
Technical depth       是否要求机制 / 状态 / 算法 / 数据 / 接口
Decision value        回答不同是否会改变面试判断
Non-duplication       是否不是另一题的同义改写
Chain position        是否位于某条完整攻击链中
Interviewer realism   真实大厂面试官是否可能这样问
```

不满足至少四项的问题不应进入正式题单。

## 用户反馈

用户可以在任何阶段评价 Red / Blue / Workflow。

影响当前 Round 的 feedback 必须先写入 GitHub：

```text
07_user_feedback.md
08_session_transcript.md
```

并形成 commit，Controller 才能推进下一阶段。聊天中的用户评价如果没有进入这两个文件，只能算未归档输入，不能被后续 workflow retrospective 当作正式 Round Evidence。

用户关于“问题质量、技术含量、重复度、风格不像真实面试”的反馈拥有最高优先级。它可以触发 Round 之后独立的 Red Skill 修订，但不能在当前 Round 中先改 Skill 再宣布当前 Round 通过。

## 停止与复测

一轮完成固定阶段后关闭。需要继续追问时创建新的 Round，并重新生成新的模拟简历；如果架构或文档已经修改，新简历应反映新的可写成果。

这样每轮都能回答：

```text
这一版 Zuno 文档
→ 能生成怎样的简历 Claim
→ GitHub 冻结这份攻击界面
→ 面试官只看这些 Claim 会怎么问
→ GitHub 冻结问题
→ 文档能不能支撑回答
→ 面试官是否认可
→ 架构 / 文档真正需要改什么
→ 红队 Skill 本身还需要怎么进化
```

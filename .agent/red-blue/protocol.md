# Red / Blue Execution Protocol

本协议定义 Zuno Red / Blue 的机器执行规则。长期方法说明见 `docs/red-blue/README.md`。

## 目标

Red / Blue 模拟真实技术面试，而不是让 Red 直接审阅 Zuno 仓库。

每一轮先由 Controller 根据当前 Zuno canonical docs、Current Evidence 和已有简历风格生成一份**本轮模拟简历**。这份简历冻结以后，Red 只能看到模拟简历、目标岗位 / JD、`attack-model.md` 和通用模型知识；Red 不得读取 Zuno Project / Architecture / Modules / Evidence，也不得知道模拟简历背后的 source trace。

Blue 才负责使用 Zuno 文档回答 Red 的问题。这样才能验证两个不同问题：

1. 一名真实面试官只凭简历，会怎样攻击这个项目；
2. 当前 Zuno 文档是否足以支撑候选人回答这些攻击。

Round 本身不修改 Architecture、Resume 或实现。修复属于 Round 之后的独立任务。

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

每个阶段完成后立即写入 GitHub。禁止在 Round 结束时仅凭聊天摘要重建过程。

## 角色

### Controller / Resume Builder

Controller 是唯一允许在 Round 开始阶段同时读取 Zuno canonical docs、Current Evidence 和既有简历风格的角色。

它负责：

- 固定 Zuno base SHA、mode、岗位和 Round id；
- 根据**当前文档真正可以承担的成果**生成模拟简历；
- 严格区分“实现成果”“架构设计 / 复盘成果”“团队研究背景”和“个人 Ownership”；
- 把 Target 设计写成“参与设计 / 梳理 / 提出”，不能伪装成已实现；
- 冻结 `01_simulated_resume.md` 后关闭 Red 对项目文档的访问；
- 推进阶段和保存 observable transcript。

Controller 不替 Red 出标准答案，也不替 Blue 美化回答。

### Red — Interviewer

Red 模拟真实大厂面试官。

**允许输入只有：**

```text
01_simulated_resume.md
目标岗位 / JD / 面试轮次
.agent/red-blue/attack-model.md
模型通用知识
必要时由用户明确批准的通用生态事实
```

**禁止输入：**

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

Red 不知道“正确架构是什么”，只能像真实面试官一样从简历 Claim、技术常识、工程反例和 Red Skill 推导问题。

Red 默认一次生成 100 个问题。问题应围绕简历最值得攻击的 3–6 条 Claim 形成若干连续深挖链，而不是 100 个随机八股。

### Blue — Candidate / Documentation Reader

Blue 收到：

```text
01_simulated_resume.md
02_red_questions.md
Zuno canonical docs / evidence allowlist
```

Blue 不读取 Red 的内部质量评分或 workflow retrospective。Blue 对 100 个问题逐题回答，必须诚实区分：

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

完成 Blue 回答后，Red 再看到：

```text
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
attack-model.md
```

Red 仍然**不读取 Zuno docs**。它评价的是：作为真实面试官，这个回答是否可信、具体、有技术深度，是否暴露新的追问空间，以及简历 Claim 是否经得住面试。

`04_red_evaluation.md` 至少记录：

- 每条高风险 Claim 的评价；
- 最危险的回答断点；
- 实现 / 架构 / Ownership / Evidence / 基础能力追问是否经得住；
- 哪些答案像背文档而不像真正做过；
- 30 秒 / 90 秒 / 3 分钟可讲性；
- 是否建议进入下一轮 retest。

Red Evaluation 不能因为不知道 Zuno docs 就宣布 Architecture Truth；它只表达 interviewer verdict。

### Blue Architecture Reflection

Blue Reflection 读取：

```text
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
04_red_evaluation.md
Zuno canonical docs / evidence
```

它的任务不是继续辩赢 Red，而是把面试暴露的问题路由到正确责任面：

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

输入包括：

- 本轮所有可观察产物；
- `attack-model.md`；
- `07_user_feedback.md`；
- 必要时历史 Round 的 workflow retrospective。

它必须回答：

- Red 的问题有没有技术含量；
- 是否真正从简历 Claim 出发；
- 是否做到精品问题而不是凑数；
- 是否存在大量语义重复；
- 是否覆盖完整工程链路；
- Build / Buy / Extend / Defer 是否真的被攻击；
- 是否能从项目自然下钻到网络、并发、数据库、Agent/RAG 等基础；
- 是否出现知道 Zuno 答案后反向出题的泄漏；
- 用户认为“问题太烂”的具体原因是什么；
- 下一轮应该怎样调整 Red Skill / question budget / persona。

Workflow Retrospective 可以提出修改 `attack-model.md` 或协议的建议，但 Round 内不自动修改它们。

## Context Firewall

```text
RESUME BUILDER
  Zuno docs + Evidence + prior resume style
        │
        └── produces frozen 01_simulated_resume.md

RED
  frozen simulated resume
  + JD / role
  + Red Interview Skill
  + general model knowledge
  X no Zuno docs

BLUE
  frozen simulated resume
  + Red questions
  + Zuno canonical docs / Evidence
  X no Red evaluation before answering

RED EVALUATION
  resume + questions + Blue answers + Red Skill
  X no Zuno docs

BLUE REFLECTION
  all interview artifacts + Zuno docs

WORKFLOW RETROSPECTIVE
  all observable artifacts + user feedback + Red Skill
```

CHATGPT_AUTO 只能做到程序性隔离；AGENT_AUTO 应建立物理独立 context。两种模式使用同一 source policy 和同一 Round 文件结构。

## 两种正式模式

### CHATGPT_AUTO

在一个 ChatGPT 对话里按上述阶段切换角色。每个阶段完成后立即归档；`08_session_transcript.md` 保存用户 intervention、Controller transition 和可观察角色 I/O。

不得把前一角色不可见的信息继续带入后一角色的答案依据。尤其 Red 不得使用当前对话里已经读过的 Zuno docs 生成问题；Controller 必须按协议重新约束 Red context。

### AGENT_AUTO

Controller 为 Resume Builder、Red、Blue、Red Evaluation、Blue Reflection 和 Workflow Retrospective 建立独立上下文。Agent 的可观察输入输出和控制事件同样写入 `08_session_transcript.md`。

独立 Agent 不允许省略归档，也不允许只保存最终报告。

两种模式都不保存或伪造模型私有 chain-of-thought；保存的是可观察 I/O、显式元数据和工具 / 控制事件摘要。

## Round 工作目录与归档

Active Round：

```text
docs/red-blue/workspace/<round-id>/
```

一轮固定文件：

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

Round 关闭后，整个文件夹原样归档为：

```text
docs/red-blue/rounds/<round-id>/
```

不保留第二套改写后的“漂亮版”Round。历史问得差、答得差、用户批评都属于有价值的训练数据，应保留原样。

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

用户可以在任何阶段评价 Red / Blue / Workflow。所有评价写入 `07_user_feedback.md` 和 `08_session_transcript.md`。

Workflow Retrospective 对用户关于“问题质量、技术含量、重复度、风格不像真实面试”的反馈赋予最高优先级。用户反馈可以触发后续独立的 Red Skill 修订，但不能在当前 Round 中回写后再宣布当前 Round 通过。

## 停止与复测

一轮完成固定七个内容阶段后关闭。需要继续追问时创建新的 Round，并重新生成新的模拟简历；如果架构或文档已经修改，新简历应反映新的可写成果。

这样每轮都能回答：

```text
这一版 Zuno 文档
→ 能生成怎样的简历 Claim
→ 面试官只看这些 Claim 会怎么问
→ 文档能不能支撑回答
→ 面试官是否认可
→ 架构 / 文档真正需要改什么
→ 红队 Skill 本身还需要怎么进化
```

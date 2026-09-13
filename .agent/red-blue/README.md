# Zuno Red / Blue Runtime

`.agent/red-blue/` 是机器运行中心；长期方法、工作区和归档入口在 `docs/red-blue/`。

本目录只拥有 active Round state、执行协议、Red Interview Skill、评价规则和模板。它不拥有 Project History、Target Architecture、Module Truth、Current Evidence 或真实简历正文。

## GitHub-first 运行原则

正式 Round 中，GitHub 不是事后归档位置，而是阶段间唯一的耐久交接面。

```text
Round branch HEAD
→ read declared stage inputs
→ run one stage
→ write stage artifact + manifest + transcript
→ commit
→ next stage re-read new HEAD
```

聊天上下文、Agent 临时内存和未提交草稿不能直接跨 stage 成为输入。所有阶段都经过 `commit → re-read` barrier。

每轮启动独立 `red-blue/<round-id>` branch，并打开一个到 `main` 的 Draft PR。Round 运行过程持续写入这个 branch / PR；关闭时把 workspace 原样归档到 `docs/red-blue/rounds/<round-id>/`，通过 CI 后再合入 `main`。

## 正式模式

只允许：

```text
CHATGPT_AUTO
AGENT_AUTO
```

两种模式使用相同的 GitHub state machine、Round 阶段和文件结构，但隔离强度不同。

### CHATGPT_AUTO

一个 ChatGPT 对话中程序性切换：

```text
Resume Builder
→ Red
→ Blue
→ Red Evaluation
→ Blue Architecture Reflection
→ Workflow Retrospective
```

所有 handoff 都必须通过 GitHub commit。该模式只能声明：

```text
firewall_strength: LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

原因很直接：同一对话无法证明模型已经物理遗忘 Resume Builder 先前读取过的 Zuno docs。GitHub state bus 让过程可审计、可恢复，但不能制造不存在的物理上下文隔离。

### AGENT_AUTO

为 Resume Builder、Red、Blue、Red Evaluation、Blue Reflection、Workflow Retrospective 建立独立 context，同时继续使用完全相同的 GitHub stage transaction。

正式 blind Red 验收使用：

```text
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

独立 context 负责信息隔离；GitHub branch / PR 负责状态交接和全过程归档。

## 机器目录

```text
.agent/red-blue/
├── README.md
├── current.md
├── protocol.md
├── attack-model.md   # Red Interview Skill
├── judge.md          # Red Evaluation / Blue Reflection / workflow audit rules
└── templates/
    ├── round.md
    └── turn.md
```

## Source boundary

### Resume Builder

可读取：固定 Zuno base SHA 的 canonical docs / Evidence + 用户已有简历风格。输出先提交为 `01_simulated_resume.md`。

### Red

只把以下内容作为正式业务输入：

```text
01_simulated_resume.md
00_manifest.yaml 中的岗位 / JD / 轮次
attack-model.md
模型通用知识
```

Red 默认不能以 Project / Architecture / Modules / Evidence / Zuno source / prior Blue answer key 为出题依据。`02_red_questions.md` 必须从 Round branch HEAD 的 allowlist 重新读取后生成。

### Blue

在 `02_red_questions.md` 已提交后，从 GitHub HEAD 读取冻结简历、Red Questions 和 manifest 固定的 Zuno refs，再回答并提交 `03_blue_answers.md`。

### Red Evaluation

在 Blue Answers 已提交后，重新读取简历、问题、Blue 答案和 Red Skill；仍不读取 Zuno docs。

### Blue Reflection

读取已提交的完整面试产物和固定 Zuno docs，判断断点属于 Resume / Narrative / Docs / Architecture / Implementation / Evidence / Ownership / Fundamentals 中哪一类。

### Workflow Retrospective

读取全轮已提交 observable artifacts、Red Skill 和用户反馈，专门判断 Red 的问题质量与 Harness 设计。

## Active Workspace

Round branch 上的 Active Workspace 位于：

```text
docs/red-blue/workspace/<round-id>/
```

一轮固定产物：

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

用户 intervention 如果影响当前 Round，必须先提交到 `07_user_feedback.md` 和 `08_session_transcript.md`，再继续下一阶段。

Round 关闭前将整个文件夹原样归档到：

```text
docs/red-blue/rounds/<round-id>/
```

Round 不在同一文件夹继续第二批问题。修复后 retest 创建新 Round、新模拟简历。

## 运行边界

Round 不自动修改 Architecture、简历、Red Skill 或业务代码。Blue Reflection / Workflow Retrospective 只提出独立后续任务。

所有模式都保存可观察角色 I/O、GitHub ref / commit、Controller transition 和 user feedback；不保存或伪造模型私有 chain-of-thought。

完整方法见 `docs/red-blue/README.md`；执行状态机见 `protocol.md`。
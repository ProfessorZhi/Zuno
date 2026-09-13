# Zuno Red / Blue Runtime

`.agent/red-blue/` 是机器运行中心；长期方法、工作区和归档入口在 `docs/red-blue/`。

本目录只拥有 active Round state、执行协议、Red Interview Skill、评价规则和模板。它不拥有 Project History、Target Architecture、Module Truth、Current Evidence 或真实简历正文。

## 正式模式

只允许：

```text
CHATGPT_AUTO
AGENT_AUTO
```

两种模式使用完全相同的 Round 阶段和文件结构。

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

最重要的隔离规则是：**Resume Builder 可以读取 Zuno docs；模拟简历冻结后，Red 不再读取 Zuno docs。**

### AGENT_AUTO

为上述各阶段建立独立 context。主要优势是更强的输入隔离；归档要求与 CHATGPT_AUTO 相同。

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

可读取：Zuno canonical docs / Evidence + 用户已有简历风格。只负责产出本轮 `01_simulated_resume.md`。

### Red

只可读取：

```text
01_simulated_resume.md
岗位 / JD / 轮次
attack-model.md
模型通用知识
```

Red 默认不能读取 Project / Architecture / Modules / Evidence / Zuno source / prior Blue answer key。原始面经用于单独更新 Skill，不作为每轮默认 Red 输入。

### Blue

读取冻结模拟简历、Red Questions 和 manifest allowlist 内 Zuno canonical docs / Evidence。

### Red Evaluation

读取模拟简历、问题、Blue 答案和 Red Skill；仍然不能读取 Zuno docs。

### Blue Reflection

读取完整面试产物和 Zuno docs，判断面试断点真正属于 Resume / Narrative / Docs / Architecture / Implementation / Evidence / Ownership / Fundamentals 中哪一类。

### Workflow Retrospective

读取全轮 observable artifacts、Red Skill 和用户反馈，专门判断 Red 的问题质量与 Harness 设计。

## Active Workspace

Active Round 位于：

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

Round 关闭后整个文件夹原样归档到：

```text
docs/red-blue/rounds/<round-id>/
```

Round 不在同一文件夹继续第二批问题。修复后 retest 创建新 Round、新模拟简历。

## 运行边界

Round 不自动修改 Architecture、简历、Red Skill 或业务代码。Blue Reflection / Workflow Retrospective 只提出独立后续任务。

所有模式都保存可观察角色 I/O、Controller transition 和 user feedback；不保存或伪造模型私有 chain-of-thought。

完整方法见 `docs/red-blue/README.md`；执行状态机见 `protocol.md`。
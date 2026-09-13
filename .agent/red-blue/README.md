# Zuno Red / Blue Runtime

`.agent/red-blue/` 是机器运行中心；长期方法、行为证据、工作区和归档入口在 `docs/red-blue/`。

本目录只拥有 active Round state、执行协议、Red Interview Skill、评价规则和模板。它不拥有 Project History、Target Architecture、Module Truth、Current Evidence 或真实简历正文。

## GitHub-first

正式 Round 中，GitHub 是阶段间唯一耐久交接面：

```text
Round branch HEAD
→ read declared stage inputs
→ run one stage
→ write artifact + manifest + transcript
→ commit
→ next stage re-read new HEAD
```

聊天上下文、Agent 临时内存和未提交草稿不能直接跨 stage 成为正式输入。每轮使用独立 `red-blue/<round-id>` branch + Draft PR。

## 模式

只允许：

```text
CHATGPT_AUTO
AGENT_AUTO
```

`CHATGPT_AUTO` 使用同一 ChatGPT 对话并通过 GitHub handoff，只能声明：

```text
firewall_strength: LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

`AGENT_AUTO` 在 Red 等角色确实使用独立 context 时可以声明：

```text
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

## Source boundary

### Resume Builder

可读取固定 Zuno base SHA 的 canonical docs / Evidence + 已有简历风格，输出 `01_simulated_resume.md`。

### Red

正式业务输入只有：

```text
01_simulated_resume.md
00_manifest.yaml 中的岗位 / JD / 轮次
attack-model.md
模型通用知识
```

Red 默认不读取 Project / Architecture / Modules / Evidence / Zuno source / prior Blue answer key。

### Red 的输出

`02_red_questions.md` 现在是 **Interview Plan + Pressure Suite**：

```text
6–10 SPOKEN_SEEDS
DYNAMIC FOLLOWUP_POLICY
BRANCH_EXAMPLES
100-question PRESSURE_SUITE
```

Pressure Suite 用于离线覆盖，不是现场脚本。现场问答必须由上一答驱动：面试官听候选人刚说出的技术、数字、选择、困难、Ownership 或 bad case，选一个高信息增益 handle，再问一个主要意图。

Controller 可以维护 Claim risk、confidence、Kill Switch 等状态，但不把这些 rubric 念给候选人。

### USER_RED_REVIEW

校准 Round 默认在第一版 Red Interview Plan 提交后暂停。用户检查 Seed 是否自然、Branch 是否真的 answer-driven、问题是否仍像 Reviewer checklist。只有用户 `APPROVE` 并把 Red plan 冻结后 Blue 才能执行。

如果用户判定 Skill 本身有结构缺陷，可以把 Round `SUPERSEDED`，独立修 Skill，再开新 Round。

### Blue

读取冻结模拟简历、冻结 Red plan、实际 interview exchange 和 manifest 固定 Zuno refs，再从允许的 canonical docs 回答。

### Red Evaluation

依据实际发生的 question / answer threads 评价候选人，而不是要求 100 问逐题答完；仍不读取 Zuno docs。

### Blue Reflection

读取面试产物和固定 Zuno docs，判断断点属于 Resume / Narrative / Docs / Architecture / Implementation / Evidence / Ownership / Fundamentals 中哪一类。

### Workflow Retrospective

专门评价 Red 是否听回答、是否自然追问、是否及时换 thread、是否存在复合长问或无信息增益原子化，并结合用户反馈更新 Harness。

## 机器目录

```text
.agent/red-blue/
├── README.md
├── current.md
├── protocol.md
├── attack-model.md
├── judge.md
└── templates/
    ├── round.md
    └── turn.md
```

## Active Workspace

Round branch 的 workspace 位于 `docs/red-blue/workspace/<round-id>/`，固定九份 artifact：

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

影响当前 Round 的用户 intervention 先提交到 feedback / transcript，再推进状态。Round 关闭前整个 workspace 原样归档到 `docs/red-blue/rounds/<round-id>/`。

Round 不自动修改 Architecture、简历、Red Skill 或业务代码。Blue Reflection / Workflow Retrospective 只提出独立后续任务。

完整方法见 `docs/red-blue/README.md`；执行状态机见 `protocol.md`；公开面经提炼出的行为证据见 `docs/red-blue/interview-behavior-evidence-2026-09.md`。

# Zuno Red / Blue Runtime

`.agent/red-blue/` 是机器运行中心；长期方法、行为证据、工作区和归档入口在 `docs/red-blue/`。

本目录拥有 active Round state、执行协议、Red Interview Skill、Blue Candidate / Architecture Skill、评价规则和模板。它不拥有 Project History、Target Architecture、Module Truth、Current Evidence 或真实简历正文。

## GitHub-first

正式 Round 中，GitHub 是阶段之间唯一耐久交接面：

```text
Round branch HEAD
→ read declared inputs
→ run one stage
→ write artifact + manifest + transcript
→ commit
→ next actor re-read new HEAD
```

聊天上下文和未提交草稿不能直接跨阶段成为正式输入。

## 默认模式：BATCH_DUEL

自动架构校准默认使用两波 100 题：

```text
Frozen Resume
→ Red Wave 1：100 题
→ Blue Wave 1：100 答 + 封存架构初诊
→ Red Wave 2：先盲评 Blue 1，再给 100 个针对性追问
→ Blue Wave 2：100 答 + 封存架构复诊
→ Red Final Evaluation
→ Blue Final Architecture Reflection
→ Controller Workflow Retrospective
→ Improvement Ledger + Round Report
→ USER_IMPROVEMENT_REVIEW
→ approved architecture / docs / skill / implementation changes
→ Next Resume Candidate
→ next Round
```

每个 Batch Checkpoint 必须把对应 GitHub 文档的**直接可点击链接**交给用户。用户不用逐题扮演候选人。

`LIVE_INTERVIEW` 继续保留，但只有用户明确要求真人逐题模拟时才使用。

## Stable Artifact Links

[`docs/red-blue/workspace/artifact-links-contract.md`](../../docs/red-blue/workspace/artifact-links-contract.md) 是用户可见 handoff 的规范契约，模板见 [`artifact-links-template.md`](../../docs/red-blue/workspace/artifact-links-template.md)。

每个正式 Round Init 必须：

1. 创建 `00_artifact_links.md` 作为整轮稳定入口；
2. 预创建 Resume、Red、Blue、Final、Reflection、Retrospective、Ledger、Report、Next Resume 等正式 artifact；
3. 未开始的 artifact 只写 `status: NOT_STARTED` 等占位信息，不预生成未来内容；
4. 阶段执行时在原路径原地更新，保持 GitHub URL 稳定；
5. 每个 checkpoint 聊天回复至少发送 `00_artifact_links.md` 总入口 + 当前 artifact 直链。

禁止只告诉用户文件名、相对路径、commit SHA 或“已完成”。

稳定 URL 不改变 firewall。Red 即使知道 sealed Blue notes 的 URL，也不能把它们加入自己的读取 allowlist。

## 为什么把 Blue 分成两个面

Blue 同时扮演：

- Candidate：回答 Red；
- Architecture Reviewer：判断这些压力是否暴露系统缺陷。

两者必须物理分 artifact。

```text
Candidate answers
→ Red 可见

Architecture notes
→ Red 不可见
→ 只供最终 Blue Architecture Reflection 使用
```

否则 Red 2 会看到 canonical 架构答案，盲测就失效。

## Red 2 不是第二份题库

Red Wave 2 必须先对 Blue Wave 1 做 blind evaluation：

```text
什么已经可信
什么仍然薄弱
哪些 Ownership / Evidence / Failure 有问题
哪些第一波问题前提有误
哪些回答产生了新的攻击 handle
```

然后根据这些 observable handles 生成新的 **100 个问题**。不能把第一波问题机械换词。

## 两个闭环

### Interview / Pressure Loop

```text
Resume
→ Red 1
→ Blue 1
→ Red 2 evaluation + follow-ups
→ Blue 2
→ Red Final
```

### Engineering Improvement Loop

```text
Blue Final Architecture Reflection
→ Resume / Red Thinking / Blue Candidate / Blue Architecture / Harness Retrospective
→ Improvement Ledger
→ Round Report
→ User Improvement Gate
→ approved changes
→ Next Resume Candidate
```

当前架构只是 baseline。Multi-Agent、Subgraph、Generic Host、GraphRAG、Native Runtime 等都允许被采用、外置或删除。

## 角色边界

### Resume Builder

读取固定 base SHA 的 canonical docs / Evidence + 简历风格，生成真实可投递的 `01_simulated_resume.md`。

### Red

只读取 Frozen Resume、岗位 / JD、pinned `attack-model.md`，以及在 Wave 2 时读取 Blue 1 observable answers。Red 不读 Zuno docs / source / Evidence，也不读 Blue architecture notes。

### Blue Candidate

读取当前 Red 批次、此前 observable answers、pinned `defense-model.md` 和固定 base SHA 的允许 canonical sources，逐题回答。

### Blue Architecture Reviewer

每个 Blue Wave 回答完以后另外写封存 architecture notes。最终再对照 Red Final、canonical docs 和两次初诊做 `05_blue_architecture_reflection.md`。

### Controller

轮末必须审：

```text
Resume Builder
Red Thinking Framework
Blue Candidate Framework
Blue Architecture Framework
Harness
```

它负责发现模拟工作流本身是否有问题，而不是只审项目架构。

## Skill pinning

每轮开始时固定：

```text
attack-model.md version
defense-model.md version
judge.md version
protocol.md version
```

轮末允许改 Skill，但只能 `NEXT_ROUND_ONLY`，不能回头重算当前轮 verdict。

## 模式

`CHATGPT_AUTO`：`LOGICAL_GITHUB_MEDIATED`，不能证明物理 blind。

`AGENT_AUTO`：角色真正使用独立 context 时可声明 `PHYSICAL_CONTEXT_ISOLATION`。

## Machine files

```text
.agent/red-blue/
├── README.md
├── current.md
├── protocol.md
├── attack-model.md
├── defense-model.md
├── judge.md
└── templates/
    ├── round.md
    └── turn.md
```

## Core Round Artifacts

```text
00_manifest.yaml
00_artifact_links.md
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

BATCH_DUEL additional artifacts:

```text
03_blue_architecture_notes.md
04_red_wave2_review_and_questions.md
04_blue_wave2_answers.md
04_blue_wave2_architecture_notes.md
09_round_report.md
```

`10_next_resume_candidate.md` 是下一轮候选输入，不得覆盖本轮 Frozen Resume。下一轮从新 main HEAD 重新校验并再次经过 USER_RESUME_REVIEW。

完整状态机见 `protocol.md`，稳定链接契约见 `docs/red-blue/workspace/artifact-links-contract.md`，评价与归因规则见 `judge.md`。

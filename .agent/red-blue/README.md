# Zuno Red / Blue Runtime

`.agent/red-blue/` 是机器运行中心；长期方法、正式说明和归档入口在 `docs/red-blue/`。

本目录只拥有：active Round state、机器 protocol、attack model、verifier rules 和运行模板。它不拥有 Project History、Target Architecture、Module Truth、Current Evidence 或简历正文。

## 正式模式

只允许：

```text
CHATGPT_AUTO
AGENT_AUTO
```

用户中途参与属于 intervention，不是第三种 `human-candidate` 模式。

### CHATGPT_AUTO

一个 ChatGPT 对话中程序性切换 Red / Blue / Verifier 视角。适合快速发现 Narrative、Architecture、Evidence、Ownership、Build/Buy 和 Simplification Gap。

### AGENT_AUTO

使用独立 Red、Blue、Verifier context。适合正式 Closed-book 验收以及高严重度 Finding 的复测。

## 机器目录

```text
.agent/red-blue/
├── README.md
├── current.md
├── protocol.md
├── attack-model.md
├── judge.md          # verifier/audit rules; not a third debating role
└── templates/
    ├── round.md
    └── turn.md
```

## Source boundary

Red 可以读取精确简历、岗位/JD、攻击模型、批准的真实面经校准材料，以及 Build/Buy 问题所需的最新公开平台资料。

Blue 使用同一份简历快照，但只能读 manifest allowlist 内的 Zuno canonical docs；默认从 Project / Architecture / Module Part A 回答，追到精确 Contract / Recovery / Evidence 后再下钻 Part B / Part C / ADR / Evidence。

Verifier 只检查来源、事实层级、decision impact 和 Gap classification，不给 Blue 补答案。

## 运行边界

Round 不得自动修改 Architecture、简历或业务代码。输出只形成 Findings；正式变化通过独立任务进入对应 Owner。

新 Round 长期归档到：

```text
docs/red-blue/rounds/<round-id>/
```

旧手工/早期自动材料只在：

```text
docs/red-blue/archive/legacy/
```

完整方法见 `docs/red-blue/README.md`；执行状态机见 `protocol.md`。